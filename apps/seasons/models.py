from datetime import time
from django.conf import settings
from django.db import models
from apps.core.models import SoftDeleteModel


class Season(SoftDeleteModel):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        REGISTRATION_OPEN = "registration_open", "Registration Open"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=140, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPCOMING,
        db_index=True,
    )
    default_session_start_time = models.TimeField(default=time(16, 0))
    default_session_end_time = models.TimeField(default=time(18, 0))
    archived_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "title"]
        indexes = [
            models.Index(fields=["status", "start_date", "end_date"]),
        ]

    def __str__(self):
        return self.title


class SeasonCircle(SoftDeleteModel):
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="season_circles",
    )
    circle = models.ForeignKey(
        "circles.Circle",
        on_delete=models.PROTECT,
        related_name="season_circles",
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="supervised_season_circles",
        limit_choices_to={"role": "teacher"},
    )
    capacity = models.PositiveIntegerField(default=25)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["season", "circle__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["season", "circle"],
                name="unique_circle_per_season",
            ),
        ]

    def __str__(self):
        return f"{self.circle.name_ar} - {self.season.title}"


class Enrollment(SoftDeleteModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        WITHDRAWN = "withdrawn", "Withdrawn"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="season_enrollments",
        limit_choices_to={"role": "student"},
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    season_circle = models.ForeignKey(
        SeasonCircle,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Approval audit trail
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_season_enrollments",
    )
    approved_at = models.DateTimeField(blank=True, null=True)

    # Withdrawal audit trail
    withdrawn_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="withdrawn_season_enrollments",
    )
    withdrawn_at = models.DateTimeField(blank=True, null=True)

    # Removal audit trail
    removal_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(status="active"),
                name="unique_active_season_enrollment_per_student",
            ),
            models.UniqueConstraint(
                fields=["student", "season"],
                name="unique_student_enrollment_per_season",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["season", "status"]),
        ]

    def __str__(self):
        circle_str = self.season_circle.circle.name_ar if self.season_circle else "No Circle Assigned"
        return f"{self.student} — {self.season} ({circle_str}) — ({self.get_status_display()})"


class SeasonSnapshot(SoftDeleteModel):
    season = models.OneToOneField(
        Season,
        on_delete=models.CASCADE,
        related_name="snapshot_record",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f"Snapshot for {self.season}"
