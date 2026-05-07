from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer
from .services import notification_service


class NotificationListAPIView(generics.ListAPIView):
    """
    GET /api/v1/notifications/

    Returns paginated notifications for the authenticated user,
    ordered by most recent first.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["type", "is_read"]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by("-created_at")


class NotificationDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/v1/notifications/<id>/

    Retrieve a single notification. Owner only.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class MarkNotificationReadAPIView(APIView):
    """
    POST /api/v1/notifications/<id>/read/

    Marks a single notification as read. Owner only.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                pk=pk, recipient=request.user
            )
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        notification_service.mark_as_read(notification)
        return Response(NotificationSerializer(notification).data)


class MarkAllNotificationsReadAPIView(APIView):
    """
    POST /api/v1/notifications/mark-all-read/

    Marks all unread notifications for the authenticated user as read.
    Returns the count of notifications updated.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = notification_service.mark_all_read(request.user)
        return Response({"updated_count": count})


class UnreadCountAPIView(APIView):
    """
    GET /api/v1/notifications/unread-count/

    Returns the count of unread notifications for the authenticated user.
    Lightweight endpoint for badge counts in mobile/web UI.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"count": count})
