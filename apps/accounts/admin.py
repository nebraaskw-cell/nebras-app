from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import ParentProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username", "full_name", "role",
        "registration_status", "is_active", "date_joined",
    ]
    list_filter = ["role", "registration_status", "governorate", "gender"]
    search_fields = ["username", "email", "first_name", "last_name", "phone_number"]
    ordering = ["-date_joined"]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Platform Info", {
            "fields": (
                "role", "registration_status", "gender",
                "governorate", "phone_number",
                "approved_by", "approved_at",
            )
        }),
    )


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = [
        "parent", "student", "status",
        "requested_at", "approved_by", "approved_at",
    ]
    list_filter = ["status"]
    search_fields = ["parent__username", "student__username"]
    readonly_fields = ["requested_at", "approved_at"]
