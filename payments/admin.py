from django.contrib import admin
from .models import PaymentMethod, Payment, PaymentTransaction, Refund


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'method_type', 'is_active', 'created_at')
    list_filter = ('method_type', 'is_active')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'customer', 'amount', 'payment_method', 'payment_for', 'status', 'currency', 'created_at')
    list_filter = ('status', 'payment_for')
    search_fields = ('payment_number', 'customer__name', 'reference_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment', 'provider', 'provider_ref', 'provider_status', 'status', 'amount', 'created_at')
    list_filter = ('provider', 'status')
    search_fields = ('payment__payment_number', 'provider_ref')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('refund_number', 'payment', 'amount', 'status', 'processed_by', 'processed_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('refund_number', 'payment__payment_number')
    readonly_fields = ('created_at', 'updated_at')
