from django.contrib import admin

from .models import IVRCall, OfflineSyncQueue, Translation, USSDSession


@admin.register(USSDSession)
class USSDSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "phone_number", "tracking_number", "status", "created_at", "expires_at")
    list_filter = ("status", "created_at")
    search_fields = ("session_id", "phone_number", "tracking_number")


@admin.register(IVRCall)
class IVRCallAdmin(admin.ModelAdmin):
    list_display = ("call_id", "phone_number", "tracking_number", "duration_seconds", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("call_id", "phone_number", "tracking_number")


@admin.register(OfflineSyncQueue)
class OfflineSyncQueueAdmin(admin.ModelAdmin):
    list_display = ("device_id", "user", "action_type", "synced", "synced_at", "created_at")
    list_filter = ("synced", "action_type", "created_at")
    search_fields = ("device_id", "user__email")


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ("language_code", "key", "value", "context", "created_at", "updated_at")
    list_filter = ("language_code",)
    search_fields = ("key", "value")
