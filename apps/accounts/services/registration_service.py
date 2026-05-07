from django.utils import timezone

from apps.accounts.models import User

from . import user_policy


def has_contact_method(source):
    """
    Proxy to user_policy.has_contact_method().
    Called by StudentRegistrationForm.clean() and StudentRegistrationSerializer.validate().
    Accepts either a dict (cleaned_data / validated_data) or a model instance.
    """
    return user_policy.has_contact_method(source)


def prepare_pending_student(user):
    """
    Prepares a user instance as a pending student (without saving).
    Called by StudentRegistrationForm.save().
    Sets role=student; the model's save() hook in user_policy
    will then set registration_status=pending and is_active=False.
    """
    user.role = User.Roles.STUDENT
    return user


def create_pending_student(validated_data):
    """
    Creates a new student user from API registration data.
    Called by StudentRegistrationSerializer.create().
    Extracts password, sets role=student, creates user with hashed password.
    Returns the created User instance.
    """
    password = validated_data.pop("password")
    validated_data["role"] = User.Roles.STUDENT
    # Normalize contacts before creation
    user_policy.apply_user_identity_normalization_dict(validated_data)
    user = User(**validated_data)
    user.set_password(password)
    user.save()
    return user


def get_pending_students():
    """
    Returns a queryset of all students with PENDING registration status.
    Called by PendingStudentListAPIView.get_queryset().
    """
    return User.objects.filter(
        role=User.Roles.STUDENT,
        registration_status=User.RegistrationStatus.PENDING,
    ).order_by("-date_joined")


def approve_student_registration(student, approved_by):
    """
    Convenience alias used by ApproveStudentAPIView.
    Delegates to approve_user().
    """
    return approve_user(student, approved_by)


def approve_user(user, approved_by):
    """
    Approves a pending user registration.

    Sets:
    - registration_status → APPROVED
    - is_active → True (user can now log in)
    - approved_by → the admin or teacher who approved
    - approved_at → current timestamp

    IMPORTANT: 'registration_status' MUST be in update_fields.
    The accounts/signals.py on_user_approved signal relies on this
    to detect the transition and send the approval notification.
    Without it in update_fields, the notification will NOT fire.

    Raises ValueError if user is not in PENDING status.
    """
    if user.registration_status != User.RegistrationStatus.PENDING:
        raise ValueError(
            f"Cannot approve a user with status '{user.registration_status}'. "
            "Only PENDING users can be approved."
        )

    user.registration_status = User.RegistrationStatus.APPROVED
    user.is_active = True
    user.approved_by = approved_by
    user.approved_at = timezone.now()
    user.save(update_fields=[
		"registration_status",
		"is_active",
		"approved_by",
		"approved_at",
		])
    return user


def reject_user(user, rejected_by):
    """
    Rejects a pending user registration.

    Sets:
    - registration_status → REJECTED
    - is_active → False

    The user cannot log in after rejection.
    Raises ValueError if user is not in PENDING status.
    """
    if user.registration_status != User.RegistrationStatus.PENDING:
        raise ValueError(
            f"Cannot reject a user with status '{user.registration_status}'. "
            "Only PENDING users can be rejected."
        )

    user.registration_status = User.RegistrationStatus.REJECTED
    user.is_active = False
    user.save(update_fields=[
        "registration_status",
        "is_active",
    ])
    return user
