from django.contrib import admin
from .models import GPSDevice, GPSPosition, GPSDeviceAssignment, Geofence, GeofenceEvent, GPSAlert


@admin.register(GPSDevice)
class GPSDeviceAdmin(admin.ModelAdmin):
    list_display = ('tracker_id', 'imei', 'device_type', 'status', 'battery_level', 'last_update', 'is_active')
    list_filter = ('status', 'device_type', 'is_active')
    search_fields = ('tracker_id', 'imei', 'serial_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GPSPosition)
class GPSPositionAdmin(admin.ModelAdmin):
    list_display = ('device', 'latitude', 'longitude', 'speed', 'heading', 'timestamp')
    list_filter = ('device',)
    search_fields = ('device__tracker_id',)
    readonly_fields = ('created_at',)
    ordering = ('-timestamp',)


@admin.register(GPSDeviceAssignment)
class GPSDeviceAssignmentAdmin(admin.ModelAdmin):
    list_display = ('device', 'assignment_type', 'is_active', 'assigned_at', 'unassigned_at')
    list_filter = ('assignment_type', 'is_active')
    search_fields = ('device__tracker_id',)
    readonly_fields = ('assigned_at',)


@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'fence_type', 'shape', 'radius_meters', 'is_active', 'alert_on_enter', 'alert_on_exit')
    list_filter = ('fence_type', 'shape', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GeofenceEvent)
class GeofenceEventAdmin(admin.ModelAdmin):
    list_display = ('device', 'geofence', 'event_type', 'latitude', 'longitude', 'timestamp')
    list_filter = ('event_type',)
    search_fields = ('device__tracker_id', 'geofence__name')
    readonly_fields = ('timestamp',)


@admin.register(GPSAlert)
class GPSAlertAdmin(admin.ModelAdmin):
    list_display = ('device', 'alert_type', 'severity', 'acknowledged', 'created_at')
    list_filter = ('alert_type', 'severity', 'acknowledged')
    search_fields = ('device__tracker_id', 'message')
    readonly_fields = ('created_at',)
