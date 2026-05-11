"""Data models for future audio submissions and automated evaluation results."""

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel


class Evaluation(SoftDeleteModel):
    """
    Stores evaluation results for student performance in sessions.
    """

    class EvaluationType(models.TextChoices):
        MEMORIZATION = "memorization", "Memorization"
        RECITATION = "recitation", "Recitation"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="evaluations",
        limit_choices_to={"role": "student"},
    )
    session = models.ForeignKey(
        "study_sessions.Session",
        on_delete=models.PROTECT,
        related_name="evaluations",
    )
    evaluation_type = models.CharField(
        max_length=20,
        choices=EvaluationType.choices,
        default=EvaluationType.MEMORIZATION,
    )
    score = models.IntegerField()  # 0-100
    feedback = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="given_evaluations",
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "session", "evaluation_type"],
                name="unique_evaluation_per_student_session_type",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "session"]),
            models.Index(fields=["evaluation_type", "evaluated_at"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.session} ({self.get_evaluation_type_display()}: {self.score})"

