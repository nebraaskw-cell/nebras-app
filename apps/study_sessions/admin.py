from django.contrib import admin, messages

from .models import Session
from .services import session_service


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("cycle", "date", "status", "start_time", "end_time", "is_auto_generated")
    list_filter = ("status", "is_auto_generated", "cycle__circle__gender", "cycle__circle__governorate")
    search_fields = ("title", "cycle__title", "cycle__circle__name", "cycle__circle__name_ar")
    autocomplete_fields = ("cycle",)
    actions = ("auto_generate_sessions_for_selected_cycles",)

    @admin.action(description="Auto-generate sessions for selected cycles")
    def auto_generate_sessions_for_selected_cycles(self, request, queryset):
        cycles = {session.cycle for session in queryset.select_related("cycle")}
        created_count = sum(session_service.generate_sessions_for_cycle(cycle) for cycle in cycles)
        self.message_user(request, f"{created_count} session(s) generated.", messages.SUCCESS)
