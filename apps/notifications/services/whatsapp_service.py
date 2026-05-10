import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def send_whatsapp_message(user, body, data=None):
    """
    WhatsApp gateway scaffold.

    Phase-ready integration point for a real provider such as Twilio,
    Meta WhatsApp Cloud API, or a Kuwait-approved messaging provider.
    Local development only logs the intent.
    """
    mode = getattr(settings, "WHATSAPP_PROVIDER", "log")
    phone_number = getattr(user, "phone_number", None)
    payload = data or {}

    if not phone_number:
        logger.info("WHATSAPP_SKIPPED | user=%s | reason=missing_phone", user.pk)
        return {"status": "skipped", "reason": "missing_phone"}

    if mode == "disabled":
        logger.info("WHATSAPP_DISABLED | user=%s | phone=%s", user.pk, phone_number)
        return {"status": "disabled"}

    logger.info(
        "WHATSAPP_LOG | user=%s | phone=%s | body=%s | data=%s",
        user.pk,
        phone_number,
        body,
        payload,
    )
    return {"status": "logged", "provider": "log"}


def send_student_approval_confirmation(user):
    """Send the student registration approval confirmation through WhatsApp."""
    return send_whatsapp_message(
        user=user,
        body=(
            "تم قبول طلب تسجيلك في منصة حلقات نبراس. "
            "يمكنك الآن تسجيل الدخول ومتابعة حلقتك."
        ),
        data={"event": "student_registration_approved"},
    )
