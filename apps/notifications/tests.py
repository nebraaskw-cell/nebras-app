from django.test import TestCase, override_settings

from apps.accounts.models import User
from apps.notifications.services.push_service import send_push_notification


class PushServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notify-user",
            password="pass12345",
            role=User.Roles.STUDENT,
            registration_status=User.RegistrationStatus.APPROVED,
        )

    @override_settings(PUSH_PROVIDER="mock")
    def test_mock_provider_returns_sent_status(self):
        result = send_push_notification(self.user, "عنوان", "رسالة")
        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["provider"], "mock")
