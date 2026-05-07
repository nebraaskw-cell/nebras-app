from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.circles.models import Cycle, Enrollment
from apps.study_sessions.models import Session


@receiver(post_save, sender=Cycle)
def on_active_cycle_saved(sender, instance, created, **kwargs):
    if instance.status == Cycle.Status.ACTIVE:
        from apps.study_sessions.services.session_service import generate_sessions_for_cycle

        generate_sessions_for_cycle(instance)


@receiver(post_save, sender=Session)
def on_session_activated(sender, instance, created, **kwargs):
    """
    When a session becomes ACTIVE, notify all enrolled students
    in that cycle.
    """
    if created:
        return
    if instance.status == "active":
        from apps.notifications.services.notification_service import notify

        enrollments = Enrollment.objects.filter(
            cycle=instance.cycle,
            status="active",
        ).select_related("student")
        for enrollment in enrollments:
            notify(
                recipient=enrollment.student,
                type="session_reminder",
                title="الجلسة بدأت الآن",
                body=f"جلسة {instance.cycle.circle.name_ar} بدأت. حضورك مهم.",
            )
