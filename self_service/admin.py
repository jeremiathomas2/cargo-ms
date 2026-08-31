from django.contrib import admin

from .models import BulkBookingUpload, CorporateAPIKey, ShipmentTemplate


@admin.register(ShipmentTemplate)
class ShipmentTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "customer",
        "origin",
        "destination",
        "cargo_type",
        "is_recurring",
        "recurrence_interval",
        "created_at",
    )
    list_filter = ("cargo_type", "is_recurring", "recurrence_interval")
    search_fields = ("name", "origin", "destination", "customer__name")


@admin.register(CorporateAPIKey)
class CorporateAPIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "key_name",
        "customer",
        "is_active",
        "rate_limit",
        "total_requests",
        "last_request_at",
        "expires_at",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("key_name", "api_key", "customer__name")


@admin.register(BulkBookingUpload)
class BulkBookingUploadAdmin(admin.ModelAdmin):
    list_display = (
        "uploaded_by",
        "status",
        "total_rows",
        "processed_rows",
        "error_rows",
        "created_at",
        "completed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("uploaded_by__email",)
