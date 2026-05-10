from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.circles.models import Circle, Enrollment


@receiver(post_save, sender=Circle)
def on_circle_created(sender, instance, created, **kwargs):
    """
    Circle creation hook.

    Chat has been removed from the active application, so no circle-side
    membership work is performed here.
    """
    return


@receiver(post_save, sender=Enrollment)
def on_enrollment_status_changed(sender, instance, created, **kwargs):
    """
    Enrollment status hook.

    Chat has been removed from the active application, so no chat membership
    updates are performed on enrollment changes.
    """
    return
