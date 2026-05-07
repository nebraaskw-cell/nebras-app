from apps.attendance.models import AttendanceRecord
from apps.circles.models import Enrollment
from apps.study_sessions.models import Session


def _validate_session_is_active(session):
    """
    Attendance can only be marked when the session is ACTIVE.
    Raises ValueError otherwise.
    """
    if session.status != Session.Status.ACTIVE:
        raise ValueError(
            f"Attendance can only be marked for an ACTIVE session. "
            f"Current session status: '{session.status}'."
        )


def _validate_teacher_owns_session(session, marked_by):
    """
    Only the teacher assigned to the session's circle can mark attendance.
    Admins are also permitted.
    Raises ValueError otherwise.
    """
    if getattr(marked_by, "is_admin_role", False):
        return  # Admins can always mark attendance

    circle_teacher = getattr(session.cycle.circle, "teacher", None)

    if circle_teacher is None:
        raise ValueError(
            "This circle has no assigned teacher. "
            "Contact an admin to assign a teacher before marking attendance."
        )

    if circle_teacher.pk != marked_by.pk:
        raise ValueError(
            "You are not the assigned teacher for this circle "
            "and cannot mark attendance for this session."
        )


def _validate_student_enrolled(session, student):
    """
    The student must have an ACTIVE enrollment in the session's cycle.
    Raises ValueError otherwise.
    """
    is_enrolled = Enrollment.objects.filter(
        student=student,
        cycle=session.cycle,
        status=Enrollment.Status.ACTIVE,
    ).exists()

    if not is_enrolled:
        raise ValueError(
            f"Student '{student}' does not have an active enrollment "
            f"in cycle '{session.cycle}'. "
            "Cannot mark attendance for a non-enrolled student."
        )


def mark_attendance(session, student, status, marked_by):
    """
    Marks or updates attendance for a single student in a session.

    Validations (all raise ValueError on failure):
    - session must be ACTIVE
    - marked_by must be the circle's teacher or an admin
    - student must have an ACTIVE enrollment in the session's cycle
    - status must be a valid AttendanceRecord.Status value

    Uses get_or_create so calling this twice updates rather than
    duplicates (idempotent within the same session).

    Returns the AttendanceRecord instance and a boolean created flag.
    """
    _validate_session_is_active(session)
    _validate_teacher_owns_session(session, marked_by)
    _validate_student_enrolled(session, student)

    if status not in AttendanceRecord.Status.values:
        raise ValueError(
            f"Invalid attendance status '{status}'. "
            f"Valid choices: {AttendanceRecord.Status.values}"
        )

    record, created = AttendanceRecord.objects.get_or_create(
        session=session,
        student=student,
        defaults={
            "status": status,
            "marked_by": marked_by,
        },
    )

    if not created and record.status != status:
        # Update if teacher is correcting an existing record
        record.status = status
        record.marked_by = marked_by
        record.save(update_fields=["status", "marked_by"])

    # Award points for attendance (Phase 4 Gamification)
    try:
        from apps.gamification.services.gamification_service import award_points
        from apps.gamification.models import PointTransaction
        
        if status == AttendanceRecord.Status.PRESENT:
            award_points(
                student=student,
                amount=10,
                transaction_type=PointTransaction.Type.ATTENDANCE,
                description=f"Attendance for {session}",
                source_obj=record
            )
        elif status == AttendanceRecord.Status.LATE:
            award_points(
                student=student,
                amount=5,
                transaction_type=PointTransaction.Type.ATTENDANCE,
                description=f"Late attendance for {session}",
                source_obj=record
            )
    except Exception as e:
        # Log error or ignore if gamification fails (should not block attendance)
        print(f"Failed to award points: {e}")

    return record, created


def bulk_mark_attendance(session, records, marked_by):
    """
    Marks attendance for multiple students in one call.

    Arguments:
        session   — Session instance (must be ACTIVE)
        records   — list of dicts: [{"student": <User>, "status": <str>}, ...]
        marked_by — User doing the marking (teacher or admin)

    Returns a dict:
        {
            "success": [AttendanceRecord, ...],
            "errors":  [{"student": <User>, "error": <str>}, ...]
        }

    Partial success is allowed — one invalid student does not
    block the rest from being recorded.
    """
    # Validate session and teacher once before looping
    try:
        _validate_session_is_active(session)
        _validate_teacher_owns_session(session, marked_by)
    except ValueError as e:
        # If session or teacher is invalid, fail the entire bulk operation
        return {
            "success": [],
            "errors": [{"student": None, "error": str(e)}],
        }

    results = []
    errors = []

    for entry in records:
        student = entry.get("student")
        status = entry.get("status")

        try:
            record, _ = mark_attendance(
                session=session,
                student=student,
                status=status,
                marked_by=marked_by,
            )
            results.append(record)
        except (ValueError, Exception) as e:
            errors.append({"student": student, "error": str(e)})

    return {"success": results, "errors": errors}


def get_session_attendance_summary(session):
    """
    Returns a summary dict of attendance counts for a session.

    Example return value:
        {
            "total": 20,
            "present": 15,
            "absent": 3,
            "late": 1,
            "excused": 1,
        }

    Used by reports (Phase 3) and teacher dashboard.
    """
    records = AttendanceRecord.objects.filter(session=session)
    summary = {
        "total": records.count(),
        "present": 0,
        "absent": 0,
        "late": 0,
        "excused": 0,
    }
    for record in records:
        summary[record.status] = summary.get(record.status, 0) + 1
    return summary
