from django.urls import path
from .views import ChatRoomListAPIView, ChatMessageListCreateAPIView

urlpatterns = [
    path("rooms/", ChatRoomListAPIView.as_view(), name="room-list"),
    path("rooms/<int:room_pk>/messages/", ChatMessageListCreateAPIView.as_view(), name="message-list-create"),
]
