from django.db import models
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.core.permissions import IsAdminOrTeacher, IsApprovedUser, IsStudentRole, ReadOnlyOrAdminRole
from apps.seasons.models import Season, SeasonCircle, Enrollment
from apps.seasons.selectors import seasons_selector
from apps.seasons.serializers import (
    SeasonSerializer,
    SeasonCircleSerializer,
    EnrollmentSerializer,
    EnrollStudentInSeasonSerializer,
    AssignCircleToEnrollmentSerializer,
    StudentEnrollInSeasonSerializer,
    RemoveEnrollmentSerializer,
)
from apps.seasons.services import enrollment_service
from apps.seasons.services.season_archive_service import archive_season


class SeasonViewSet(viewsets.ModelViewSet):
    serializer_class = SeasonSerializer
    permission_classes = [ReadOnlyOrAdminRole]
    filterset_fields = ["status", "start_date", "end_date"]
    search_fields = ["title"]
    ordering_fields = ["start_date", "end_date", "status", "created_at"]

    def get_queryset(self):
        queryset = seasons_selector.get_seasons()
        user = self.request.user
        if user.is_authenticated and user.role == User.Roles.STUDENT:
            queryset = queryset.filter(status__in=[Season.Status.ACTIVE, Season.Status.REGISTRATION_OPEN])
        return queryset

    @action(detail=True, methods=["post"], permission_classes=[ReadOnlyOrAdminRole])
    def archive(self, request, pk=None):
        """Archive a season, transitioning CLOSED -> ARCHIVED, generating a comprehensive JSON snapshot."""
        season = self.get_object()

        if not request.user.is_admin_role:
            return Response({"detail": "Only admins can archive seasons."}, status=status.HTTP_403_FORBIDDEN)

        try:
            archive_season(season, request.user)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(SeasonSerializer(season).data)


class SeasonCircleViewSet(viewsets.ModelViewSet):
    serializer_class = SeasonCircleSerializer
    permission_classes = [ReadOnlyOrAdminRole]
    filterset_fields = ["season", "circle", "supervisor"]
    search_fields = ["circle__name", "circle__name_ar", "supervisor__first_name", "supervisor__last_name"]
    ordering_fields = ["season", "circle", "capacity", "created_at"]

    def get_queryset(self):
        return SeasonCircle.objects.all().select_related("season", "circle", "supervisor")


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ["season", "season_circle", "student", "status"]
    search_fields = [
        "student__username",
        "student__first_name",
        "student__last_name",
        "season__title",
        "season_circle__circle__name_ar",
    ]
    ordering_fields = ["enrolled_at", "status", "created_at"]

    def get_queryset(self):
        return Enrollment.objects.all().select_related(
            "student", "season", "season_circle", "season_circle__circle", "approved_by"
        )

    def create(self, request, *args, **kwargs):
        """Admin/Teacher registers a student in a season first."""
        serializer = EnrollStudentInSeasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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
            season = Season.objects.get(pk=serializer.validated_data["season_id"])
        except Season.DoesNotExist:
            return Response(
                {"detail": "Season not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            enrollment = enrollment_service.enroll_student_in_season(
                student=student,
                season=season,
                enrolled_by=request.user,
            )
        except (ValueError, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    def _assert_teacher_manages_enrollment(self, enrollment, user):
        if user.role != User.Roles.TEACHER:
            return
        if enrollment.season_circle and enrollment.season_circle.supervisor != user:
            raise ValueError(
                "You can only manage enrollments for your assigned circle."
            )

    @action(detail=True, methods=["post"])
    def assign_circle(self, request, pk=None):
        """Assign a circle to a season enrollment."""
        enrollment = self.get_object()
        serializer = AssignCircleToEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            season_circle = SeasonCircle.objects.get(pk=serializer.validated_data["season_circle_id"])
        except SeasonCircle.DoesNotExist:
            return Response(
                {"detail": "SeasonCircle not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == User.Roles.TEACHER and season_circle.supervisor != request.user:
            return Response(
                {"detail": "You can only assign students to your supervised circle."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            enrollment_service.assign_circle_to_enrollment(
                enrollment=enrollment,
                season_circle=season_circle,
                assigned_by=request.user,
            )
        except (ValueError, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Transition enrollment PENDING → ACTIVE."""
        enrollment = self.get_object()
        try:
            self._assert_teacher_manages_enrollment(enrollment, request.user)
            enrollment_service.approve_enrollment(enrollment, approved_by=request.user)
        except (ValueError, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        """Transition enrollment to WITHDRAWN."""
        enrollment = self.get_object()
        try:
            self._assert_teacher_manages_enrollment(enrollment, request.user)
            enrollment_service.withdraw_enrollment(enrollment, withdrawn_by=request.user)
        except (ValueError, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=["post"])
    def remove(self, request, pk=None):
        """Remove a student from enrollment with reason. Admin/teacher only."""
        enrollment = self.get_object()
        serializer = RemoveEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self._assert_teacher_manages_enrollment(enrollment, request.user)
            enrollment_service.remove_enrollment(
                enrollment=enrollment,
                removed_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except (ValueError, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=False, methods=["post"], permission_classes=[IsApprovedUser, IsStudentRole])
    def student_enroll(self, request):
        """Step 1: Students can enroll themselves in an open season."""
        serializer = StudentEnrollInSeasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            season = Season.objects.get(pk=serializer.validated_data["season_id"])
        except Season.DoesNotExist:
            return Response(
                {"detail": "Season not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            enrollment = enrollment_service.enroll_student_in_season(
                student=request.user,
                season=season,
                enrolled_by=request.user,
            )
        except (ValueError, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsApprovedUser, IsStudentRole])
    def student_select_circle(self, request, pk=None):
        """Step 2: Students can choose their circle in their enrolled season."""
        enrollment = self.get_object()

        if enrollment.student != request.user:
            return Response(
                {"detail": "You can only select circle for your own enrollment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssignCircleToEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            season_circle = SeasonCircle.objects.get(pk=serializer.validated_data["season_circle_id"])
        except SeasonCircle.DoesNotExist:
            return Response(
                {"detail": "SeasonCircle not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            enrollment_service.assign_circle_to_enrollment(
                enrollment=enrollment,
                season_circle=season_circle,
                assigned_by=request.user,
            )
        except (ValueError, ValidationError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(EnrollmentSerializer(enrollment).data)
