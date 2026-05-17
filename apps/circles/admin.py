from django.contrib import admin

from .models import Circle


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ar", "gender", "start_date", "end_date", "status", "governorate", "teacher")
    list_filter = ("gender", "status", "governorate")
    search_fields = ("name", "name_ar", "teacher__username")
    autocomplete_fields = ("teacher",)
