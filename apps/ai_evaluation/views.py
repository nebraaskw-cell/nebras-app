from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.core.permissions import IsAdminOrTeacher
from apps.study_sessions.models import Session

from .models import Evaluation

from .models import Evaluation
from .serializers import EvaluationRequestSerializer
from .services.evaluation_service import evaluate_transcript


class EvaluationAPIView(APIView):
    permission_classes = [IsAdminOrTeacher]  # Only teachers/admins can evaluate

    def post(self, request):
        serializer = EvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate student and session
        try:
            student = User.objects.get(
                pk=serializer.validated_data["student_id"],
                role=User.Roles.STUDENT,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Student not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            session = Session.objects.get(pk=serializer.validated_data["session_id"])
        except Session.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if teacher is assigned to the circle
        if (
            request.user.role == User.Roles.TEACHER
            and session.cycle.circle.teacher != request.user
        ):
            return Response(
                {"detail": "You can only evaluate students in your assigned circle."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get evaluation result
        result = evaluate_transcript(serializer.validated_data["transcript"])

        # Create evaluation record
        evaluation = Evaluation.objects.create(
            student=student,
            session=session,
            evaluation_type=serializer.validated_data["evaluation_type"],
            score=result["score"],
            feedback=result["feedback"],
            evaluated_by=request.user,
        )

        return Response({
            "evaluation_id": evaluation.id,
            "score": evaluation.score,
            "feedback": evaluation.feedback,
        }, status=status.HTTP_201_CREATED)

