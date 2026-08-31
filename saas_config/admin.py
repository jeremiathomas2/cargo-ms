from django.contrib import admin

from .models import Organization, OrganizationDomain, TenantQuota


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "subdomain",
        "currency",
        "timezone",
        "plan",
        "is_active",
        "max_users",
        "max_shipments",
        "created_at",
        "updated_at",
    )
    list_filter = ("plan", "is_active", "currency", "timezone")
    search_fields = ("name", "slug", "subdomain")


@admin.register(OrganizationDomain)
class OrganizationDomainAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "organization",
        "is_primary",
        "is_verified",
        "created_at",
    )
    list_filter = ("is_primary", "is_verified")
    search_fields = ("domain",)


@admin.register(TenantQuota)
class TenantQuotaAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "users_used",
        "shipments_used",
        "storage_used_mb",
        "api_requests_used",
        "period_start",
        "period_end",
    )
    search_fields = ("organization__name",)
