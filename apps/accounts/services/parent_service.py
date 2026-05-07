from django.utils import timezone

from apps.accounts.models import ParentProfile, User


def _validate_parent_user(user):
    if getattr(user, "role", None) != User.Roles.PARENT:
        raise ValueError("Only users with role=parent can request linking.")


def _validate_student_user(user):
    if getattr(user, "role", None) != User.Roles.STUDENT:
        raise ValueError("Can only link to a user with role=student.")


def _validate_approver(approved_by, student):
    """
    Only an admin or the teacher of the student's active circle
    can approve a parent linking request.
    """
    if getattr(approved_by, "is_admin_role", False):
        return  # Admins always allowed

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


def _add_parent_to_circle_chat(profile):
    """
    Adds the parent to the circle chat room of the student's
    active enrollment. Silent if the student has no active enrollment.
    """
    from apps.circles.models import Enrollment
    from apps.chat.services.room_service import add_member_to_circle_room

    active_enrollment = (
        Enrollment.objects
        .filter(student=profile.student, status="active")
        .select_related("cycle__circle")
        .first()
    )

    if active_enrollment:
        add_member_to_circle_room(
            circle=active_enrollment.cycle.circle,
            user=profile.parent,
            role_in_room="parent",
        )


def request_parent_linking(parent, student):
    """
    Parent requests to be linked to a student.

    Validates:
    - parent must have role=parent
    - student must have role=student
    - parent must not already have any active profile (OneToOne)
    - student must not already have an approved parent

    Creates a PENDING ParentProfile.
    Returns the ParentProfile instance.
    """
    _validate_parent_user(parent)
    _validate_student_user(student)

    # Check parent is not already linked (approved)
    if ParentProfile.objects.filter(
        parent=parent,
        status=ParentProfile.Status.APPROVED,
    ).exists():
        raise ValueError(
            "This parent account is already linked to a student."
        )

    # Check student does not already have an approved parent
    if ParentProfile.objects.filter(
        student=student,
        status=ParentProfile.Status.APPROVED,
    ).exists():
        raise ValueError(
            "This student already has an approved parent linked."
        )

    # Check for duplicate pending request
    if ParentProfile.objects.filter(
        parent=parent,
        student=student,
        status=ParentProfile.Status.PENDING,
    ).exists():
        raise ValueError(
            "A pending linking request already exists for this parent and student."
        )

    return ParentProfile.objects.create(
        parent=parent,
        student=student,
        status=ParentProfile.Status.PENDING,
    )


def approve_parent_linking(profile, approved_by):
    """
    Approves a PENDING parent linking request.

    Validates:
    - profile must be in PENDING status
    - approved_by must be admin or teacher of student's active circle

    On approval:
    - Sets status to APPROVED with audit trail
    - Adds parent to the student's circle chat room
    - Sends notification to the parent

    Returns the updated ParentProfile instance.
    """
    if profile.status != ParentProfile.Status.PENDING:
        raise ValueError(
            f"Only PENDING profiles can be approved. "
            f"Current status: {profile.status}."
        )

    _validate_approver(approved_by, profile.student)

    profile.status = ParentProfile.Status.APPROVED
    profile.approved_by = approved_by
    profile.approved_at = timezone.now()
    profile.save(update_fields=["status", "approved_by", "approved_at"])

    # Add parent to circle chat
    _add_parent_to_circle_chat(profile)

    # Notify parent
    from apps.notifications.services.notification_service import notify
    notify(
        recipient=profile.parent,
        type="general",
        title="تم ربط حسابك بحساب الطالب",
        body=(
            f"تم ربط حسابك بحساب الطالب {profile.student.full_name}. "
            "يمكنك الآن متابعة تقدمه والتواصل في مجموعة الحلقة."
        ),
    )

    return profile


def reject_parent_linking(profile, rejected_by):
    """
    Rejects a PENDING parent linking request.

    Validates:
    - profile must be in PENDING status

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
