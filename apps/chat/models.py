from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ChatRoom(TimeStampedModel):
    class Type(models.TextChoices):
        GLOBAL = "global", "Global"
        CIRCLE = "circle", "Circle"

    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.GLOBAL,
        db_index=True,
    )
    circle = models.OneToOneField(
        "circles.Circle",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="chat_room",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["type"],
                condition=models.Q(type="global"),
                name="unique_global_chat_room",
            )
        ]

    def __str__(self):
        if self.type == self.Type.GLOBAL:
            return "Global Chat"
        return f"Circle Chat — {self.circle}"


class ChatMessage(TimeStampedModel):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.PROTECT,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chat_messages",
    )
    body = models.TextField()
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_messages",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room", "created_at"]),
            models.Index(fields=["room", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.sender} in {self.room}: {self.body[:50]}"


class ChatMembership(TimeStampedModel):
    class RoleInRoom(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"
        PARENT = "parent", "Parent"
        ADMIN = "admin", "Admin"

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_memberships",
    )
    role_in_room = models.CharField(
        max_length=10,
        choices=RoleInRoom.choices,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["room", "user"],
                name="unique_membership_per_room",
            )
        ]
        indexes = [
            models.Index(fields=["room", "user"]),
        ]

    def __str__(self):
        return f"{self.user} in {self.room} as {self.role_in_room}"
