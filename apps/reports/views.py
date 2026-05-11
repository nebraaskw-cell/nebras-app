from datetime import date, timedelta
from html import escape

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrTeacher, IsAdminRole, IsParentRole
from apps.circles.models import Circle
from apps.accounts.models import User, ParentProfile
from .services import generation_service


def _parse_date_range(request):
    from_date_str = request.query_params.get(
        "from",
        (date.today() - timedelta(days=30)).isoformat(),
    )
    to_date_str = request.query_params.get("to", date.today().isoformat())

    try:
        return date.fromisoformat(from_date_str), date.fromisoformat(to_date_str), None
    except ValueError:
        return None, None, "Invalid date format. Use YYYY-MM-DD."


def _excel_response(filename, title, rows):
    """
    Return a lightweight Excel-compatible .xls response.

    This avoids adding a spreadsheet dependency while still allowing Excel
    to open the exported Arabic report data cleanly.
    """
    table_rows = "\n".join(
        "<tr>"
        + "".join(f"<td>{escape(str(cell or ''))}</td>" for cell in row)
        + "</tr>"
        for row in rows
    )
    html = f"""﻿<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; direction: rtl; }}
        table {{ border-collapse: collapse; width: 100%; }}
        td {{ border: 1px solid #999; padding: 8px; }}
        .heading td {{ background: #144a52; color: #fff; font-weight: bold; }}
    </style>
</head>
<body>
    <h2>{escape(title)}</h2>
    <table>{table_rows}</table>
</body>
</html>"""
    response = HttpResponse(html, content_type="application/vnd.ms-excel; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


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
            parent_profiles = ParentProfile.objects.filter(
                parent=user,
                status=ParentProfile.Status.APPROVED,
            ).select_related("student")
            context["parent_students"] = [profile.student for profile in parent_profiles]
            if parent_profiles:
                context["student"] = parent_profiles[0].student
                
        return context


class CircleReportAPIView(APIView):
    permission_classes = [IsAdminOrTeacher]

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
        from_date, to_date, error = _parse_date_range(request)
        if error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)
            
        data = generation_service.generate_registration_analytics_report(from_date, to_date)
        return Response(data)


class CircleReportExcelAPIView(APIView):
    permission_classes = [IsAdminOrTeacher]

    def get(self, request, pk):
        circle = generics.get_object_or_404(Circle, pk=pk)
        if request.user.role == User.Roles.TEACHER and circle.teacher != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        data = generation_service.generate_circle_detail_report(circle)
        rows = [
            ["التقرير", "تقرير الحلقة"],
            ["اسم الحلقة", data["circle"]["name_ar"]],
            ["المعلم", data["circle"]["teacher"] or "غير محدد"],
            ["المحافظة", data["circle"]["governorate"]],
            ["المسجد", data["circle"]["mosque"]],
            ["الطاقة الاستيعابية", data["circle"]["capacity"]],
            ["التسجيلات النشطة", data["enrollments"]["active"]],
            ["إجمالي الجلسات", data["sessions"]["total"]],
            ["الجلسات المكتملة", data["sessions"]["completed"]],
            ["نسبة الحضور", f"{data['attendance']['present_pct']}%"],
            ["نسبة الغياب", f"{data['attendance']['absent_pct']}%"],
        ]
        return _excel_response(
            filename=f"circle-report-{circle.pk}.xls",
            title=f"تقرير حلقة {circle.name_ar}",
            rows=rows,
        )


class StudentPerformanceExcelAPIView(APIView):
    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get(self, request, pk):
        student = generics.get_object_or_404(User, pk=pk, role=User.Roles.STUDENT)

        can_view = False
        if request.user.is_admin_role:
            can_view = True
        elif request.user.is_teacher_role:
            can_view = student.enrollments.filter(
                cycle__circle__teacher=request.user,
                status="active",
            ).exists()
        elif request.user.role == User.Roles.PARENT:
            can_view = ParentProfile.objects.filter(
                parent=request.user,
                student=student,
                status=ParentProfile.Status.APPROVED,
            ).exists()

        if not can_view:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        data = generation_service.generate_student_performance_report(student)
        rows = [
            ["التقرير", "تقرير أداء الطالب"],
            ["الطالب", data["student"]["name"]],
            ["المحافظة", data["student"]["governorate"] or ""],
            ["الحالة", data["student"]["registration_status"]],
            ["عدد الدورات", data["total_cycles"]],
            [],
            ["الحلقة", "الدورة", "حالة التسجيل", "الحضور", "نسبة الحضور"],
        ]
        for item in data["history"]:
            attendance = item["attendance"]
            rows.append([
                item["circle"],
                item["cycle"],
                item["enrollment_status"],
                f"{attendance['present']} / {attendance['total']}",
                f"{attendance['attendance_rate_pct']}%",
            ])

        return _excel_response(
            filename=f"student-report-{student.pk}.xls",
            title=f"تقرير الطالب {student.full_name}",
            rows=rows,
        )


class RegistrationAnalyticsExcelAPIView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        from_date, to_date, error = _parse_date_range(request)
        if error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        data = generation_service.generate_registration_analytics_report(from_date, to_date)
        rows = [
            ["التقرير", "إحصائيات التسجيل"],
            ["من", data["period"]["from"]],
            ["إلى", data["period"]["to"]],
            ["إجمالي المسجلين", data["total_registrations"]],
            ["قيد المراجعة", data["by_status"]["pending"]],
            ["تم قبولهم", data["by_status"]["approved"]],
            ["مرفوض", data["by_status"]["rejected"]],
            ["نسبة القبول", f"{data['approval_rate_pct']}%"],
            [],
            ["المحافظة", "العدد"],
        ]
        for item in data["by_governorate"]:
            rows.append([item["governorate"] or "غير محدد", item["count"]])

        rows.extend([[], ["الجنس", "العدد"]])
        for item in data["by_gender"]:
            rows.append([item["gender"] or "غير محدد", item["count"]])

        return _excel_response(
            filename="registration-analytics.xls",
            title="إحصائيات التسجيل",
            rows=rows,
        )
