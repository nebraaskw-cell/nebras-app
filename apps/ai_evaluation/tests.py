from unittest.mock import patch, MagicMock
from django.test import TestCase

from apps.ai_evaluation.services.evaluation_service import evaluate_transcript


class EvaluationServiceTests(TestCase):
    @patch('apps.ai_evaluation.services.evaluation_service.os.getenv')
    @patch('apps.ai_evaluation.services.evaluation_service.OpenAI')
    def test_evaluate_transcript_success(self, mock_openai, mock_getenv):
        mock_getenv.return_value = 'fake_key'
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'تقييم جيد'
        mock_client.chat.completions.create.return_value = mock_response

        payload = evaluate_transcript("sample transcript")
        self.assertIn("score", payload)
        self.assertIn("feedback", payload)
        self.assertEqual(payload["feedback"], "تقييم جيد")

    @patch('apps.ai_evaluation.services.evaluation_service.os.getenv')
    @patch('apps.ai_evaluation.services.evaluation_service.OpenAI')
    def test_evaluate_transcript_error(self, mock_openai, mock_getenv):
        mock_getenv.return_value = 'fake_key'
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        payload = evaluate_transcript("sample transcript")
        self.assertIn("score", payload)
        self.assertIn("feedback", payload)
        self.assertEqual(payload["score"], 50)
        self.assertIn("خطأ", payload["feedback"])
