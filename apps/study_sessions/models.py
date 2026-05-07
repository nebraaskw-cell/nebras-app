from django.db import models

from apps.core.models import SoftDeleteModel


class Session(SoftDeleteModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    cycle = models.ForeignKey(
        "circles.Cycle",
        on_delete=models.PROTECT,
        related_name="sessions",
    )
    title = models.CharField(max_length=140, blank=True)
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
    )
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_auto_generated = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["date", "start_time"]
        indexes = [
            models.Index(fields=["cycle", "date", "status"]),
        ]

    def __str__(self):
        return self.title or f"{self.cycle} - {self.date}"
