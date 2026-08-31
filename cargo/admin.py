from django.contrib import admin
from .models import Shipment, ShipmentStatusHistory, CargoEvent, CargoNote, CargoAssignment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'tracking_id', 'customer', 'origin', 'destination',
        'status', 'payment_status', 'created_at',
    )
    list_filter = ('status', 'priority', 'cargo_type', 'payment_status')
    search_fields = (
        'tracking_id', 'booking_number', 'sender_name', 'receiver_name',
        'customer__first_name', 'customer__last_name', 'customer__company_name',
    )
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'tracking_id', 'booking_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Identifiers', {
            'fields': ('id', 'tracking_id', 'booking_number', 'waybill_number', 'organization'),
        }),
        ('Parties', {
            'fields': ('customer', 'created_by'),
        }),
        ('Sender', {
            'fields': ('sender_name', 'sender_phone', 'sender_address', 'sender_city'),
        }),
        ('Receiver', {
            'fields': ('receiver_name', 'receiver_phone', 'receiver_address', 'receiver_city'),
        }),
        ('Route', {
            'fields': ('origin_branch', 'destination_branch', 'origin', 'destination', 'route'),
        }),
        ('Cargo Details', {
            'fields': (
                'cargo_type', 'description', 'num_packages',
                'actual_weight', 'volumetric_weight', 'charged_weight', 'volume',
                'length', 'width', 'height', 'declared_value',
            ),
        }),
        ('Flags', {
            'fields': (
                'is_insured', 'insurance_amount', 'pickup_required', 'delivery_required',
                'special_handling', 'is_fragile', 'is_perishable', 'is_hazardous', 'priority',
            ),
        }),
        ('Status', {
            'fields': (
                'status', 'payment_status', 'current_branch', 'current_warehouse',
                'current_location', 'current_latitude', 'current_longitude',
            ),
        }),
        ('Assignment', {
            'fields': ('assigned_trip', 'assigned_vehicle', 'assigned_driver', 'assigned_gps'),
        }),
        ('Dates', {
            'fields': ('estimated_departure', 'estimated_arrival', 'actual_arrival', 'delivered_at'),
        }),
        ('Cost', {
            'fields': ('shipping_cost', 'handling_fee', 'insurance_fee', 'total_cost'),
        }),
        ('Tracking', {
            'fields': ('qr_code', 'barcode', 'public_tracking_enabled'),
        }),
        ('Meta', {
            'fields': ('is_deleted', 'deleted_at', 'created_at', 'updated_at'),
        }),
    )


@admin.register(ShipmentStatusHistory)
class ShipmentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'previous_status', 'new_status', 'changed_by', 'source', 'created_at')
    list_filter = ('new_status', 'source')
    search_fields = ('shipment__tracking_id',)
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at')


@admin.register(CargoEvent)
class CargoEventAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'event_type', 'description', 'created_by', 'created_at')
    list_filter = ('event_type',)
    search_fields = ('shipment__tracking_id', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at')


@admin.register(CargoNote)
class CargoNoteAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'author', 'content', 'is_internal', 'created_at')
    list_filter = ('is_internal',)
    search_fields = ('shipment__tracking_id', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CargoAssignment)
class CargoAssignmentAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'assignment_type', 'assigned_by', 'created_at')
    list_filter = ('assignment_type',)
    search_fields = ('shipment__tracking_id',)
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at')
