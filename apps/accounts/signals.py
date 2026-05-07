from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def on_user_approved(sender, instance, created, **kwargs):
    """
    Sends an approval notification ONLY when registration_status
    explicitly transitions TO approved.

    Uses update_fields to guard against firing on every profile save.
    This means the caller (registration_service) MUST include
    'registration_status' in update_fields when approving a user.

    Does NOT fire on:
    - New user creation (created=True)
    - Profile updates that do not touch registration_status
    - Users whose status was already approved before the save
    """
    if created:
        return

    # Only proceed if registration_status was explicitly updated
    update_fields = kwargs.get("update_fields") or []
    if "registration_status" not in update_fields:
        return

    if instance.registration_status != User.RegistrationStatus.APPROVED:
        return

    # Lazy import to avoid circular dependency at app startup
    from apps.notifications.services.notification_service import notify

    notify(
        recipient=instance,
        type="approval",
        title="تم قبول تسجيلك",
        body=(
            "تم قبول طلب تسجيلك في منصة حلقات نبراس. "
            "يمكنك الآن تسجيل الدخول والانضمام إلى حلقتك."
        ),
    )
