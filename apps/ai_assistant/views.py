from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AssistantPromptSerializer
from .services.assistant_service import generate_guidance


class AssistantPromptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssistantPromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = generate_guidance(serializer.validated_data["prompt"])
        return Response(result, status=status.HTTP_200_OK)

