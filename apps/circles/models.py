from django.conf import settings
from django.db import models

from apps.core.choices import GenderChoices, GovernorateChoices
from apps.core.models import SoftDeleteModel


class Circle(SoftDeleteModel):
    class Status(models.TextChoices):
        OPEN = "open", "مفتوحة"
        CLOSED = "closed", "مغلقة"

    name = models.CharField(max_length=120, unique=True)
    name_ar = models.CharField(max_length=120, unique=True)
    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        db_index=True
    )
    description = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True
    )
    governorate = models.CharField(
        max_length=30,
        choices=GovernorateChoices.choices,
        db_index=True
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="assigned_circles",
        limit_choices_to={"role": "teacher"},
    )
    image = models.ImageField(upload_to="circles/", blank=True, null=True)

    class Meta:
        ordering = ["governorate", "name"]
        indexes = [
            models.Index(fields=["governorate", "gender", "status"]),
        ]

    def __str__(self):
        return f"{self.name_ar} ({self.get_gender_display()} - {self.get_governorate_display()})"
