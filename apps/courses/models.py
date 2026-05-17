from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel


class Course(SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    class EnrollmentMode(models.TextChoices):
        OPEN = "open", "Open"
        APPROVAL_REQUIRED = "approval_required", "Approval Required"
        INVITATION_ONLY = "invitation_only", "Invitation Only"

    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="courses",
        limit_choices_to={"role": "teacher"},
    )

    capacity = models.PositiveIntegerField(default=50)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    enrollment_mode = models.CharField(
        max_length=20,
        choices=EnrollmentMode.choices,
        default=EnrollmentMode.OPEN,
        db_index=True,
    )

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_islamic_content = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "start_date"]),
            models.Index(fields=["teacher", "status"]),
        ]

    def __str__(self):
        return self.title_ar or self.title


class CourseModule(SoftDeleteModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
    )
    sequence_order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ["sequence_order"]
        unique_together = ["course", "sequence_order"]
        indexes = [
            models.Index(fields=["course", "sequence_order"]),
        ]

    def __str__(self):
        return f"{self.course.title_ar} - {self.title_ar}"


class Lesson(SoftDeleteModel):
    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    sequence_order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    has_quiz = models.BooleanField(default=False)

    class Meta:
        ordering = ["sequence_order"]
        unique_together = ["module", "sequence_order"]
        indexes = [
            models.Index(fields=["module", "sequence_order"]),
        ]

    def __str__(self):
        return f"{self.module.title_ar} - {self.title_ar}"


class CourseEnrollment(SoftDeleteModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_enrollments",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(
        Course,
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
        related_name="approved_course_enrollments",
    )
    approved_at = models.DateTimeField(blank=True, null=True)

    # Completion tracking
    completion_date = models.DateTimeField(blank=True, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    progress_percent = models.PositiveIntegerField(default=0)

    # Withdrawal audit trail
    withdrawn_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="withdrawn_course_enrollments",
    )
    withdrawn_at = models.DateTimeField(blank=True, null=True)

    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                condition=models.Q(status__in=["pending", "active"]),
                name="unique_pending_active_enrollment_per_course",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["course", "status"]),
            models.Index(fields=["status", "enrolled_at"]),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title_ar}"


class LessonCompletion(SoftDeleteModel):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_completions",
        limit_choices_to={"role": "student"},
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    quiz_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ["student", "lesson"]
        indexes = [
            models.Index(fields=["student", "completed_at"]),
            models.Index(fields=["lesson", "completed_at"]),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.title_ar}"


class ModuleCompletion(SoftDeleteModel):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OPTIONAL_SKIPPED = "optional_skipped", "Optional Skipped"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="module_completions",
        limit_choices_to={"role": "student"},
    )
    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        db_index=True,
    )

    class Meta:
        unique_together = ["student", "module"]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["module", "status"]),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.module.title_ar}"


class Certificate(SoftDeleteModel):
    enrollment = models.OneToOneField(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name="certificate",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    issued_date = models.DateTimeField(auto_now_add=True)
    certificate_code = models.CharField(max_length=50, unique=True)
    is_issued = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["student", "issued_date"]),
            models.Index(fields=["course", "issued_date"]),
        ]

    def __str__(self):
        return f"Certificate: {self.student.full_name} - {self.course.title_ar}"
