import logging
from django.conf import settings


logger = logging.getLogger(__name__)


def send_push_notification(user, title, body, data=None):
    """
    Push gateway with safe fallback modes.

    Modes:
    - "disabled": no-op
    - "log": log payload for development/testing
    - "mock": returns a deterministic mock delivery object
    """
    mode = getattr(settings, "PUSH_PROVIDER", "log")
    payload = data or {}

    if mode == "disabled":
        logger.info("PUSH_DISABLED | user=%s", user.pk)
        return {"status": "disabled"}

    if mode == "mock":
        logger.info("PUSH_MOCK | user=%s | title=%s", user.pk, title)
        return {"status": "sent", "provider": "mock", "message_id": f"mock-{user.pk}"}

    logger.info(
        "PUSH_LOG | user=%s | title=%s | body=%s | data=%s",
        user.pk,
        title,
        body,
        payload,
    )
    return {"status": "logged", "provider": "log"}
