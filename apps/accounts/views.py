import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.models import AttendanceRecord
from apps.circles.models import Circle, Enrollment
from apps.core.permissions import IsAdminOrTeacher, IsAdminRole, IsParentRole
from apps.gamification.models import EarnedBadge
from apps.gamification.services.gamification_service import get_total_points
from apps.study_sessions.models import Session

from .forms import StudentRegistrationForm
from .models import ParentProfile, User
from .serializers import (
    ParentProfileRequestSerializer,
    ParentProfileSerializer,
    StudentRegistrationSerializer,
    UserSerializer,
)
from .services import parent_service, registration_service

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["role"] = user.role
        context["registration_status"] = user.registration_status

        if user.role == User.Roles.ADMIN:
            context["pending_students"] = User.objects.filter(
                role=User.Roles.STUDENT,
                registration_status=User.RegistrationStatus.PENDING,
            ).order_by("-date_joined")
            context["pending_parents"] = ParentProfile.objects.filter(
                status=ParentProfile.Status.PENDING
            ).order_by("-requested_at")
            context["active_circles_count"] = Circle.objects.filter(is_active=True).count()
            context["active_enrollments_count"] = Enrollment.objects.filter(
                status="active"
            ).count()

        elif user.role == User.Roles.TEACHER:
            context["my_circles"] = Circle.objects.filter(teacher=user, is_active=True)
            context["upcoming_sessions"] = Session.objects.filter(
                cycle__circle__teacher=user, status="scheduled"
            ).order_by("date", "start_time")[:5]
            context["active_sessions"] = Session.objects.filter(
                cycle__circle__teacher=user, status="active"
            ).order_by("date", "start_time")
            context["pending_parents"] = (
                ParentProfile.objects.filter(
                    status=ParentProfile.Status.PENDING,
                    student__enrollments__cycle__circle__teacher=user,
                    student__enrollments__status="active",
                )
                .distinct()
                .order_by("-requested_at")
            )

        elif user.role == User.Roles.STUDENT:
            enrollment = (
                Enrollment.objects.filter(student=user, status="active")
                .select_related("cycle__circle")
                .first()
            )
            context["my_enrollment"] = enrollment
            if enrollment:
                attendance = AttendanceRecord.objects.filter(student=user).aggregate(
                    present=Count("id", filter=Q(status="present")),
                    absent=Count("id", filter=Q(status="absent")),
                )
                context["attendance_present"] = attendance["present"]
                context["attendance_absent"] = attendance["absent"]

            context["total_points"] = get_total_points(user)
            context["badges"] = EarnedBadge.objects.filter(student=user).select_related("badge")

        elif user.role == User.Roles.PARENT:
            parent_profiles = (
                ParentProfile.objects.filter(parent=user)
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

            approved_profiles = parent_profiles.filter(status=ParentProfile.Status.APPROVED)

            # Collect all student IDs from approved profiles in one pass
            student_ids = [p.student_id for p in approved_profiles]

            # Fetch all attendance counts in a single aggregated query
            attendance_qs = (
                AttendanceRecord.objects.filter(student_id__in=student_ids)
                .values("student_id")
                .annotate(
                    present=Count("id", filter=Q(status="present")),
                    absent=Count("id", filter=Q(status="absent")),
                )
            )
            attendance_map = {row["student_id"]: row for row in attendance_qs}

            # Fetch all active enrollments in a single query
            enrollment_map = {
                e.student_id: e
                for e in Enrollment.objects.filter(
                    student_id__in=student_ids, status="active"
                ).select_related("cycle__circle__teacher")
            }

            # Fetch all earned badges in a single query
            badges_map: dict[int, list] = {sid: [] for sid in student_ids}
            for badge in EarnedBadge.objects.filter(
                student_id__in=student_ids
            ).select_related("badge"):
                badges_map[badge.student_id].append(badge)

            # Build linked_students with no further DB queries
            linked_students = []
            for profile in approved_profiles:
                sid = profile.student_id
                att = attendance_map.get(sid, {})
                linked_students.append(
                    {
                        "profile": profile,
                        "student": profile.student,
                        "enrollment": enrollment_map.get(sid),
                        "attendance_present": att.get("present", 0),
                        "attendance_absent": att.get("absent", 0),
                        "total_points": get_total_points(profile.student),
                        "badges": badges_map.get(sid, []),
                    }
                )

            context["linked_students"] = linked_students

        return context


class StudentRegistrationView(CreateView):
    form_class = StudentRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:student-register-complete")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Registration submitted. Your account is pending approval.",
        )
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
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return registration_service.get_pending_students()


class ApproveStudentAPIView(APIView):
    permission_classes = [IsAdminOrTeacher]

    def post(self, request, pk):
        student = generics.get_object_or_404(
            User,
            pk=pk,
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.PENDING,
        )
        registration_service.approve_student_registration(student, approved_by=request.user)
        return Response(UserSerializer(student).data, status=status.HTTP_200_OK)


class RejectStudentAPIView(APIView):
    permission_classes = [IsAdminOrTeacher]

    def post(self, request, pk):
        student = generics.get_object_or_404(
            User,
            pk=pk,
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.PENDING,
        )
        try:
            registration_service.reject_user(student, rejected_by=request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserSerializer(student).data, status=status.HTTP_200_OK)


class ParentLinkRequestAPIView(generics.CreateAPIView):
    """Parent requests to link to a student."""

    serializer_class = ParentProfileRequestSerializer
    permission_classes = [IsParentRole]


class PendingParentLinkListAPIView(generics.ListAPIView):
    """Admin/Teacher views pending parent link requests."""

    serializer_class = ParentProfileSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return ParentProfile.objects.filter(status=ParentProfile.Status.PENDING)


class ApproveParentLinkAPIView(APIView):
    """Admin/Teacher approves a parent link request."""

    permission_classes = [IsAdminOrTeacher]

    def post(self, request, pk):
        link_request = generics.get_object_or_404(
            ParentProfile,
            pk=pk,
            status=ParentProfile.Status.PENDING,
        )
        try:
            link_request = parent_service.approve_parent_linking(
                profile=link_request,
                approved_by=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ParentProfileSerializer(link_request).data, status=status.HTTP_200_OK)


class RejectParentLinkAPIView(APIView):
    """Admin/Teacher rejects a parent link request."""

    permission_classes = [IsAdminOrTeacher]

    def post(self, request, pk):
        link_request = generics.get_object_or_404(
            ParentProfile,
            pk=pk,
            status=ParentProfile.Status.PENDING,
        )
        try:
            link_request = parent_service.reject_parent_linking(
                profile=link_request,
                rejected_by=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ParentProfileSerializer(link_request).data, status=status.HTTP_200_OK)