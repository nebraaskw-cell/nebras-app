from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import EvaluationRequestSerializer
from .services.evaluation_service import evaluate_transcript


class EvaluationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = evaluate_transcript(serializer.validated_data["transcript"])
        return Response(result, status=status.HTTP_200_OK)

