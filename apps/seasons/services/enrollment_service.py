from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.seasons.models import Enrollment, Season, SeasonCircle
from apps.seasons.policies import seasons_policy


def _validate_student(student):
    """Guard: only user with role=student can be enrolled."""
    if getattr(student, "role", None) != "student":
        raise ValueError("Only student users can be enrolled.")


def enroll_student_in_season(student, season: Season, enrolled_by=None):
    """
    Step 1: Enroll a student in a Season.
    Creates a PENDING enrollment for the student in the given season.
    """
    _validate_student(student)

    # 1. Enforce policy: Season must be REGISTRATION_OPEN
    seasons_policy.validate_registration(student, season)

    # 2. Check if student already has a pending or active enrollment globally
    conflicting = Enrollment.objects.filter(
        student=student,
        status__in=[Enrollment.Status.PENDING, Enrollment.Status.ACTIVE],
    ).first()

    if conflicting:
        raise ValidationError(
            f"الطالب لديه بالفعل تسجيل ({conflicting.get_status_display()}) في موسم '{conflicting.season}'."
        )

    # Create the season registration (initially with no circle assigned)
    return Enrollment.objects.create(
        student=student,
        season=season,
        status=Enrollment.Status.PENDING,
    )


def assign_circle_to_enrollment(enrollment: Enrollment, season_circle: SeasonCircle, assigned_by=None):
    """
    Step 2: Assign a specific Circle to a student's Season Enrollment.
    """
    _validate_student(enrollment.student)

    # 1. Enforce policy: Selected circle must be associated with the season
    seasons_policy.validate_circle_selection(enrollment, season_circle)

    # 2. Enforce policy: Season must not be archived
    seasons_policy.validate_modification(enrollment.season)

    # 3. Check capacity limits for this circle in this season
    capacity_usage = Enrollment.objects.filter(
        season_circle=season_circle,
        status__in=[Enrollment.Status.PENDING, Enrollment.Status.ACTIVE],
    ).count()

    if capacity_usage >= season_circle.capacity:
        raise ValidationError(
            "هذه الحلقة ممتلئة بالكامل في الموسم الحالي ولا يمكن قبول المزيد من التسجيلات."
        )

    enrollment.season_circle = season_circle
    enrollment.save(update_fields=["season_circle", "updated_at"])
    return enrollment


def approve_enrollment(enrollment: Enrollment, approved_by):
    """
    Transitions a PENDING enrollment to ACTIVE.
    """
    _validate_student(enrollment.student)
    seasons_policy.validate_modification(enrollment.season)

    now = timezone.now()

    # Withdraw any other active enrollment globally
    other_active = Enrollment.objects.filter(
        student=enrollment.student,
        status=Enrollment.Status.ACTIVE,
    ).exclude(pk=enrollment.pk)

    for other in other_active:
        other.status = Enrollment.Status.WITHDRAWN
        other.withdrawn_by = approved_by
        other.withdrawn_at = now
        other.save(update_fields=["status", "withdrawn_by", "withdrawn_at", "updated_at"])

    enrollment.status = Enrollment.Status.ACTIVE
    enrollment.approved_by = approved_by
    enrollment.approved_at = now
    enrollment.save(
        update_fields=["status", "approved_by", "approved_at", "updated_at"]
    )
    return enrollment


def withdraw_enrollment(enrollment: Enrollment, withdrawn_by):
    """
    Transitions enrollment to WITHDRAWN.
    """
    seasons_policy.validate_modification(enrollment.season)
    now = timezone.now()
    enrollment.status = Enrollment.Status.WITHDRAWN
    enrollment.withdrawn_by = withdrawn_by
    enrollment.withdrawn_at = now
    enrollment.save(
        update_fields=["status", "withdrawn_by", "withdrawn_at", "updated_at"]
    )
    return enrollment


def remove_enrollment(enrollment: Enrollment, removed_by, reason):
    """
    Removes a student from enrollment with a reason.
    """
    seasons_policy.validate_modification(enrollment.season)
    now = timezone.now()
    enrollment.status = Enrollment.Status.WITHDRAWN
    enrollment.withdrawn_by = removed_by
    enrollment.withdrawn_at = now
    enrollment.removal_reason = reason
    enrollment.save(
        update_fields=["status", "withdrawn_by", "withdrawn_at", "removal_reason", "updated_at"]
    )
    return enrollment


def complete_enrollment(enrollment: Enrollment):
    """
    Transitions an ACTIVE enrollment to COMPLETED at season end.
    """
    if enrollment.status != Enrollment.Status.ACTIVE:
        raise ValueError(
            f"Only ACTIVE enrollments can be completed. Current status: {enrollment.status}"
        )
    enrollment.status = Enrollment.Status.COMPLETED
    enrollment.save(update_fields=["status", "updated_at"])
    return enrollment
