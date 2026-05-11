from datetime import time

from django.conf import settings
from django.db import models

from apps.core.choices import GenderChoices, GovernorateChoices
from apps.core.models import SoftDeleteModel

from .services import cycle_service


class Circle(SoftDeleteModel):
    name = models.CharField(max_length=120, unique=True)
    name_ar = models.CharField(max_length=120, unique=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, db_index=True)
    governorate = models.CharField(max_length=30, choices=GovernorateChoices.choices, db_index=True)
    mosque_name = models.CharField(max_length=160)
    location_name = models.CharField(max_length=160, blank=True)
    capacity = models.PositiveIntegerField(default=25)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="assigned_circles",
        limit_choices_to={"role": "teacher"},
    )
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["governorate", "gender", "name"]
        indexes = [
            models.Index(fields=["governorate", "gender", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name_ar} ({self.get_governorate_display()})"


class Cycle(SoftDeleteModel):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    circle = models.ForeignKey(Circle, on_delete=models.PROTECT, related_name="cycles")
    title = models.CharField(max_length=140)
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
        ordering = ["-start_date", "circle__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["circle", "title"],
                name="unique_cycle_title_per_circle",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "start_date", "end_date"]),
        ]

    def clean(self):
        super().clean()
        cycle_service.validate_cycle_dates(self.start_date, self.end_date)
        cycle_service.validate_session_time_window(
            self.default_session_start_time,
            self.default_session_end_time,
        )

    def save(self, *args, **kwargs):
        # Auto-calculate end_date from start_date if not provided
        if self.start_date and not self.end_date:
            self.end_date = cycle_service.calculate_cycle_end_date(self.start_date)

        self.full_clean()

        # Capture previous status before saving so we can detect transition
        is_new = self._state.adding
        previous_status = None
        if not is_new:
            try:
                previous_status = Cycle.objects.get(pk=self.pk).status
            except Cycle.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Auto-generate sessions when cycle first becomes ACTIVE
        transitioning_to_active = (
            self.status == self.Status.ACTIVE
            and (is_new or previous_status != self.Status.ACTIVE)
        )
        if transitioning_to_active:
            # Lazy import to avoid circular dependency
            from apps.study_sessions.services.session_service import (
                generate_sessions_for_cycle,
            )
            generate_sessions_for_cycle(self)

    def __str__(self):
        return f"{self.title} - {self.circle.name_ar}"


class Enrollment(SoftDeleteModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        WITHDRAWN = "withdrawn", "Withdrawn"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
    )
    cycle = models.ForeignKey(
        Cycle,
        on_delete=models.PROTECT,
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
        related_name="approved_enrollments",
    )
    approved_at = models.DateTimeField(blank=True, null=True)

    # Withdrawal audit trail
    withdrawn_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="withdrawn_enrollments",
    )
    withdrawn_at = models.DateTimeField(blank=True, null=True)

    # Removal audit trail (for teacher/admin removal)
    removal_reason = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(status="active"),
                name="unique_active_enrollment_per_student",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["cycle", "status"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.cycle} ({self.get_status_display()})"
