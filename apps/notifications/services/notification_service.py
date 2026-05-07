from apps.notifications.models import Notification
from apps.notifications.services import push_service


def notify(recipient, type, title, body):
    """
    1. Creates a Notification record in DB.
    2. Calls push_service.send_push_notification() (stubbed).
    Returns the Notification instance.
    """
    notification = Notification.objects.create(
        recipient=recipient,
        type=type,
        title=title,
        body=body,
    )
    push_service.send_push_notification(
        user=recipient,
        title=title,
        body=body,
        data={"notification_id": notification.pk, "type": type},
    )
    return notification


def mark_as_read(notification):
    """Sets is_read=True."""
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return notification


def mark_all_read(user):
    """Marks all unread notifications for user as read."""
    return Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
