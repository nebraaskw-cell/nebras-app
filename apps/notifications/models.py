from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        APPROVAL = "approval", "Approval"
        SESSION_REMINDER = "session_reminder", "Session Reminder"
        CYCLE_UPDATE = "cycle_update", "Cycle Update"
        GENERAL = "general", "General"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        db_index=True,
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.title}"
