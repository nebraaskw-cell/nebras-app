from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "status", "marked_by", "marked_at")
    list_filter = ("status", "session__cycle__circle__gender", "session__cycle__circle__governorate")
    search_fields = ("student__username", "student__email", "session__title", "session__cycle__title")
    autocomplete_fields = ("session", "student", "marked_by")
