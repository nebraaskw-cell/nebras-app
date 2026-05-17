from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.seasons.models import Season, SeasonCircle, Enrollment, SeasonSnapshot
from apps.study_sessions.models import Session
from apps.attendance.models import AttendanceRecord
from apps.ai_evaluation.models import Evaluation


def archive_season(season: Season, user):
    """
    Orchestrates the archiving of a season.
    Transitions CLOSED -> ARCHIVED and generates a comprehensive data snapshot.
    """
    if season.status == Season.Status.ARCHIVED:
        return season

    # Check that only closed seasons can be archived (or active if closing directly)
    if season.status not in [Season.Status.CLOSED, Season.Status.ACTIVE]:
        raise ValidationError(
            "لا يمكن أرشفة الموسم إلا إذا كان مغلقاً أو نشطاً."
        )

    with transaction.atomic():
        # 1. Update season status and timing
        season.status = Season.Status.ARCHIVED
        season.archived_at = timezone.now()
        season.save()

        # 2. Complete all active enrollments in the season
        active_enrollments = Enrollment.objects.filter(
            season=season,
            status=Enrollment.Status.ACTIVE,
        )
        for enrollment in active_enrollments:
            enrollment.status = Enrollment.Status.COMPLETED
            enrollment.save(update_fields=["status", "updated_at"])

        # 3. Generate Snapshot Data
        snapshot_data = generate_season_snapshot_data(season)

        # 4. Save to SeasonSnapshot
        SeasonSnapshot.objects.update_or_create(
            season=season,
            defaults={"data": snapshot_data},
        )

    return season


def generate_season_snapshot_data(season: Season):
    """
    Builds the complete JSON-serializable snapshot of the season data.
    """
    season_circles = SeasonCircle.objects.filter(season=season).select_related("circle", "supervisor")
    enrollments = Enrollment.objects.filter(season=season).select_related("student", "season_circle")
    sessions = Session.objects.filter(cycle__season=season).select_related("cycle__circle")

    total_students = enrollments.count()
    total_circles = season_circles.count()
    total_sessions = sessions.count()

    circles_data = []

    for sc in season_circles:
        circle = sc.circle
        teacher = sc.supervisor

        # Students in this circle for this season
        sc_enrollments = enrollments.filter(season_circle=sc)
        students_list = []
        student_ids = []
        for e in sc_enrollments:
            student = e.student
            student_ids.append(student.id)
            students_list.append({
                "student_id": student.id,
                "username": student.username,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "full_name": student.full_name,
                "gender": student.gender,
                "governorate": student.governorate,
                "enrollment_status": e.get_status_display(),
            })

        # Sessions for this circle in this season
        sc_sessions = sessions.filter(cycle=sc)
        sessions_list = []
        for s in sc_sessions:
            # Calculate attendance rate for this session
            att_records = AttendanceRecord.objects.filter(session=s)
            tot_att = att_records.count()
            pres_att = att_records.filter(status=AttendanceRecord.Status.PRESENT).count()
            late_att = att_records.filter(status=AttendanceRecord.Status.LATE).count()
            rate = round(((pres_att + late_att) / tot_att * 100), 1) if tot_att > 0 else 0.0

            sessions_list.append({
                "session_id": s.id,
                "title": s.title,
                "date": str(s.date),
                "status": s.get_status_display(),
                "attendance_rate_pct": rate,
            })

        # Attendance records for students of this circle in this season's sessions
        attendance_list = []
        sc_att_records = AttendanceRecord.objects.filter(
            session__in=sc_sessions,
            student_id__in=student_ids
        ).select_related("student", "session")

        for att in sc_att_records:
            attendance_list.append({
                "student_username": att.student.username,
                "session_title": att.session.title,
                "session_date": str(att.session.date),
                "status": att.get_status_display(),
                "marked_at": str(att.marked_at) if att.marked_at else None,
            })

        # Evaluation results for students of this circle in this season's sessions
        evaluations_list = []
        sc_evals = Evaluation.objects.filter(
            session__in=sc_sessions,
            student_id__in=student_ids
        ).select_related("student", "session")

        for ev in sc_evals:
            evaluations_list.append({
                "student_username": ev.student.username,
                "session_title": ev.session.title,
                "session_date": str(ev.session.date),
                "type": ev.get_evaluation_type_display(),
                "score": ev.score,
                "feedback": ev.feedback,
            })

        # Calculate overall circle attendance rate
        total_att = len(attendance_list)
        pres_late = sum(1 for a in attendance_list if a["status"] in ["Present", "Late"])
        overall_attendance_rate = round((pres_late / total_att * 100), 1) if total_att > 0 else 100.0

        circles_data.append({
            "circle_id": circle.id,
            "name": circle.name,
            "name_ar": circle.name_ar,
            "teacher": teacher.full_name if teacher else "No Teacher",
            "capacity": sc.capacity,
            "student_count": len(students_list),
            "students": students_list,
            "sessions": sessions_list,
            "overall_attendance_rate_pct": overall_attendance_rate,
            "attendance_records": attendance_list,
            "evaluations": evaluations_list,
        })

    return {
        "season_id": season.id,
        "title": season.title,
        "start_date": str(season.start_date),
        "end_date": str(season.end_date) if season.end_date else None,
        "archived_at": str(season.archived_at) if season.archived_at else None,
        "total_students": total_students,
        "total_circles": total_circles,
        "total_sessions": total_sessions,
        "circles": circles_data,
    }
