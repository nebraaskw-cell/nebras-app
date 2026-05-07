from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatMembership
from apps.accounts.serializers import UserSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    circle_name = serializers.CharField(source='circle.name_ar', read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'type', 'circle', 'circle_name', 'is_active', 'created_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'sender_name', 'body', 'reply_to', 'created_at']
        read_only_fields = ['sender', 'created_at']
