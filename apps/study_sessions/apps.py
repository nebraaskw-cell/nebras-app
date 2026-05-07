from django.apps import AppConfig


class StudySessionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.study_sessions"
    label = "study_sessions"
    verbose_name = "Study Sessions"

    def ready(self):
        import apps.study_sessions.signals  # noqa: F401
