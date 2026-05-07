from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.core.permissions import IsAdminOrTeacher
from apps.study_sessions.models import Session

from .models import AttendanceRecord
from .serializers import (
    AttendanceSummarySerializer,
    AttendanceRecordSerializer,
    BulkMarkAttendanceSerializer,
    MarkAttendanceSerializer,
)
from .services import attendance_service


class AttendanceRecordViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Read-only viewset for attendance records.
    Admin and teachers can list/filter; students see their own.
    """

    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ["session", "student", "status"]
    search_fields = ["student__username", "student__first_name", "student__last_name"]
    ordering_fields = ["marked_at", "status"]

    def get_queryset(self):
        return AttendanceRecord.objects.select_related(
            "session", "student", "marked_by"
        )


class MarkAttendanceAPIView(APIView):
    """
    POST /api/v1/attendance/sessions/<session_id>/mark/

    Mark attendance for a single student in a session.
    Teacher of the circle or admin only.
    """

    permission_classes = [IsAdminOrTeacher]

    def post(self, request, session_id):
        serializer = MarkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            session = Session.objects.select_related(
                "cycle__circle__teacher"
            ).get(pk=session_id)
        except Session.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            student = User.objects.get(
                pk=serializer.validated_data["student_id"],
                role=User.Roles.STUDENT,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Student not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            record, created = attendance_service.mark_attendance(
                session=session,
                student=student,
                status=serializer.validated_data["status"],
                marked_by=request.user,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            AttendanceRecordSerializer(record).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class BulkMarkAttendanceAPIView(APIView):
    """
    POST /api/v1/attendance/sessions/<session_id>/bulk-mark/

    Mark attendance for multiple students in one request.
    Teacher of the circle or admin only.
    Partial success is allowed.
    """

    permission_classes = [IsAdminOrTeacher]

    def post(self, request, session_id):
        serializer = BulkMarkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            session = Session.objects.select_related(
                "cycle__circle__teacher"
            ).get(pk=session_id)
        except Session.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Resolve student IDs to User instances
        entries = []
        resolve_errors = []
        for entry in serializer.validated_data["records"]:
            try:
                student = User.objects.get(
                    pk=entry["student_id"],
                    role=User.Roles.STUDENT,
                )
                entries.append({"student": student, "status": entry["status"]})
            except User.DoesNotExist:
                resolve_errors.append({
                    "student_id": entry["student_id"],
                    "error": "Student not found.",
                })

        result = attendance_service.bulk_mark_attendance(
            session=session,
            records=entries,
            marked_by=request.user,
        )

        return Response({
            "success_count": len(result["success"]),
            "success": AttendanceRecordSerializer(result["success"], many=True).data,
            "errors": [
                {
                    "student": str(e.get("student", "")),
                    "error": e.get("error", ""),
                }
                for e in result["errors"]
            ] + resolve_errors,
        })


class SessionAttendanceSummaryAPIView(APIView):
    """
    GET /api/v1/attendance/sessions/<session_id>/summary/

    Returns attendance count summary for a session.
    """

    permission_classes = [IsAdminOrTeacher]

    def get(self, request, session_id):
        try:
            session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        summary = attendance_service.get_session_attendance_summary(session)
        serializer = AttendanceSummarySerializer(summary)
        return Response(serializer.data)
