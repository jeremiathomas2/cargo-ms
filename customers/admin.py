from django.contrib import admin
from .models import Customer, CustomerAddress, CustomerContact


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0
    fields = ['address_type', 'label', 'address_line1', 'address_line2', 'city', 'region', 'country', 'is_default']


class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 0
    fields = ['name', 'title', 'email', 'phone', 'is_primary', 'receive_notifications']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_number', 'full_name', 'customer_type', 'status', 'phone', 'email', 'credit_limit', 'current_balance', 'rating', 'is_watchlisted', 'created_at']
    search_fields = ['customer_number', 'first_name', 'last_name', 'company_name', 'email', 'phone', 'tax_id']
    list_filter = ['customer_type', 'status', 'is_watchlisted', 'created_at']
    readonly_fields = ['id', 'total_shipments', 'total_revenue', 'created_at', 'updated_at']
    inlines = [CustomerAddressInline, CustomerContactInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'customer_number', 'customer_type', 'status')
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'company_name')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'secondary_phone')
        }),
        ('Financial', {
            'fields': ('tax_id', 'credit_limit', 'current_balance', 'payment_terms_days', 'total_shipments', 'total_revenue')
        }),
        ('Rating & Notes', {
            'fields': ('rating', 'notes')
        }),
        ('Watchlist', {
            'fields': ('is_watchlisted', 'watchlist_reason'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address_type', 'label', 'address_line1', 'city', 'region', 'country', 'is_default']
    search_fields = ['customer__customer_number', 'customer__company_name', 'label', 'address_line1', 'city']
    list_filter = ['address_type', 'is_default', 'country']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Address Information', {
            'fields': ('id', 'customer', 'address_type', 'label')
        }),
        ('Address Details', {
            'fields': ('address_line1', 'address_line2', 'city', 'region', 'country', 'postal_code')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Contact & Default', {
            'fields': ('is_default', 'contact_person', 'contact_phone')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'title', 'email', 'phone', 'is_primary', 'receive_notifications']
    search_fields = ['name', 'customer__customer_number', 'customer__company_name', 'email', 'phone']
    list_filter = ['is_primary', 'receive_notifications']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Contact Information', {
            'fields': ('id', 'customer', 'name', 'title')
        }),
        ('Communication', {
            'fields': ('email', 'phone')
        }),
        ('Preferences', {
            'fields': ('is_primary', 'receive_notifications')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
