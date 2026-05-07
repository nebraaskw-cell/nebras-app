from django.conf import settings
from django.db import models


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    session = models.ForeignKey(
        "study_sessions.Session",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={"role": "student"},
        related_name="attendance_records",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABSENT,
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="marked_attendances",
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "student"],
                name="unique_attendance_per_session_student",
            ),
        ]
        indexes = [
            models.Index(fields=["session", "status"]),
            models.Index(fields=["student", "marked_at"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.session} ({self.get_status_display()})"
