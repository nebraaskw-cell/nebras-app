from django.test import TestCase

from apps.ai_evaluation.services.evaluation_service import evaluate_transcript


class EvaluationServiceTests(TestCase):
    def test_evaluate_transcript_returns_score_and_feedback(self):
        payload = evaluate_transcript("sample transcript")
        self.assertIn("score", payload)
        self.assertIn("feedback", payload)
        self.assertGreaterEqual(payload["score"], 40)
