from django.contrib import admin
from .models import (
    PricingRule, Tax, Discount, Insurance,
    Quotation, QuotationItem, Invoice, InvoiceItem,
)


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'calculation', 'base_rate', 'min_charge', 'max_charge', 'priority', 'is_active')
    list_filter = ('calculation', 'is_active')
    search_fields = ('name', 'origin', 'destination')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'applies_to', 'is_active')
    list_filter = ('applies_to', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'min_shipments', 'max_discount', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'shipment', 'insured_value', 'premium', 'status', 'provider', 'valid_from', 'valid_to')
    list_filter = ('status',)
    search_fields = ('policy_number', 'shipment__tracking_id', 'provider')
    readonly_fields = ('created_at',)


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'total')


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('quotation_number', 'customer', 'origin', 'destination', 'total', 'status', 'currency', 'valid_until', 'created_at')
    list_filter = ('status',)
    search_fields = ('quotation_number', 'customer__name', 'origin', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QuotationItemInline]


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ('quotation', 'description', 'quantity', 'unit_price', 'total')
    search_fields = ('quotation__quotation_number', 'description')


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'total')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'status', 'total', 'amount_paid', 'balance', 'currency', 'due_date', 'created_at')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'customer__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total')
    search_fields = ('invoice__invoice_number', 'description')
