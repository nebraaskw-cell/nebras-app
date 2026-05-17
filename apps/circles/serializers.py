from rest_framework import serializers

from .models import Circle


class CircleSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = Circle
        fields = [
            "id",
            "name",
            "name_ar",
            "gender",
            "description",
            "start_date",
            "end_date",
            "status",
            "governorate",
            "teacher",
            "teacher_name",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
