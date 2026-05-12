from django.utils import timezone

from apps.circles.models import Enrollment


def _validate_student(student):
    """Guard: only user with role=student can be enrolled."""
    if getattr(student, "role", None) != "student":
        raise ValueError("Only student users can be enrolled.")


def enroll_student(student, cycle, enrolled_by):
    """
    Creates a PENDING enrollment for the student in the given cycle.

    Rules enforced:
    - User must have role=student.
    - Student must have NO existing PENDING or ACTIVE enrollment
      in any cycle. A student can only be in one circle at a time.
    - The target cycle cannot be completed or archived.
    - The target cycle must have available capacity.

    Raises ValueError if any conflict exists.
    Returns the new Enrollment instance.
    """
    _validate_student(student)

    if cycle.status in [cycle.Status.COMPLETED, cycle.Status.ARCHIVED]:
        raise ValueError(
            "Cannot enroll in a cycle that is completed or archived."
        )

    capacity_usage = Enrollment.objects.filter(
        cycle=cycle,
        status__in=[Enrollment.Status.PENDING, Enrollment.Status.ACTIVE],
    ).count()
    if capacity_usage >= cycle.circle.capacity:
        raise ValueError(
            "This cycle is full and cannot accept additional enrollments."
        )

    conflicting = Enrollment.objects.filter(
        student=student,
        status__in=[Enrollment.Status.PENDING, Enrollment.Status.ACTIVE],
    ).select_related("cycle").first()

    if conflicting:
        raise ValueError(
            f"Student already has a {conflicting.get_status_display()} enrollment "
            f"in '{conflicting.cycle}'. "
            "Withdraw the existing enrollment before enrolling in a new cycle."
        )

    return Enrollment.objects.create(
        student=student,
        cycle=cycle,
        status=Enrollment.Status.PENDING,
    )


def approve_enrollment(enrollment, approved_by):
    """
    Transitions a PENDING enrollment to ACTIVE.

    Rules enforced:
    - User on the enrollment must have role=student.
    - Any other ACTIVE enrollment for this student is withdrawn
      first (with audit trail).

    Returns the updated Enrollment instance.
    """
    _validate_student(enrollment.student)

    now = timezone.now()

    # Withdraw any other active enrollment for this student
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


def withdraw_enrollment(enrollment, withdrawn_by):
    """
    Transitions any enrollment to WITHDRAWN.
    Records who withdrew and when for full audit trail.

    Returns the updated Enrollment instance.
    """
    now = timezone.now()
    enrollment.status = Enrollment.Status.WITHDRAWN
    enrollment.withdrawn_by = withdrawn_by
    enrollment.withdrawn_at = now
    enrollment.save(
        update_fields=["status", "withdrawn_by", "withdrawn_at", "updated_at"]
    )
    return enrollment


def remove_enrollment(enrollment, removed_by, reason):
    """
    Removes a student from enrollment with reason.
    Similar to withdraw but records removal reason.

    Returns the updated Enrollment instance.
    """
    now = timezone.now()
    enrollment.status = Enrollment.Status.WITHDRAWN
    enrollment.withdrawn_by = removed_by
    enrollment.withdrawn_at = now
    enrollment.removal_reason = reason
    enrollment.save(
        update_fields=["status", "withdrawn_by", "withdrawn_at", "removal_reason", "updated_at"]
    )
    return enrollment


def complete_enrollment(enrollment):
    """
    Transitions an ACTIVE enrollment to COMPLETED at cycle end.
    Called by cycle archiving logic (Phase 4).

    Returns the updated Enrollment instance.
    """
    if enrollment.status != Enrollment.Status.ACTIVE:
        raise ValueError(
            f"Only ACTIVE enrollments can be completed. "
            f"Current status: {enrollment.status}"
        )
    enrollment.status = Enrollment.Status.COMPLETED
    enrollment.save(update_fields=["status", "updated_at"])
    return enrollment
