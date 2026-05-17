from django.contrib import admin
from apps.seasons.models import Season, SeasonCircle, Enrollment, SeasonSnapshot


class SeasonCircleInline(admin.TabularInline):
    model = SeasonCircle
    extra = 0
    autocomplete_fields = ("circle", "supervisor")


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "start_date",
        "end_date",
        "status",
        "default_session_start_time",
        "default_session_end_time",
        "archived_at",
    )
    list_filter = ("status", "start_date")
    search_fields = ("title", "notes")
    inlines = [SeasonCircleInline]
    readonly_fields = ("archived_at",)


@admin.register(SeasonCircle)
class SeasonCircleAdmin(admin.ModelAdmin):
    list_display = ("season", "circle", "supervisor", "capacity")
    list_filter = ("season", "circle__gender", "circle__governorate")
    search_fields = ("circle__name", "circle__name_ar", "supervisor__username")
    autocomplete_fields = ("season", "circle", "supervisor")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "season", "season_circle", "status", "enrolled_at", "approved_by")
    list_filter = ("status", "season", "season_circle__circle__gender", "season_circle__circle__governorate")
    search_fields = (
        "student__username",
        "student__email",
        "season__title",
        "season_circle__circle__name_ar",
    )
    autocomplete_fields = ("student", "season", "season_circle", "approved_by", "withdrawn_by")


@admin.register(SeasonSnapshot)
class SeasonSnapshotAdmin(admin.ModelAdmin):
    list_display = ("season", "created_at")
    readonly_fields = ("season", "data", "created_at")
