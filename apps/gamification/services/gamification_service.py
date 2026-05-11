import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

from apps.gamification.models import Badge, EarnedBadge, PointTransaction

logger = logging.getLogger(__name__)


def award_points(student, amount, transaction_type, description="", source_obj=None):
    """
    Awards points to a student and records the transaction in a single DB write.
    If source_obj is provided, the content type is resolved before creating
    the record so no second save is needed.
    """
    ct = None
    object_id = None
    if source_obj is not None:
        ct = ContentType.objects.get_for_model(source_obj)
        object_id = source_obj.pk

    transaction = PointTransaction.objects.create(
        student=student,
        amount=amount,
        transaction_type=transaction_type,
        description=description,
        content_type=ct,
        object_id=object_id,
    )

    check_badge_eligibility(student)
    return transaction


def get_total_points(student):
    """Calculates total points for a student."""
    return (
        PointTransaction.objects.filter(student=student).aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )


def check_badge_eligibility(student):
    """Checks if a student is eligible for any new badges."""
    total_points = get_total_points(student)
    available_badges = Badge.objects.filter(
        is_active=True, points_required__lte=total_points
    )
    for badge in available_badges:
        EarnedBadge.objects.get_or_create(student=student, badge=badge)