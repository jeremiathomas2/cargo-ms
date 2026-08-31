from django.contrib import admin

from .models import (
    AnomalyDetection,
    DemandForecast,
    ETAProjection,
    PricingRecommendation,
    RouteOptimization,
)


@admin.register(ETAProjection)
class ETAProjectionAdmin(admin.ModelAdmin):
    list_display = ("shipment", "predicted_arrival", "model_version", "created_at")
    list_filter = ("model_version", "created_at")
    search_fields = ("shipment__tracking_number",)


@admin.register(RouteOptimization)
class RouteOptimizationAdmin(admin.ModelAdmin):
    list_display = (
        "trip",
        "estimated_savings_km",
        "estimated_savings_hours",
        "fuel_savings",
        "is_applied",
        "created_at",
    )
    list_filter = ("is_applied", "created_at")
    search_fields = ("trip__trip_number",)


@admin.register(AnomalyDetection)
class AnomalyDetectionAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "anomaly_type",
        "severity",
        "detected_at",
        "acknowledged",
        "acknowledged_by",
    )
    list_filter = ("anomaly_type", "severity", "acknowledged", "detected_at")
    search_fields = ("device__tracker_id", "description")


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ("route", "forecast_date", "predicted_volume", "confidence", "model_version", "created_at")
    list_filter = ("model_version", "forecast_date")
    search_fields = ("route__route_name",)


@admin.register(PricingRecommendation)
class PricingRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "suggested_rate",
        "current_rate",
        "is_approved",
        "approved_by",
        "created_at",
    )
    list_filter = ("is_approved", "created_at")
    search_fields = ("route__route_name",)
