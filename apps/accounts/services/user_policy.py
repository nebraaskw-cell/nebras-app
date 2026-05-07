ADMIN_ROLE = "admin"
APPROVED_STATUS = "approved"
PENDING_STATUS = "pending"
STUDENT_ROLE = "student"


def _read(source, field_name):
    if hasattr(source, "get"):
        return source.get(field_name)
    return getattr(source, field_name, None)


def normalize_optional_contact(value):
    if value == "":
        return None
    return value


def normalize_email(value):
    value = normalize_optional_contact(value)
    if value:
        return value.lower()
    return value


def has_contact_method(source):
    return bool(_read(source, "email") or _read(source, "phone_number"))


def requires_contact_method(user):
    return getattr(user, "role", None) == STUDENT_ROLE


def apply_user_identity_normalization(user):
    user.email = normalize_email(getattr(user, "email", None))
    user.phone_number = normalize_optional_contact(getattr(user, "phone_number", None))
    return user


def apply_user_identity_normalization_dict(data):
    """Dict-compatible variant used by create_pending_student()."""
    if "email" in data:
        data["email"] = normalize_email(data["email"])
    if "phone_number" in data:
        data["phone_number"] = normalize_optional_contact(data["phone_number"])
    return data


def apply_role_state_defaults(user):
    """
    Enforces role-based state rules on save.
    - Superusers are always admin + approved + active.
    - New students are always set to PENDING + inactive (awaiting approval).
    """
    if getattr(user, "is_superuser", False):
        user.role = ADMIN_ROLE
        user.registration_status = APPROVED_STATUS
        user.is_active = True
        return user

    state = getattr(user, "_state", None)
    is_new = state and state.adding

    if is_new and getattr(user, "role", None) == STUDENT_ROLE:
        user.registration_status = PENDING_STATUS
        user.is_active = False

    return user
