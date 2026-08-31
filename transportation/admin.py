from django.contrib import admin
from .models import Vehicle, Driver, Route, RouteStop, Trip, Manifest, ManifestShipment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'vehicle_type', 'make', 'model_name', 'year', 'status', 'assigned_branch', 'total_km', 'total_trips', 'is_active')
    list_filter = ('vehicle_type', 'status', 'is_active', 'assigned_branch', 'organization')
    search_fields = ('registration_number', 'make', 'model_name')
    readonly_fields = ('total_km', 'total_trips', 'created_at', 'updated_at')
    raw_id_fields = ('organization', 'assigned_branch', 'gps_device')
    fieldsets = (
        (None, {'fields': ('registration_number', 'vehicle_type', 'organization')}),
        ('Vehicle Info', {'fields': ('make', 'model_name', 'year', 'color')}),
        ('Capacity', {'fields': ('max_capacity_kg', 'max_volume_m3', 'fuel_capacity')}),
        ('Status', {'fields': ('status', 'assigned_branch', 'gps_device', 'is_active')}),
        ('Compliance', {'fields': ('insurance_expiry', 'inspection_expiry')}),
        ('Statistics', {'fields': ('total_km', 'total_trips')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'phone', 'license_number', 'license_expiry', 'status', 'assigned_vehicle', 'rating', 'is_active')
    list_filter = ('status', 'is_active', 'assigned_branch', 'organization')
    search_fields = ('employee_id', 'first_name', 'last_name', 'phone', 'email', 'license_number')
    readonly_fields = ('total_trips', 'total_km', 'created_at', 'updated_at')
    raw_id_fields = ('organization', 'user', 'assigned_vehicle', 'assigned_branch')
    fieldsets = (
        (None, {'fields': ('employee_id', 'user', 'organization')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'email')}),
        ('License', {'fields': ('license_number', 'license_expiry', 'license_class')}),
        ('Assignment', {'fields': ('status', 'assigned_vehicle', 'assigned_branch', 'is_active')}),
        ('Statistics', {'fields': ('total_trips', 'total_km', 'rating')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 0
    fields = ('name', 'sequence', 'latitude', 'longitude', 'estimated_arrival_minutes')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'route_type', 'corridor', 'origin', 'destination', 'distance_km', 'estimated_duration_hours', 'base_price', 'is_active')
    list_filter = ('route_type', 'is_active')
    search_fields = ('name', 'code', 'corridor', 'origin', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RouteStopInline]


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'sequence', 'latitude', 'longitude', 'estimated_arrival_minutes')
    list_filter = ('route',)
    search_fields = ('name',)
    readonly_fields = ('created_at',)


class ManifestShipmentInline(admin.TabularInline):
    model = ManifestShipment
    extra = 0
    fields = ('shipment', 'position', 'loaded_at', 'loaded_by', 'unloaded_at', 'unloaded_by')
    raw_id_fields = ('shipment', 'loaded_by', 'unloaded_by')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('trip_number', 'vehicle', 'driver', 'route', 'status', 'departure_time', 'estimated_arrival', 'actual_arrival', 'num_shipments', 'created_at')
    list_filter = ('status', 'route', 'vehicle', 'created_at')
    search_fields = ('trip_number', 'notes')
    readonly_fields = ('trip_number', 'created_at', 'updated_at')
    raw_id_fields = ('vehicle', 'driver', 'route', 'manifest', 'gps_device', 'created_by')
    fieldsets = (
        (None, {'fields': ('trip_number', 'vehicle', 'driver', 'route', 'manifest')}),
        ('Tracking', {'fields': ('gps_device', 'status')}),
        ('Schedule', {'fields': ('departure_time', 'estimated_arrival', 'actual_arrival')}),
        ('Statistics', {'fields': ('actual_distance_km', 'total_weight_kg', 'num_shipments')}),
        ('Other', {'fields': ('notes', 'created_by')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('manifest_number', 'vehicle', 'driver', 'origin', 'destination', 'status', 'total_shipments', 'total_packages', 'total_weight_kg', 'created_at')
    list_filter = ('status', 'vehicle', 'created_at')
    search_fields = ('manifest_number', 'origin', 'destination')
    readonly_fields = ('manifest_number', 'created_at', 'updated_at')
    raw_id_fields = ('trip', 'vehicle', 'driver', 'locked_by', 'created_by')
    inlines = [ManifestShipmentInline]
    fieldsets = (
        (None, {'fields': ('manifest_number', 'trip', 'vehicle', 'driver')}),
        ('Route', {'fields': ('origin', 'destination')}),
        ('Status', {'fields': ('status', 'locked_at', 'locked_by', 'dispatched_at')}),
        ('Totals', {'fields': ('total_shipments', 'total_packages', 'total_weight_kg', 'total_volume_m3')}),
        ('Other', {'fields': ('created_by',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ManifestShipment)
class ManifestShipmentAdmin(admin.ModelAdmin):
    list_display = ('manifest', 'shipment', 'position', 'loaded_at', 'loaded_by', 'unloaded_at', 'unloaded_by', 'created_at')
    list_filter = ('manifest', 'created_at')
    search_fields = ('manifest__manifest_number', 'shipment__tracking_id')
    readonly_fields = ('created_at',)
    raw_id_fields = ('manifest', 'shipment', 'loaded_by', 'unloaded_by')
