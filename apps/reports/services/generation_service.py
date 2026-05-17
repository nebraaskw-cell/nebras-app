from django.db.models import Count, Q

from apps.accounts.models import User
from apps.attendance.models import AttendanceRecord
from apps.study_sessions.models import Session


def generate_circle_detail_report(circle):
    """
    Full detail report for a single circle.

    Returns a dict containing:
    - Circle metadata (teacher, governorate, capacity, etc.)
    - Active season/cycle info (if any)
    - Enrollment counts
    - Session counts by status
    - Attendance summary with percentages
    """
    from apps.seasons.models import SeasonCircle, Enrollment

    active_cycle = SeasonCircle.objects.filter(
        circle=circle,
        season__status="active",
    ).first()

    enrolled_count = (
        Enrollment.objects
        .filter(season_circle__circle=circle, status="active")
        .count()
        if active_cycle else 0
    )

    session_counts = Session.objects.filter(
        cycle__circle=circle,
    ).aggregate(
        total=Count("id"),
        scheduled=Count("id", filter=Q(status="scheduled")),
        active=Count("id", filter=Q(status="active")),
        completed=Count("id", filter=Q(status="completed")),
        cancelled=Count("id", filter=Q(status="cancelled")),
    )

    attendance_counts = AttendanceRecord.objects.filter(
        session__cycle__circle=circle,
    ).aggregate(
        total=Count("id"),
        present=Count("id", filter=Q(status="present")),
        absent=Count("id", filter=Q(status="absent")),
        late=Count("id", filter=Q(status="late")),
        excused=Count("id", filter=Q(status="excused")),
    )

    total_att = attendance_counts["total"] or 1
    attendance_rates = {
        "present_pct": round(attendance_counts["present"] / total_att * 100, 1),
        "absent_pct": round(attendance_counts["absent"] / total_att * 100, 1),
        "late_pct": round(attendance_counts["late"] / total_att * 100, 1),
        "excused_pct": round(attendance_counts["excused"] / total_att * 100, 1),
    }

    return {
        "circle": {
            "id": circle.pk,
            "name": circle.name,
            "name_ar": circle.name_ar,
            "governorate": circle.get_governorate_display(),
            "gender": circle.get_gender_display(),
            "teacher": str(circle.teacher) if circle.teacher else None,
            "capacity": active_cycle.capacity if active_cycle else 0,
            "is_active": circle.status == "open",
        },
        "active_cycle": {
            "id": active_cycle.pk,
            "title": active_cycle.season.title,
            "start_date": str(active_cycle.season.start_date),
            "end_date": str(active_cycle.season.end_date) if active_cycle.season.end_date else None,
        } if active_cycle else None,
        "enrollments": {
            "active": enrolled_count,
        },
        "sessions": session_counts,
        "attendance": {
            **attendance_counts,
            **attendance_rates,
        },
    }


def generate_student_performance_report(student):
    """
    Performance report for a single student across all seasons.

    Returns a dict containing:
    - Student metadata
    - Total seasons participated in
    - Per-season history with attendance breakdown and rate
    """
    from apps.seasons.models import Enrollment

    enrollments = (
        Enrollment.objects
        .filter(student=student)
        .select_related("season", "season_circle__circle")
        .order_by("-enrolled_at")
    )

    history = []
    for enrollment in enrollments:
        completed_sessions = Session.objects.filter(
            cycle=enrollment.season_circle,
            status="completed",
        ).count() if enrollment.season_circle else 0

        if enrollment.season_circle:
            attendance = AttendanceRecord.objects.filter(
                student=student,
                session__cycle=enrollment.season_circle,
            ).aggregate(
                total=Count("id"),
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
                late=Count("id", filter=Q(status="late")),
                excused=Count("id", filter=Q(status="excused")),
            )
        else:
            attendance = {
                "total": 0,
                "present": 0,
                "absent": 0,
                "late": 0,
                "excused": 0,
            }

        total = attendance["total"] or 1
        attendance_rate = round(attendance["present"] / total * 100, 1)

        history.append({
            "cycle": str(enrollment.season),
            "circle": enrollment.season_circle.circle.name_ar if enrollment.season_circle else "لم يتم اختيار الحلقة بعد",
            "enrollment_status": enrollment.get_status_display(),
            "enrolled_at": str(enrollment.enrolled_at.date()),
            "sessions_completed_in_cycle": completed_sessions,
            "attendance": {
                **attendance,
                "attendance_rate_pct": attendance_rate,
            },
        })

    return {
        "student": {
            "id": student.pk,
            "name": student.full_name,
            "governorate": (
                student.get_governorate_display()
                if student.governorate else None
            ),
            "gender": (
                student.get_gender_display()
                if student.gender else None
            ),
            "registration_status": student.get_registration_status_display()
                if hasattr(student, "get_registration_status_display") else student.registration_status,
        },
        "total_cycles": enrollments.count(),
        "history": history,
    }


def generate_registration_analytics_report(from_date, to_date):
    """
    Registration analytics for a given date range.

    Inputs:
    - from_date: date object (inclusive)
    - to_date: date object (inclusive)

    Returns a dict containing:
    - Total student registrations in the period
    - Breakdown by approval status
    - Breakdown by governorate
    - Breakdown by gender
    - Approval rate percentage
    """
    students = User.objects.filter(
        role=User.Roles.STUDENT,
        date_joined__date__gte=from_date,
        date_joined__date__lte=to_date,
    )

    total = students.count()

    by_status = students.aggregate(
        pending=Count("id", filter=Q(registration_status="pending")),
        approved=Count("id", filter=Q(registration_status="approved")),
        rejected=Count("id", filter=Q(registration_status="rejected")),
    )

    by_governorate = list(
        students
        .values("governorate")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    by_gender = list(
        students
        .values("gender")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    approval_rate = (
        round(by_status["approved"] / total * 100, 1)
        if total > 0 else 0
    )

    return {
        "period": {
            "from": str(from_date),
            "to": str(to_date),
        },
        "total_registrations": total,
        "by_status": by_status,
        "approval_rate_pct": approval_rate,
        "by_governorate": by_governorate,
        "by_gender": by_gender,
    }
