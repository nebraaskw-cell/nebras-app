from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.circles.models import Circle, Enrollment


@receiver(post_save, sender=Circle)
def on_circle_created(sender, instance, created, **kwargs):
    """
    When a new Circle is created:
    1. Auto-create its chat room.
    2. Add the assigned teacher as a member (if assigned).
    """
    if not created:
        return

    from apps.chat.services.room_service import (
        add_member_to_circle_room,
        get_or_create_circle_room,
    )

    get_or_create_circle_room(instance)

    if instance.teacher:
        add_member_to_circle_room(
            circle=instance,
            user=instance.teacher,
            role_in_room="teacher",
        )


@receiver(post_save, sender=Enrollment)
def on_enrollment_status_changed(sender, instance, created, **kwargs):
    """
    When an Enrollment status changes to ACTIVE:
    → Add the student to the circle's chat room.

    When an Enrollment status changes to WITHDRAWN or COMPLETED:
    → Remove the student from the circle's chat room.

    Uses update_fields guard to avoid firing on unrelated saves.
    """
    if created:
        return

    update_fields = kwargs.get("update_fields") or []
    if "status" not in update_fields:
        return

    from apps.chat.services.room_service import (
        add_member_to_circle_room,
        remove_member_from_circle_room,
    )

    circle = instance.cycle.circle

    if instance.status == Enrollment.Status.ACTIVE:
        add_member_to_circle_room(
            circle=circle,
            user=instance.student,
            role_in_room="student",
        )

    elif instance.status in [
        Enrollment.Status.WITHDRAWN,
        Enrollment.Status.COMPLETED,
    ]:
        remove_member_from_circle_room(
            circle=circle,
            user=instance.student,
        )
