from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.circles.models import Circle


@receiver(post_save, sender=Circle)
def on_circle_created(sender, instance, created, **kwargs):
    """
    Circle creation hook.
    """
    return
