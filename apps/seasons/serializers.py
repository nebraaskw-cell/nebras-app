from rest_framework import serializers
from apps.seasons.models import Season, SeasonCircle, Enrollment


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            "id",
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
        read_only_fields = ["id", "archived_at", "created_at", "updated_at"]


class SeasonCircleSerializer(serializers.ModelSerializer):
    circle_name = serializers.CharField(source="circle.name_ar", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.full_name", read_only=True, default=None)

    class Meta:
        model = SeasonCircle
        fields = [
            "id",
            "season",
            "circle",
            "circle_name",
            "supervisor",
            "supervisor_name",
            "capacity",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    season_title = serializers.CharField(source="season.title", read_only=True)
    circle_name = serializers.CharField(source="season_circle.circle.name_ar", read_only=True, default=None)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_name",
            "season",
            "season_title",
            "season_circle",
            "circle_name",
            "enrolled_at",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "withdrawn_by",
            "withdrawn_at",
            "removal_reason",
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
            "removal_reason",
            "created_at",
            "updated_at",
        ]


class EnrollStudentInSeasonSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    season_id = serializers.IntegerField()


class AssignCircleToEnrollmentSerializer(serializers.Serializer):
    season_circle_id = serializers.IntegerField()


class StudentEnrollInSeasonSerializer(serializers.Serializer):
    season_id = serializers.IntegerField()


class RemoveEnrollmentSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
