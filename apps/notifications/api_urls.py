from django.urls import path

from .views import (
    MarkAllNotificationsReadAPIView,
    MarkNotificationReadAPIView,
    NotificationDetailAPIView,
    NotificationListAPIView,
    UnreadCountAPIView,
)

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path("<int:pk>/", NotificationDetailAPIView.as_view(), name="notification-detail"),
    path("<int:pk>/read/", MarkNotificationReadAPIView.as_view(), name="notification-read"),
    path("mark-all-read/", MarkAllNotificationsReadAPIView.as_view(), name="notification-mark-all-read"),
    path("unread-count/", UnreadCountAPIView.as_view(), name="notification-unread-count"),
]
