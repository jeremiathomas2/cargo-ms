from django.contrib import admin

from .models import IntegrationLog, WebhookDelivery, WebhookSubscription


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "url",
        "organization",
        "is_active",
        "retry_count",
        "created_at",
    )
    list_filter = ("is_active", "organization")
    search_fields = ("url", "organization__name")


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "subscription",
        "event_type",
        "response_status",
        "delivered",
        "attempts",
        "next_retry_at",
        "created_at",
    )
    list_filter = ("delivered", "event_type", "created_at")
    search_fields = ("event_type",)


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = (
        "integration_name",
        "organization",
        "direction",
        "status",
        "error_message",
        "created_at",
    )
    list_filter = ("integration_name", "direction", "status", "created_at")
    search_fields = ("integration_name", "organization__name", "error_message")
