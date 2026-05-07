from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    marked_by_name = serializers.CharField(source="marked_by.full_name", read_only=True, default=None)
    session_date = serializers.DateField(source="session.date", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "session",
            "session_date",
            "student",
            "student_name",
            "status",
            "marked_by",
            "marked_by_name",
            "marked_at",
            "notes",
        ]
        read_only_fields = ["id", "marked_by", "marked_at"]


class MarkAttendanceSerializer(serializers.Serializer):
    """Write serializer for marking a single student's attendance."""

    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=AttendanceRecord.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class BulkMarkAttendanceSerializer(serializers.Serializer):
    """Write serializer for marking attendance for multiple students at once."""

    records = MarkAttendanceSerializer(many=True)


class AttendanceSummarySerializer(serializers.Serializer):
    """Read-only serializer for session attendance summary."""

    total = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
