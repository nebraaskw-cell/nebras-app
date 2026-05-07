from apps.chat.models import ChatMembership, ChatRoom


def get_or_create_global_room():
    """
    Returns the single global chat room.
    Creates it if it does not exist yet.
    Safe to call multiple times — idempotent.
    """
    room, _ = ChatRoom.objects.get_or_create(
        type=ChatRoom.Type.GLOBAL,
    )
    return room


def get_or_create_circle_room(circle):
    """
    Returns the chat room for a specific circle.
    Creates it if it does not exist yet.
    Called when a circle is created or when first needed.
    """
    room, _ = ChatRoom.objects.get_or_create(
        type=ChatRoom.Type.CIRCLE,
        circle=circle,
    )
    return room


def get_user_rooms(user):
    """
    Returns all chat rooms the user has access to.

    Rules:
    - Global room: all authenticated users (all roles)
    - Circle rooms: only via ChatMembership record
    """
    global_room = ChatRoom.objects.filter(
        type=ChatRoom.Type.GLOBAL,
        is_active=True,
    )
    circle_rooms = ChatRoom.objects.filter(
        type=ChatRoom.Type.CIRCLE,
        is_active=True,
        memberships__user=user,
    )
    return (global_room | circle_rooms).distinct()


def add_member_to_circle_room(circle, user, role_in_room):
    """
    Adds a user to a circle's chat room with the given role.
    Safe to call multiple times — uses get_or_create.

    role_in_room must be one of:
        'teacher', 'student', 'parent', 'admin'

    Returns the ChatMembership instance.
    """
    room = get_or_create_circle_room(circle)
    membership, _ = ChatMembership.objects.get_or_create(
        room=room,
        user=user,
        defaults={"role_in_room": role_in_room},
    )
    return membership


def remove_member_from_circle_room(circle, user):
    """
    Removes a user from a circle's chat room.
    Called when enrollment is withdrawn or parent link is removed.
    Silent if the room or membership does not exist.
    """
    try:
        room = ChatRoom.objects.get(
            type=ChatRoom.Type.CIRCLE,
            circle=circle,
        )
        ChatMembership.objects.filter(room=room, user=user).delete()
    except ChatRoom.DoesNotExist:
        pass
