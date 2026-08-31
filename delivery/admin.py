from django.contrib import admin
from .models import Delivery, DeliveryAttempt, ProofOfDelivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('delivery_number', 'shipment', 'driver', 'status', 'scheduled_date', 'delivered_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('delivery_number', 'shipment__tracking_id', 'delivery_address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'attempt_number', 'result', 'attempted_by', 'attempted_at')
    list_filter = ('result',)
    search_fields = ('delivery__delivery_number',)
    readonly_fields = ('attempted_at',)


@admin.register(ProofOfDelivery)
class ProofOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'recipient_name', 'recipient_phone', 'otp_verified', 'delivered_by', 'delivered_at')
    list_filter = ('otp_verified',)
    search_fields = ('delivery__delivery_number', 'recipient_name', 'recipient_phone')
    readonly_fields = ('delivered_at',)
