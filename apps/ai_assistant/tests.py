from django.test import TestCase

from apps.ai_assistant.services.assistant_service import generate_guidance


class AssistantServiceTests(TestCase):
    def test_generate_guidance_returns_stub_payload(self):
        payload = generate_guidance("اختبار")
        self.assertIn("response", payload)
        self.assertEqual(payload["provider"], "stub")
