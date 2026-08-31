from django.contrib import admin
from .models import Package, PackageItem


class PackageItemInline(admin.TabularInline):
    model = PackageItem
    extra = 1
    readonly_fields = ('id', 'created_at')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'package_number', 'shipment', 'package_type', 'weight',
        'condition', 'status', 'created_at',
    )
    list_filter = ('package_type', 'condition', 'status')
    search_fields = ('package_number', 'barcode', 'shipment__tracking_id', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [PackageItemInline]
    fieldsets = (
        ('Identifiers', {
            'fields': ('id', 'package_number', 'barcode', 'qr_code'),
        }),
        ('Shipment', {
            'fields': ('shipment',),
        }),
        ('Details', {
            'fields': ('package_type', 'description', 'weight', 'length', 'width', 'height', 'volume', 'value'),
        }),
        ('Status', {
            'fields': ('condition', 'status'),
        }),
        ('Location', {
            'fields': ('current_warehouse', 'current_zone', 'current_bin', 'assigned_gps'),
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(PackageItem)
class PackageItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'package', 'quantity', 'unit_value', 'hs_code', 'created_at')
    search_fields = ('description', 'package__package_number', 'hs_code')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at')
