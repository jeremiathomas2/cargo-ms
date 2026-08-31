from django.contrib import admin
from .models import Warehouse, WarehouseZone, WarehouseShelf, WarehouseBin, WarehouseMovement


class WarehouseZoneInline(admin.TabularInline):
    model = WarehouseZone
    extra = 0
    fields = ('name', 'code', 'zone_type', 'capacity', 'current_occupancy', 'is_active')


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'branch', 'capacity', 'current_occupancy', 'utilization_display', 'temperature_controlled', 'is_active')
    list_filter = ('is_active', 'temperature_controlled', 'branch', 'organization')
    search_fields = ('name', 'code', 'address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WarehouseZoneInline]
    fieldsets = (
        (None, {'fields': ('name', 'code', 'organization', 'branch', 'manager')}),
        ('Details', {'fields': ('address', 'latitude', 'longitude')}),
        ('Capacity', {'fields': ('capacity', 'current_occupancy')}),
        ('Settings', {'fields': ('temperature_controlled', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def utilization_display(self, obj):
        return f"{obj.utilization_percent:.1f}%"
    utilization_display.short_description = 'Utilization'


class WarehouseShelfInline(admin.TabularInline):
    model = WarehouseShelf
    extra = 0
    fields = ('name', 'code', 'max_bins', 'is_active')


@admin.register(WarehouseZone)
class WarehouseZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'warehouse', 'zone_type', 'capacity', 'current_occupancy', 'is_active')
    list_filter = ('zone_type', 'is_active', 'warehouse')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at',)
    inlines = [WarehouseShelfInline]


class WarehouseBinInline(admin.TabularInline):
    model = WarehouseBin
    extra = 0
    fields = ('name', 'code', 'max_capacity', 'current_occupancy', 'is_occupied', 'is_active')


@admin.register(WarehouseShelf)
class WarehouseShelfAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'zone', 'max_bins', 'is_active')
    list_filter = ('is_active', 'zone')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at',)
    inlines = [WarehouseBinInline]


@admin.register(WarehouseBin)
class WarehouseBinAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'shelf', 'max_capacity', 'current_occupancy', 'is_occupied', 'is_active')
    list_filter = ('is_active', 'is_occupied', 'shelf')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at',)


@admin.register(WarehouseMovement)
class WarehouseMovementAdmin(admin.ModelAdmin):
    list_display = ('id_short', 'movement_type', 'warehouse', 'shipment', 'package', 'from_zone', 'to_zone', 'scanned_by', 'created_at')
    list_filter = ('movement_type', 'warehouse', 'created_at')
    search_fields = ('notes', 'barcode_scan', 'shipment__tracking_id', 'package__tracking_id')
    readonly_fields = ('created_at',)
    raw_id_fields = ('shipment', 'package', 'warehouse', 'from_zone', 'from_shelf', 'from_bin', 'to_zone', 'to_shelf', 'to_bin', 'scanned_by')

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
