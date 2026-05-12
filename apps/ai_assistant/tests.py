from unittest.mock import patch, MagicMock
from django.test import TestCase

from apps.ai_assistant.services.assistant_service import generate_guidance


class AssistantServiceTests(TestCase):
    @patch('apps.ai_assistant.services.assistant_service.os.getenv')
    @patch('apps.ai_assistant.services.assistant_service.OpenAI')
    def test_generate_guidance_success(self, mock_openai, mock_getenv):
        mock_getenv.return_value = 'fake_key'
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'إجابة تجريبية'
        mock_client.chat.completions.create.return_value = mock_response

        payload = generate_guidance("اختبار")
        self.assertIn("response", payload)
        self.assertEqual(payload["provider"], "openai")
        self.assertEqual(payload["response"], "إجابة تجريبية")

    @patch('apps.ai_assistant.services.assistant_service.os.getenv')
    @patch('apps.ai_assistant.services.assistant_service.OpenAI')
    def test_generate_guidance_error(self, mock_openai, mock_getenv):
        mock_getenv.return_value = 'fake_key'
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        payload = generate_guidance("اختبار")
        self.assertIn("response", payload)
        self.assertEqual(payload["provider"], "error")
        self.assertIn("خطأ", payload["response"])
