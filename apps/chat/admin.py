from django.contrib import admin

from apps.chat.models import ChatMembership, ChatMessage, ChatRoom


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ["type", "circle", "is_active", "created_at"]
    list_filter = ["type", "is_active"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        "sender", "room", "body_preview",
        "is_deleted", "created_at",
    ]
    list_filter = ["room", "is_deleted"]
    search_fields = ["sender__username", "body"]
    readonly_fields = ["created_at", "updated_at", "deleted_at", "deleted_by"]

    def body_preview(self, obj):
        return obj.body[:60]
    body_preview.short_description = "Message"


@admin.register(ChatMembership)
class ChatMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "room", "role_in_room", "joined_at"]
    list_filter = ["role_in_room", "room"]
    search_fields = ["user__username"]
