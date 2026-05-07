from django.contrib import admin

from .models import Circle, Cycle, Enrollment


class CycleInline(admin.TabularInline):
    model = Cycle
    extra = 0
    fields = (
        "title",
        "start_date",
        "end_date",
        "status",
        "default_session_start_time",
        "default_session_end_time",
    )
    readonly_fields = ()


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ar", "gender", "governorate", "teacher", "is_active", "capacity")
    list_filter = ("gender", "governorate", "is_active")
    search_fields = ("name", "name_ar", "mosque_name", "location_name", "teacher__username")
    autocomplete_fields = ("teacher",)
    inlines = [CycleInline]


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ("title", "circle", "start_date", "end_date", "status", "archived_at")
    list_filter = ("status", "circle__gender", "circle__governorate")
    search_fields = ("title", "circle__name", "circle__name_ar")
    autocomplete_fields = ("circle",)
    readonly_fields = ("archived_at",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "cycle", "status", "enrolled_at", "approved_by")
    list_filter = ("status", "cycle__circle__gender", "cycle__circle__governorate")
    search_fields = ("student__username", "student__email", "cycle__title", "cycle__circle__name_ar")
    autocomplete_fields = ("student", "cycle", "approved_by")
