from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class AuditLog(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )
    action = models.CharField(max_length=255)
    object_id = models.CharField(max_length=100, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action} ({self.created_at})"
