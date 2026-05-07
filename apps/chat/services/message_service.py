from django.utils import timezone

from apps.chat.models import ChatMessage, ChatMembership, ChatRoom


def _can_access_room(user, room):
    """
    Returns True if user can access the given room.

    Global room: any authenticated user (all roles including Visitor).
    Circle room: user must have a ChatMembership record.
    """
    if not user.is_authenticated:
        return False
    if room.type == ChatRoom.Type.GLOBAL:
        return True
    return ChatMembership.objects.filter(room=room, user=user).exists()


def _can_delete_message(user, message):
    """
    Determines if a user can delete a given message.

    - Admins can delete any message in any room.
    - Teacher of a circle can delete any message in that circle's room.
    - All other users can only delete their own messages.
    """
    if getattr(user, "is_admin_role", False):
        return True

    room = message.room
    if room.type == ChatRoom.Type.CIRCLE and room.circle is not None:
        if room.circle.teacher_id == user.pk:
            return True

    return message.sender_id == user.pk


def send_message(room, sender, body, reply_to=None):
    """
    Sends a message to a chat room.

    Validates:
    - sender must have access to the room
    - body must not be empty after stripping whitespace
    - reply_to must belong to the same room if provided
    - reply_to message must not be deleted

    Returns the created ChatMessage instance.
    """
    if not _can_access_room(sender, room):
        raise ValueError(
            "You do not have access to this chat room."
        )

    body = body.strip()
    if not body:
        raise ValueError("Message body cannot be empty.")

    if reply_to is not None:
        if reply_to.room_id != room.pk:
            raise ValueError(
                "Cannot reply to a message from a different room."
            )
        if reply_to.is_deleted:
            raise ValueError(
                "Cannot reply to a deleted message."
            )

    return ChatMessage.objects.create(
        room=room,
        sender=sender,
        body=body,
        reply_to=reply_to,
    )


def delete_message(message, deleted_by):
    """
    Soft-deletes a message.
    Records who deleted it and when.

    Raises ValueError if:
    - message is already deleted
    - user does not have permission to delete
    """
    if message.is_deleted:
        raise ValueError("This message has already been deleted.")

    if not _can_delete_message(deleted_by, message):
        raise ValueError(
            "You do not have permission to delete this message."
        )

    message.is_deleted = True
    message.deleted_at = timezone.now()
    message.deleted_by = deleted_by
    message.save(update_fields=[
        "is_deleted", "deleted_at", "deleted_by",
    ])
    return message


def get_room_messages(room, page=1, page_size=50):
    """
    Returns paginated non-deleted messages for a room.
    Ordered oldest-first within the page.
    Eager-loads sender and reply_to data for efficiency.

    Returns a QuerySet slice.
    """
    offset = (page - 1) * page_size
    return (
        ChatMessage.objects
        .filter(room=room, is_deleted=False)
        .select_related(
            "sender",
            "reply_to",
            "reply_to__sender",
        )
        .order_by("created_at")[offset: offset + page_size]
    )
