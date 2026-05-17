from django.contrib import admin

from .models import Certificate, Course, CourseEnrollment, CourseModule, Lesson, LessonCompletion, ModuleCompletion


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title_ar", "teacher", "status", "capacity", "enrollment_mode", "created_at"]
    list_filter = ["status", "enrollment_mode", "is_islamic_content", "teacher"]
    search_fields = ["title", "title_ar", "description"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ["course", "sequence_order", "title_ar", "is_required", "duration_hours"]
    list_filter = ["is_required", "course"]
    search_fields = ["title", "title_ar", "course__title_ar"]
    ordering = ["course", "sequence_order"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["module", "sequence_order", "title_ar", "duration_minutes", "has_quiz"]
    list_filter = ["has_quiz", "module__course"]
    search_fields = ["title", "title_ar", "module__title_ar"]
    ordering = ["module", "sequence_order"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "status", "enrolled_at", "progress_percent"]
    list_filter = ["status", "course", "enrolled_at"]
    search_fields = ["student__username", "student__first_name", "student__last_name", "course__title_ar"]
    ordering = ["-enrolled_at"]
    readonly_fields = ["enrolled_at", "approved_at", "completion_date", "created_at", "updated_at"]


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ["student", "lesson", "completed_at", "quiz_score"]
    list_filter = ["completed_at", "lesson__module__course"]
    search_fields = ["student__username", "lesson__title_ar"]
    ordering = ["-completed_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ModuleCompletion)
class ModuleCompletionAdmin(admin.ModelAdmin):
    list_display = ["student", "module", "status", "completed_at"]
    list_filter = ["status", "module__course"]
    search_fields = ["student__username", "module__title_ar"]
    ordering = ["-completed_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "certificate_code", "issued_date", "is_issued"]
    list_filter = ["is_issued", "issued_date", "course"]
    search_fields = ["student__username", "course__title_ar", "certificate_code"]
    ordering = ["-issued_date"]
    readonly_fields = ["issued_date", "created_at", "updated_at"]
