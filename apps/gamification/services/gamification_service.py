from apps.gamification.models import PointTransaction, Badge, EarnedBadge
from django.db.models import Sum

def award_points(student, amount, transaction_type, description="", source_obj=None):
    """
    Awards points to a student and records the transaction.
    """
    transaction = PointTransaction.objects.create(
        student=student,
        amount=amount,
        transaction_type=transaction_type,
        description=description
    )
    if source_obj:
        from django.contrib.contenttypes.models import ContentType
        transaction.content_type = ContentType.objects.get_for_model(source_obj)
        transaction.object_id = source_obj.id
        transaction.save()
        
    # Check for new badges
    check_badge_eligibility(student)
    return transaction

def get_total_points(student):
    """Calculates total points for a student."""
    return PointTransaction.objects.filter(student=student).aggregate(total=Sum('amount'))['total'] or 0

def check_badge_eligibility(student):
    """Checks if a student is eligible for any new badges."""
    total_points = get_total_points(student)
    available_badges = Badge.objects.filter(is_active=True, points_required__lte=total_points)
    
    for badge in available_badges:
        EarnedBadge.objects.get_or_create(student=student, badge=badge)
