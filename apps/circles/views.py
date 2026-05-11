from django.db import models
from django.views.generic import ListView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.core.permissions import IsAdminOrTeacher, IsApprovedUser, IsStudentRole, ReadOnlyOrAdminRole

from .models import Circle, Cycle, Enrollment
from .serializers import (
    CircleSerializer,
    CycleSerializer,
    EnrollmentSerializer,
    EnrollStudentSerializer,
    RemoveEnrollmentSerializer,
    StudentEnrollSerializer,
)
from .services import enrollment_service, query_service


class CircleListView(ListView):
    model = Circle
    template_name = "circles/list.html"
    context_object_name = "circles"
    paginate_by = 20

    def get_queryset(self):
        return query_service.get_active_circles().prefetch_related(
            models.Prefetch(
                'cycles',
                queryset=Cycle.objects.filter(status=Cycle.Status.ACTIVE),
                to_attr='active_cycles'
            )
        )


class CycleListView(ListView):
    model = Cycle
    template_name = "circles/cycles.html"
    context_object_name = "cycles"
    paginate_by = 20

    def get_queryset(self):
        queryset = query_service.get_cycles()
        user = self.request.user
        if user.is_authenticated and user.role == User.Roles.STUDENT:
            queryset = queryset.filter(status=Cycle.Status.ACTIVE)
        return queryset


class CircleViewSet(viewsets.ModelViewSet):
    serializer_class = CircleSerializer
    permission_classes = [ReadOnlyOrAdminRole]
    filterset_fields = ["gender", "governorate", "is_active"]
    search_fields = ["name", "name_ar", "mosque_name", "location_name"]
    ordering_fields = ["name", "governorate", "created_at"]

    def get_queryset(self):
        return query_service.get_circles()


class CycleViewSet(viewsets.ModelViewSet):
    serializer_class = CycleSerializer
    permission_classes = [ReadOnlyOrAdminRole]
    filterset_fields = ["circle", "status", "start_date", "end_date"]
    search_fields = ["title", "circle__name", "circle__name_ar"]
    ordering_fields = ["start_date", "end_date", "status", "created_at"]

    def get_queryset(self):
        queryset = query_service.get_cycles()
        user = self.request.user
        if user.is_authenticated and user.role == User.Roles.STUDENT:
            queryset = queryset.filter(status=Cycle.Status.ACTIVE)
        return queryset

    @action(detail=True, methods=["post"], permission_classes=[ReadOnlyOrAdminRole])
    def archive(self, request, pk=None):
        """Archive a cycle and complete its active enrollments."""
        from services.archiving import archive_cycle
        cycle = self.get_object()
        
        # Only admins should archive
        if not request.user.is_admin_role:
            return Response({"detail": "Only admins can archive cycles."}, status=status.HTTP_403_FORBIDDEN)
            
        archive_cycle(cycle, request.user)
        return Response(CycleSerializer(cycle).data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    Enrollment management — admin/teacher only.

    list/retrieve: view all enrollments with filters.
    create: enroll a student in a cycle via EnrollStudentSerializer.
    approve: POST {id}/approve/ — transition PENDING → ACTIVE.
    withdraw: POST {id}/withdraw/ — transition any → WITHDRAWN.
    """

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ["cycle", "student", "status"]
    search_fields = [
        "student__username",
        "student__first_name",
        "student__last_name",
        "cycle__title",
        "cycle__circle__name_ar",
    ]
    ordering_fields = ["enrolled_at", "status", "created_at"]

    def get_queryset(self):
        return Enrollment.objects.select_related(
            "student", "cycle", "cycle__circle", "approved_by"
        )

    def create(self, request, *args, **kwargs):
        """Enroll a student in a cycle. Admin/teacher only."""
        serializer = EnrollStudentSerializer(data=request.data)
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
            cycle = Cycle.objects.get(pk=serializer.validated_data["cycle_id"])
        except Cycle.DoesNotExist:
            return Response(
                {"detail": "Cycle not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            enrollment = enrollment_service.enroll_student(
                student=student,
                cycle=cycle,
                enrolled_by=request.user,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Transition enrollment PENDING → ACTIVE."""
        enrollment = self.get_object()
        try:
            enrollment_service.approve_enrollment(enrollment, approved_by=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        """Transition enrollment to WITHDRAWN."""
        enrollment = self.get_object()
        try:
            enrollment_service.withdraw_enrollment(enrollment, withdrawn_by=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EnrollmentSerializer(enrollment).data)

    @action(detail=False, methods=["post"], permission_classes=[IsApprovedUser, IsStudentRole])
    def student_enroll(self, request):
        """Students can enroll themselves in an active cycle."""
        serializer = StudentEnrollSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cycle = Cycle.objects.get(pk=serializer.validated_data["cycle_id"])
        except Cycle.DoesNotExist:
            return Response(
                {"detail": "Cycle not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            enrollment = enrollment_service.enroll_student(
                student=request.user,
                cycle=cycle,
                enrolled_by=request.user,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def remove(self, request, pk=None):
        """Remove a student from enrollment with reason. Admin/teacher only."""
        enrollment = self.get_object()
        serializer = RemoveEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if teacher is assigned to the circle
        if (
            request.user.role == User.Roles.TEACHER
            and enrollment.cycle.circle.teacher != request.user
        ):
            return Response(
                {"detail": "You can only remove students from your assigned circle."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            enrollment_service.remove_enrollment(
                enrollment=enrollment,
                removed_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EnrollmentSerializer(enrollment).data)

