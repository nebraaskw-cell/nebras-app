from django.db import models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.models import User
from apps.core.permissions import IsAdminOrTeacher, IsApprovedUser, IsStudentRole

from .models import Certificate, Course, CourseEnrollment, CourseModule, Lesson, LessonCompletion, ModuleCompletion
from .serializers import (
    CertificateSerializer,
    CourseEnrollmentSerializer,
    CourseModuleSerializer,
    CourseSerializer,
    EnrollStudentSerializer,
    LessonCompletionSerializer,
    LessonSerializer,
    ModuleCompletionSerializer,
)
from .services import course_service, enrollment_service, progress_service, query_service


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]  # Allow browsing courses
    queryset = Course.objects.all()
    filterset_fields = ["status", "enrollment_mode", "is_islamic_content", "teacher"]
    search_fields = ["title", "title_ar", "description"]
    ordering_fields = ["created_at", "start_date", "title"]

    def get_queryset(self):
        queryset = query_service.get_courses()
        user = self.request.user

        # Students can only see active courses
        if user.is_authenticated and user.role == User.Roles.STUDENT:
            queryset = queryset.filter(status=Course.Status.ACTIVE)

        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], permission_classes=[IsStudentRole])
    def enroll(self, request, pk=None):
        """Student enrolls in a course."""
        course = self.get_object()
        student = request.user

        try:
            enrollment = enrollment_service.enroll_student(student, course)
            serializer = CourseEnrollmentSerializer(enrollment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], permission_classes=[IsApprovedUser])
    def progress(self, request, pk=None):
        """Get student's progress in this course."""
        course = self.get_object()
        student = request.user

        progress_data = progress_service.calculate_course_progress(student, course)
        return Response(progress_data)


class CourseModuleViewSet(viewsets.ModelViewSet):
    serializer_class = CourseModuleSerializer
    permission_classes = [AllowAny]
    queryset = CourseModule.objects.all()
    filterset_fields = ["course", "is_required"]
    search_fields = ["title", "title_ar"]
    ordering_fields = ["sequence_order", "title"]

    def get_queryset(self):
        return CourseModule.objects.select_related('course').prefetch_related('lessons')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return super().get_permissions()


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]
    queryset = Lesson.objects.all()
    filterset_fields = ["module", "has_quiz"]
    search_fields = ["title", "title_ar", "content"]
    ordering_fields = ["sequence_order", "title"]

    def get_queryset(self):
        return Lesson.objects.select_related('module', 'module__course')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], permission_classes=[IsStudentRole])
    def complete(self, request, pk=None):
        """Mark lesson as completed for the current student."""
        lesson = self.get_object()
        student = request.user

        time_spent = request.data.get('time_spent_seconds', 0)
        quiz_score = request.data.get('quiz_score')

        try:
            completion = progress_service.mark_lesson_complete(
                student, lesson, time_spent, quiz_score
            )
            serializer = LessonCompletionSerializer(completion)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAdminOrTeacher]
    queryset = CourseEnrollment.objects.all()
    filterset_fields = ["course", "student", "status"]
    search_fields = [
        "student__username",
        "student__first_name",
        "student__last_name",
        "course__title_ar",
    ]
    ordering_fields = ["enrolled_at", "status", "progress_percent"]

    def get_queryset(self):
        return query_service.get_course_enrollments()

    def create(self, request, *args, **kwargs):
        """Admin/teacher enrolls a student in a course."""
        serializer = EnrollStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student_id = serializer.validated_data['student_id']
        course_id = serializer.validated_data['course_id']

        try:
            student = User.objects.get(id=student_id, role=User.Roles.STUDENT)
            course = Course.objects.get(id=course_id)
            enrollment = enrollment_service.enroll_student(student, course, request.user)
            response_serializer = CourseEnrollmentSerializer(enrollment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrTeacher])
    def approve(self, request, pk=None):
        """Approve a pending enrollment."""
        enrollment = self.get_object()

        try:
            enrollment = enrollment_service.approve_enrollment(enrollment, request.user)
            serializer = CourseEnrollmentSerializer(enrollment)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrTeacher])
    def withdraw(self, request, pk=None):
        """Withdraw an enrollment."""
        enrollment = self.get_object()

        try:
            enrollment = enrollment_service.withdraw_enrollment(enrollment, request.user)
            serializer = CourseEnrollmentSerializer(enrollment)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrTeacher])
    def complete(self, request, pk=None):
        """Mark enrollment as completed."""
        enrollment = self.get_object()
        grade = request.data.get('grade')

        try:
            enrollment = enrollment_service.complete_enrollment(enrollment, grade)
            serializer = CourseEnrollmentSerializer(enrollment)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LessonCompletionViewSet(viewsets.ModelViewSet):
    serializer_class = LessonCompletionSerializer
    permission_classes = [IsApprovedUser]
    queryset = LessonCompletion.objects.all()
    filterset_fields = ["student", "lesson", "completed_at"]
    search_fields = ["lesson__title_ar"]
    ordering_fields = ["completed_at", "quiz_score"]

    def get_queryset(self):
        queryset = LessonCompletion.objects.select_related('student', 'lesson', 'lesson__module')
        user = self.request.user

        # Students can only see their own completions
        if user.role == User.Roles.STUDENT:
            queryset = queryset.filter(student=user)

        return queryset


class ModuleCompletionViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleCompletionSerializer
    permission_classes = [IsApprovedUser]
    queryset = ModuleCompletion.objects.all()
    filterset_fields = ["student", "module", "status"]
    search_fields = ["module__title_ar"]
    ordering_fields = ["completed_at", "status"]

    def get_queryset(self):
        queryset = ModuleCompletion.objects.select_related('student', 'module', 'module__course')
        user = self.request.user

        # Students can only see their own completions
        if user.role == User.Roles.STUDENT:
            queryset = queryset.filter(student=user)

        return queryset


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsApprovedUser]
    queryset = Certificate.objects.all()
    filterset_fields = ["student", "course", "is_issued"]
    search_fields = ["student__username", "course__title_ar", "certificate_code"]
    ordering_fields = ["issued_date"]

    def get_queryset(self):
        queryset = Certificate.objects.select_related('student', 'course', 'enrollment')
        user = self.request.user

        # Students can only see their own certificates
        if user.role == User.Roles.STUDENT:
            queryset = queryset.filter(student=user)

        return queryset
