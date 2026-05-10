from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrTeacherRole, IsAdminRole, IsParentRole

from .forms import StudentRegistrationForm
from .models import User, ParentProfile
from .serializers import (
    StudentRegistrationSerializer,
    UserSerializer,
    ParentProfileSerializer,
    ParentProfileRequestSerializer,
)
from .services import registration_service
from .services import parent_service


from apps.circles.models import Circle, Enrollment
from apps.study_sessions.models import Session
from apps.attendance.models import AttendanceRecord

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["role"] = user.role
        context["registration_status"] = user.registration_status

        if user.role == User.Roles.ADMIN:
            context["pending_students"] = User.objects.filter(
                role=User.Roles.STUDENT, registration_status=User.RegistrationStatus.PENDING
            ).order_by("-date_joined")
            context["pending_parents"] = ParentProfile.objects.filter(status=ParentProfile.Status.PENDING).order_by("-requested_at")
            context["active_circles_count"] = Circle.objects.filter(is_active=True).count()
            context["active_enrollments_count"] = Enrollment.objects.filter(status="active").count()

        elif user.role == User.Roles.TEACHER:
            context["my_circles"] = Circle.objects.filter(teacher=user, is_active=True)
            context["upcoming_sessions"] = Session.objects.filter(
                cycle__circle__teacher=user, status="scheduled"
            ).order_by("date", "start_time")[:5]
            context["active_sessions"] = Session.objects.filter(
                cycle__circle__teacher=user, status="active"
            ).order_by("date", "start_time")
            context["pending_parents"] = ParentProfile.objects.filter(
                status=ParentProfile.Status.PENDING,
                student__enrollments__cycle__circle__teacher=user,
                student__enrollments__status="active"
            ).distinct().order_by("-requested_at")

        elif user.role == User.Roles.STUDENT:
            enrollment = Enrollment.objects.filter(student=user, status="active").select_related("cycle__circle").first()
            context["my_enrollment"] = enrollment
            if enrollment:
                records = AttendanceRecord.objects.filter(student=user)
                context["attendance_present"] = records.filter(status="present").count()
                context["attendance_absent"] = records.filter(status="absent").count()

            # Phase 4 Gamification
            from apps.gamification.services.gamification_service import get_total_points
            from apps.gamification.models import EarnedBadge
            context["total_points"] = get_total_points(user)
            context["badges"] = EarnedBadge.objects.filter(student=user).select_related('badge')

        elif user.role == User.Roles.PARENT:
            parent_profiles = (
                ParentProfile.objects
                .filter(parent=user)
                .select_related("student")
                .order_by("-requested_at")
            )
            active_link_count = parent_profiles.filter(
                status__in=[
                    ParentProfile.Status.PENDING,
                    ParentProfile.Status.APPROVED,
                ]
            ).count()
            context["parent_profiles"] = parent_profiles
            context["parent_profile"] = parent_profiles.first()
            context["can_request_parent_link"] = active_link_count < 3

            approved_profiles = parent_profiles.filter(
                status=ParentProfile.Status.APPROVED
            )
            linked_students = []

            from apps.gamification.services.gamification_service import get_total_points
            from apps.gamification.models import EarnedBadge

            for profile in approved_profiles:
                student = profile.student
                enrollment = (
                    Enrollment.objects
                    .filter(student=student, status="active")
                    .select_related("cycle__circle__teacher")
                    .first()
                )
                records = AttendanceRecord.objects.filter(student=student)
                linked_students.append({
                    "profile": profile,
                    "student": student,
                    "enrollment": enrollment,
                    "attendance_present": records.filter(status="present").count(),
                    "attendance_absent": records.filter(status="absent").count(),
                    "total_points": get_total_points(student),
                    "badges": EarnedBadge.objects.filter(student=student).select_related("badge"),
                })

            context["linked_students"] = linked_students

        return context


class StudentRegistrationView(CreateView):
    form_class = StudentRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:student-register-complete")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Registration submitted. Your account is pending approval.")
        return response


class StudentRegistrationCompleteView(TemplateView):
    template_name = "accounts/register_complete.html"


class MeAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class StudentRegistrationAPIView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class PendingStudentListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrTeacherRole]

    def get_queryset(self):
        return registration_service.get_pending_students()


class ApproveStudentAPIView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        student = generics.get_object_or_404(
            User,
            pk=pk,
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.PENDING,
        )
        registration_service.approve_student_registration(student, approved_by=request.user)
        return Response(UserSerializer(student).data, status=status.HTTP_200_OK)


class ParentLinkRequestAPIView(generics.CreateAPIView):
    """Parent requests to link to a student."""
    serializer_class = ParentProfileRequestSerializer
    permission_classes = [IsParentRole]


class PendingParentLinkListAPIView(generics.ListAPIView):
    """Admin/Teacher views pending parent link requests."""
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAdminOrTeacherRole]

    def get_queryset(self):
        return ParentProfile.objects.filter(status=ParentProfile.Status.PENDING)


class ApproveParentLinkAPIView(APIView):
    """Admin/Teacher approves a parent link request."""
    permission_classes = [IsAdminOrTeacherRole]

    def post(self, request, pk):
        link_request = generics.get_object_or_404(
            ParentProfile,
            pk=pk,
            status=ParentProfile.Status.PENDING
        )
        try:
            link_request = parent_service.approve_parent_linking(
                profile=link_request,
                approved_by=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ParentProfileSerializer(link_request).data, status=status.HTTP_200_OK)

