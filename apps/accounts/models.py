from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.choices import GenderChoices, GovernorateChoices

from .services import user_policy


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        PARENT = "parent", "Parent"
        VISITOR = "visitor", "Visitor"

    class RegistrationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.VISITOR,
        db_index=True,
    )
    registration_status = models.CharField(
        max_length=20,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
        db_index=True,
    )
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, blank=True)
    governorate = models.CharField(
        max_length=30,
        choices=GovernorateChoices.choices,
        blank=True,
        db_index=True,
    )
    approved_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_users",
    )
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["role", "registration_status"]),
            models.Index(fields=["governorate", "gender"]),
        ]
        ordering = ["-date_joined"]

    def clean(self):
        super().clean()
        if (
            user_policy.requires_contact_method(self)
            and not user_policy.has_contact_method(self)
        ):
            raise ValidationError(
                "Students must register with either email or phone number."
            )

    def save(self, *args, **kwargs):
        user_policy.apply_user_identity_normalization(self)
        user_policy.apply_role_state_defaults(self)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self):
        return self.role == self.Roles.ADMIN or self.is_superuser

    @property
    def is_teacher_role(self):
        return self.role == self.Roles.TEACHER

    @property
    def is_student_role(self):
        return self.role == self.Roles.STUDENT

    def __str__(self):
        return self.full_name


class ParentProfile(models.Model):
    """
    Links a parent user to a student user.

    Created as PENDING when parent requests linking.
    Approved by admin or the teacher of the student's circle.
    One parent per student (enforced via partial unique constraint).
    A parent account can be linked to up to three students (enforced in service).
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="linked_student_profiles",
        limit_choices_to={"role": "parent"},
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="parent_profiles",
        limit_choices_to={"role": "student"},
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_parent_profiles",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(status="approved"),
                name="unique_approved_parent_per_student",
            )
        ]
        indexes = [
            models.Index(fields=["status", "requested_at"]),
        ]

    def __str__(self):
        return f"{self.parent} → {self.student} ({self.status})"
