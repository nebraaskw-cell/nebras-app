from django.utils import timezone

from apps.accounts.models import ParentProfile, User


MAX_STUDENTS_PER_PARENT = 3
COUNTED_PARENT_LINK_STATUSES = [
    ParentProfile.Status.PENDING,
    ParentProfile.Status.APPROVED,
]


def _validate_parent_user(user):
    if getattr(user, "role", None) != User.Roles.PARENT:
        raise ValueError("Only users with role=parent can request linking.")


def _validate_student_user(user):
    if getattr(user, "role", None) != User.Roles.STUDENT:
        raise ValueError("Can only link to a user with role=student.")


def _validate_parent_link_capacity(parent):
    active_link_count = ParentProfile.objects.filter(
        parent=parent,
        status__in=COUNTED_PARENT_LINK_STATUSES,
    ).count()
    if active_link_count >= MAX_STUDENTS_PER_PARENT:
        raise ValueError(
            "A parent account can be linked to a maximum of 3 students."
        )


def _validate_approver(approved_by, student):
    """
    Only an admin or the teacher of the student's active circle
    can approve a parent linking request.
    """
    if getattr(approved_by, "is_admin_role", False):
        return

    from apps.circles.models import Enrollment

    active_enrollment = (
        Enrollment.objects
        .filter(student=student, status="active")
        .select_related("cycle__circle__teacher")
        .first()
    )

    if not active_enrollment:
        raise ValueError(
            "Student has no active enrollment. "
            "Only an admin can approve this linking request."
        )

    circle_teacher = active_enrollment.cycle.circle.teacher
    if circle_teacher is None or circle_teacher.pk != approved_by.pk:
        raise ValueError(
            "Only the teacher of the student's circle "
            "or an admin can approve parent linking."
        )


def request_parent_linking(parent, student, notes=""):
    """
    Parent requests to be linked to a student.

    A parent can have up to three PENDING/APPROVED student links.
    Rejected links do not count against the limit.
    """
    _validate_parent_user(parent)
    _validate_student_user(student)
    _validate_parent_link_capacity(parent)

    if ParentProfile.objects.filter(
        parent=parent,
        student=student,
        status__in=COUNTED_PARENT_LINK_STATUSES,
    ).exists():
        raise ValueError(
            "A pending or approved link already exists for this student."
        )

    if student.registration_status != User.RegistrationStatus.APPROVED:
        raise ValueError(
            "Cannot request a parent link for a student who is not approved."
        )

    if ParentProfile.objects.filter(
        student=student,
        status=ParentProfile.Status.APPROVED,
    ).exists():
        raise ValueError("This student already has an approved parent linked.")

    return ParentProfile.objects.create(
        parent=parent,
        student=student,
        status=ParentProfile.Status.PENDING,
        notes=notes,
    )


def approve_parent_linking(profile, approved_by):
    """
    Approves a PENDING parent linking request.

    Validates:
    - profile must be in PENDING status
    - parent must still be within the three-student limit
    - approved_by must be admin or teacher of student's active circle
    """
    if profile.status != ParentProfile.Status.PENDING:
        raise ValueError(
            f"Only PENDING profiles can be approved. "
            f"Current status: {profile.status}."
        )

    approved_link_count = ParentProfile.objects.filter(
        parent=profile.parent,
        status=ParentProfile.Status.APPROVED,
    ).exclude(pk=profile.pk).count()
    if approved_link_count >= MAX_STUDENTS_PER_PARENT:
        raise ValueError(
            "A parent account can be linked to a maximum of 3 students."
        )

    if ParentProfile.objects.filter(
        student=profile.student,
        status=ParentProfile.Status.APPROVED,
    ).exclude(pk=profile.pk).exists():
        raise ValueError("This student already has an approved parent linked.")

    _validate_approver(approved_by, profile.student)

    profile.status = ParentProfile.Status.APPROVED
    profile.approved_by = approved_by
    profile.approved_at = timezone.now()
    profile.save(update_fields=["status", "approved_by", "approved_at"])

    from apps.notifications.services.notification_service import notify

    notify(
        recipient=profile.parent,
        type="general",
        title="تم ربط حسابك بحساب الطالب",
        body=(
            f"تم ربط حسابك بحساب الطالب {profile.student.full_name}. "
            "يمكنك الآن متابعة تقدمه وتقاريره من لوحة ولي الأمر."
        ),
    )

    return profile


def reject_parent_linking(profile, rejected_by):
    """
    Rejects a PENDING parent linking request.

    Returns the updated ParentProfile instance.
    """
    if profile.status != ParentProfile.Status.PENDING:
        raise ValueError(
            f"Only PENDING profiles can be rejected. "
            f"Current status: {profile.status}."
        )

    profile.status = ParentProfile.Status.REJECTED
    profile.save(update_fields=["status"])
    return profile
