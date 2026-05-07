from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatRoom, ChatMessage, ChatMembership
from .serializers import ChatRoomSerializer, ChatMessageSerializer


class ChatRoomListAPIView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can see global chat and circle chats they are members of
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(type=ChatRoom.Type.GLOBAL) | 
            Q(memberships__user=user)
        ).distinct()


class ChatMessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs.get('room_pk')
        user = self.request.user
        
        # Security: check if user has access to room
        room = generics.get_object_or_404(ChatRoom, pk=room_id)
        if room.type != ChatRoom.Type.GLOBAL:
            if not ChatMembership.objects.filter(room=room, user=user).exists():
                return ChatMessage.objects.none()
                
        queryset = ChatMessage.objects.filter(room_id=room_id, is_deleted=False)
        
        # Support for polling (fetch only messages after a certain ID)
        after_id = self.request.query_params.get('after_id')
        if after_id:
            queryset = queryset.filter(id__gt=after_id)
            
        return queryset.order_by('created_at')

    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_pk')
        room = generics.get_object_or_404(ChatRoom, pk=room_id)
        
        # Check permission to post
        if room.type != ChatRoom.Type.GLOBAL:
            if not ChatMembership.objects.filter(room=room, user=self.request.user).exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You are not a member of this chat room.")
                
        serializer.save(sender=self.request.user, room=room)
