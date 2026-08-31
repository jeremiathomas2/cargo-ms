from django.contrib import admin
from .models import Branch, BranchSetting


class BranchSettingInline(admin.StackedInline):
    model = BranchSetting
    can_delete = False
    verbose_name_plural = 'Branch Settings'


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'country', 'is_headquarters', 'is_active', 'manager', 'created_at']
    search_fields = ['name', 'code', 'city', 'country', 'phone', 'email']
    list_filter = ['is_headquarters', 'is_active', 'country', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [BranchSettingInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'name', 'code', 'is_headquarters', 'is_active')
        }),
        ('Location', {
            'fields': ('address', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Management', {
            'fields': ('manager',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BranchSetting)
class BranchSettingAdmin(admin.ModelAdmin):
    list_display = ['branch', 'currency', 'tracking_prefix', 'auto_receive', 'auto_dispatch', 'gps_required', 'insurance_default']
    search_fields = ['branch__name', 'branch__code', 'currency', 'tracking_prefix']
    list_filter = ['auto_receive', 'auto_dispatch', 'gps_required', 'insurance_default', 'currency']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Branch', {
            'fields': ('id', 'branch')
        }),
        ('Operating Hours', {
            'fields': ('operating_hours_start', 'operating_hours_end', 'timezone')
        }),
        ('Configuration', {
            'fields': ('currency', 'tracking_prefix', 'auto_receive', 'auto_dispatch', 'gps_required', 'insurance_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
