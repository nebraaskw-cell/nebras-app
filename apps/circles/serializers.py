from rest_framework import serializers

from .models import Circle, Cycle, Enrollment


class CircleSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = Circle
        fields = [
            "id",
            "name",
            "name_ar",
            "gender",
            "governorate",
            "mosque_name",
            "location_name",
            "capacity",
            "teacher",
            "teacher_name",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CycleSerializer(serializers.ModelSerializer):
    circle_name = serializers.CharField(source="circle.name_ar", read_only=True)

    class Meta:
        model = Cycle
        fields = [
            "id",
            "circle",
            "circle_name",
            "title",
            "start_date",
            "end_date",
            "status",
            "default_session_start_time",
            "default_session_end_time",
            "archived_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "end_date", "archived_at", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    cycle_title = serializers.CharField(source="cycle.title", read_only=True)
    circle_name = serializers.CharField(source="cycle.circle.name_ar", read_only=True)
    approved_by_name = serializers.CharField(
        source="approved_by.full_name", read_only=True, default=None
    )

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_name",
            "cycle",
            "cycle_title",
            "circle_name",
            "enrolled_at",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "withdrawn_by",
            "withdrawn_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "enrolled_at",
            "approved_by",
            "approved_at",
            "withdrawn_by",
            "withdrawn_at",
            "created_at",
            "updated_at",
        ]


class EnrollStudentSerializer(serializers.Serializer):
    """Write serializer for enrolling a student in a cycle."""

    student_id = serializers.IntegerField()
    cycle_id = serializers.IntegerField()


