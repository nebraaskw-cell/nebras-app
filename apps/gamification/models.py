from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class PointTransaction(TimeStampedModel):
    class Type(models.TextChoices):
        ATTENDANCE = "attendance", "Attendance"
        RECITATION = "recitation", "Recitation"
        STREAK = "streak", "Streak Bonus"
        SPECIAL = "special", "Special Achievement"
        ADMIN = "admin", "Admin Adjustment"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_transactions",
        limit_choices_to={"role": "student"}
    )
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    description = models.CharField(max_length=255, blank=True)
    
    # Optional link to the source of the points
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student}: {self.amount} ({self.transaction_type})"


class Badge(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="badges/", blank=True, null=True)
    points_required = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class EarnedBadge(TimeStampedModel):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="earned_badges",
        limit_choices_to={"role": "student"}
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="earned_by")
    
    class Meta:
        unique_together = ("student", "badge")

    def __str__(self):
        return f"{self.student} earned {self.badge}"
