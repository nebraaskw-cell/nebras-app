from django.core.exceptions import ValidationError
from apps.seasons.models import Season, SeasonCircle


def validate_registration(student, season: Season):
    """
    Enforce that registration is only allowed if the season status is REGISTRATION_OPEN.
    """
    if season.status != Season.Status.REGISTRATION_OPEN:
        raise ValidationError(
            f"لا يمكن التسجيل في الموسم الحالي لأن حالته ليست مفتوحة للتسجيل (الحالة الحالية: {season.get_status_display()})."
        )


def validate_circle_selection(enrollment, season_circle: SeasonCircle):
    """
    Enforce that the selected circle is linked to the season of the enrollment.
    """
    if season_circle.season != enrollment.season:
        raise ValidationError(
            "الحلقة المختارة غير مرتبطة بالموسم الذي تم التسجيل فيه."
        )


def validate_session_creation(season_circle: SeasonCircle):
    """
    Enforce that sessions can only be created if the season status is ACTIVE.
    """
    if season_circle.season.status != Season.Status.ACTIVE:
        raise ValidationError(
            f"لا يمكن إنشاء جلسة جديدة لأن الموسم ليس في الحالة النشطة (الحالة الحالية: {season_circle.season.get_status_display()})."
        )


def validate_modification(season: Season):
    """
    Enforce that no data modification (students, attendance, sessions, etc.) is allowed after a season is ARCHIVED.
    """
    if season.status == Season.Status.ARCHIVED:
        raise ValidationError(
            "لا يمكن تعديل أي بيانات في هذا الموسم لأنه تمت أرشفته بالكامل."
        )
