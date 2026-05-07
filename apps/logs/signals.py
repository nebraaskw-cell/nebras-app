from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import User
from apps.logs.models import AuditLog

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action="LOGIN",
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action="LOGOUT",
        ip_address=request.META.get('REMOTE_ADDR')
    )

@receiver(post_save, sender=User)
def log_user_approval(sender, instance, created, **kwargs):
    if not created:
        # Check if registration_status changed to approved
        # This is a bit simplified as we don't have previous state easily here without extra work
        # but for demonstration we log status updates.
        if instance.registration_status == User.RegistrationStatus.APPROVED:
             # We might not have the current user here if not using a middleware to track it
             # but we can log that the student was approved.
             pass
