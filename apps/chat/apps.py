from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
    verbose_name = "Chat"

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_create_global_room, sender=self)


def _create_global_room(sender, **kwargs):
    """
    Creates the global chat room after migrations run.
    Uses post_migrate signal to avoid hitting DB during app startup.
    """
    try:
        from apps.chat.services.room_service import get_or_create_global_room
        get_or_create_global_room()
    except Exception:
        pass