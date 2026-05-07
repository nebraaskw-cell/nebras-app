from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "type",
            "title",
            "body",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "recipient", "type", "title", "body", "created_at"]
