from rest_framework import serializers

from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    cycle_title = serializers.CharField(source="cycle.title", read_only=True)
    circle_name = serializers.CharField(source="cycle.circle.name_ar", read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "cycle",
            "cycle_title",
            "circle_name",
            "title",
            "date",
            "start_time",
            "end_time",
            "status",
            "started_at",
            "completed_at",
            "is_auto_generated",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "started_at",
            "completed_at",
            "is_auto_generated",
            "created_at",
            "updated_at",
        ]
