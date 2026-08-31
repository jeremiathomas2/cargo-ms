from django.contrib import admin

from .models import CarbonEmission, DriverScorecard, FuelLog, VehicleMaintenance


@admin.register(DriverScorecard)
class DriverScorecardAdmin(admin.ModelAdmin):
    list_display = (
        "driver",
        "period_start",
        "period_end",
        "total_score",
        "speeding_events",
        "harsh_braking_events",
        "on_time_deliveries",
        "total_deliveries",
        "total_km",
        "fuel_consumed_l",
        "fuel_cost",
    )
    list_filter = ("period_start", "period_end")
    search_fields = ("driver__first_name", "driver__last_name")


@admin.register(VehicleMaintenance)
class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "maintenance_type",
        "description",
        "mileage_at_service",
        "next_service_km",
        "next_service_date",
        "cost",
        "status",
        "created_at",
    )
    list_filter = ("maintenance_type", "status")
    search_fields = ("vehicle__plate_number", "description", "performed_by")


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "date",
        "odometer_km",
        "fuel_liters",
        "fuel_cost",
        "price_per_liter",
        "station",
        "created_by",
    )
    list_filter = ("date",)
    search_fields = ("vehicle__plate_number", "station")


@admin.register(CarbonEmission)
class CarbonEmissionAdmin(admin.ModelAdmin):
    list_display = (
        "shipment",
        "trip",
        "vehicle",
        "distance_km",
        "fuel_consumed_l",
        "emission_factor",
        "total_emissions_kg",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("shipment__tracking_number", "trip__trip_number")
