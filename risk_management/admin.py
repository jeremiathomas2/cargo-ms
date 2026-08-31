from django.contrib import admin

from .models import RiskScore, SLABreach, SLALevel, Watchlist


@admin.register(SLALevel)
class SLALevelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "target_transit_hours",
        "max_transit_hours",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(SLABreach)
class SLABreachAdmin(admin.ModelAdmin):
    list_display = (
        "shipment",
        "sla_level",
        "expected_arrival",
        "actual_arrival",
        "breach_duration_hours",
        "severity",
        "escalated",
        "resolved",
        "resolved_at",
        "created_at",
    )
    list_filter = ("severity", "escalated", "resolved", "created_at")
    search_fields = ("shipment__tracking_number",)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = (
        "entity_type",
        "entity_value",
        "reason",
        "added_by",
        "is_active",
        "added_at",
        "expires_at",
    )
    list_filter = ("entity_type", "is_active", "added_at")
    search_fields = ("entity_value", "reason")


@admin.register(RiskScore)
class RiskScoreAdmin(admin.ModelAdmin):
    list_display = (
        "shipment",
        "risk_score",
        "reviewed",
        "reviewed_by",
        "reviewed_at",
        "created_at",
    )
    list_filter = ("reviewed", "created_at")
    search_fields = ("shipment__tracking_number",)
