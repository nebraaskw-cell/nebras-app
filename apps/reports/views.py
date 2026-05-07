from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrTeacherRole, IsAdminRole, IsParentRole
from apps.circles.models import Circle
from apps.accounts.models import User, ParentProfile
from .services import generation_service


class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "reports/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == User.Roles.ADMIN:
            context["circles"] = Circle.objects.filter(is_active=True)
            context["students"] = User.objects.filter(role=User.Roles.STUDENT)
        elif user.role == User.Roles.TEACHER:
            context["circles"] = Circle.objects.filter(teacher=user, is_active=True)
            context["students"] = User.objects.filter(
                role=User.Roles.STUDENT,
                enrollments__cycle__circle__teacher=user,
                enrollments__status="active"
            ).distinct()
        elif user.role == User.Roles.PARENT:
            parent_profile = ParentProfile.objects.filter(parent=user, status=ParentProfile.Status.APPROVED).first()
            if parent_profile:
                context["student"] = parent_profile.student
                
        return context


class CircleReportAPIView(APIView):
    permission_classes = [IsAdminOrTeacherRole]

    def get(self, request, pk):
        circle = generics.get_object_or_404(Circle, pk=pk)
        if request.user.role == User.Roles.TEACHER and circle.teacher != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        data = generation_service.generate_circle_detail_report(circle)
        return Response(data)


class StudentPerformanceAPIView(APIView):
    def get_permissions(self):
        # We'll check object-level logic in get() for parents
        return [permissions.IsAuthenticated()]

    def get(self, request, pk):
        student = generics.get_object_or_404(User, pk=pk, role=User.Roles.STUDENT)
        
        # Check permissions: Admin, Teacher (if student in their circle), or Parent (if linked)
        can_view = False
        if request.user.is_admin_role:
            can_view = True
        elif request.user.is_teacher_role:
            if student.enrollments.filter(cycle__circle__teacher=request.user, status="active").exists():
                can_view = True
        elif request.user.role == User.Roles.PARENT:
            if ParentProfile.objects.filter(parent=request.user, student=student, status=ParentProfile.Status.APPROVED).exists():
                can_view = True
        
        if not can_view:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        data = generation_service.generate_student_performance_report(student)
        return Response(data)


class RegistrationAnalyticsAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        from datetime import date, timedelta
        
        from_date_str = request.query_params.get('from', (date.today() - timedelta(days=30)).isoformat())
        to_date_str = request.query_params.get('to', date.today().isoformat())
        
        try:
            from_date = date.fromisoformat(from_date_str)
            to_date = date.fromisoformat(to_date_str)
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            
        data = generation_service.generate_registration_analytics_report(from_date, to_date)
        return Response(data)
