from rest_framework import serializers

from .models import Certificate, Course, CourseEnrollment, CourseModule, Lesson, LessonCompletion, ModuleCompletion


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    modules_count = serializers.SerializerMethodField()
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'teacher', 'teacher_name', 'capacity', 'status', 'enrollment_mode',
            'start_date', 'end_date', 'is_islamic_content',
            'modules_count', 'enrollments_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_modules_count(self, obj):
        return obj.modules.count()

    def get_enrollments_count(self, obj):
        return obj.enrollments.filter(status='active').count()


class CourseModuleSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseModule
        fields = [
            'id', 'course', 'sequence_order', 'title', 'title_ar',
            'description', 'duration_hours', 'is_required',
            'lessons_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'sequence_order', 'title', 'title_ar',
            'content', 'duration_minutes', 'has_quiz',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title_ar', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student', 'student_name', 'course', 'course_title',
            'enrolled_at', 'status', 'approved_by', 'approved_by_name',
            'approved_at', 'completion_date', 'grade', 'progress_percent',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['enrolled_at', 'approved_at', 'completion_date', 'created_at', 'updated_at']


class EnrollStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()


class LessonCompletionSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title_ar', read_only=True)

    class Meta:
        model = LessonCompletion
        fields = [
            'id', 'student', 'lesson', 'lesson_title',
            'completed_at', 'time_spent_seconds', 'quiz_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ModuleCompletionSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title_ar', read_only=True)

    class Meta:
        model = ModuleCompletion
        fields = [
            'id', 'student', 'module', 'module_title',
            'completed_at', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title_ar', read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'enrollment', 'student', 'student_name',
            'course', 'course_title', 'issued_date',
            'certificate_code', 'is_issued',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['issued_date', 'created_at', 'updated_at']