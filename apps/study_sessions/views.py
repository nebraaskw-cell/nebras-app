from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrTeacher, IsAdminRole, IsTeacherRole

from .models import Session
from .serializers import SessionSerializer
from .services import session_service


class SessionViewSet(viewsets.ModelViewSet):
    """
    CRUD for study sessions.

    List/retrieve: admin or teacher.
    Create/update/delete: admin only (sessions are normally auto-generated).
    Start/complete: teacher of the circle only (admin also permitted).
    Cancel: admin or teacher.
    """

    serializer_class = SessionSerializer
    filterset_fields = ["cycle", "status", "date", "is_auto_generated"]
    search_fields = ["title", "cycle__title", "cycle__circle__name", "cycle__circle__name_ar"]
    ordering_fields = ["date", "start_time", "status", "created_at"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminRole()]
        return [IsAdminOrTeacher()]

    def get_queryset(self):
        return Session.objects.select_related(
            "cycle", "cycle__circle", "cycle__circle__teacher"
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrTeacher])
    def start(self, request, pk=None):
        """Transition session SCHEDULED → ACTIVE. Teacher or admin only."""
        session = self.get_object()
        try:
            session_service.start_session(session, started_by=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SessionSerializer(session).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrTeacher])
    def complete(self, request, pk=None):
        """Transition session ACTIVE → COMPLETED. Teacher or admin only."""
        session = self.get_object()
        try:
            session_service.complete_session(session, completed_by=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SessionSerializer(session).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrTeacher])
    def cancel(self, request, pk=None):
        """Transition SCHEDULED or ACTIVE → CANCELLED. Teacher or admin only."""
        session = self.get_object()
        try:
            session_service.cancel_session(session, cancelled_by=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SessionSerializer(session).data)
