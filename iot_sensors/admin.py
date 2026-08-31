from django.contrib import admin

from .models import DigitalSeal, SensorAlert, SensorDevice, SensorReading


@admin.register(SensorDevice)
class SensorDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "tracker_id",
        "sensor_type",
        "serial_number",
        "is_active",
        "battery_level",
        "last_update",
        "created_at",
    )
    list_filter = ("sensor_type", "is_active")
    search_fields = ("tracker_id", "serial_number")


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = (
        "sensor",
        "temperature",
        "humidity",
        "shock_level",
        "door_open",
        "latitude",
        "longitude",
        "timestamp",
    )
    list_filter = ("sensor__sensor_type", "timestamp")
    search_fields = ("sensor__tracker_id",)


@admin.register(SensorAlert)
class SensorAlertAdmin(admin.ModelAdmin):
    list_display = (
        "sensor",
        "alert_type",
        "severity",
        "message",
        "acknowledged",
        "acknowledged_by",
        "created_at",
    )
    list_filter = ("alert_type", "severity", "acknowledged", "created_at")
    search_fields = ("sensor__tracker_id", "message")


@admin.register(DigitalSeal)
class DigitalSealAdmin(admin.ModelAdmin):
    list_display = (
        "seal_id",
        "shipment",
        "status",
        "applied_by",
        "verified_by",
        "applied_at",
        "verified_at",
    )
    list_filter = ("status", "applied_at")
    search_fields = ("seal_id", "shipment__tracking_number")
