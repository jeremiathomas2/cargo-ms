from django.contrib import admin

from .models import (
    BorderCrossingEvent,
    BorderPost,
    CorridorRoute,
    CustomsDeclaration,
    RegionalAgent,
)


@admin.register(BorderPost)
class BorderPostAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "country", "is_active", "expected_dwell_hours", "created_at")
    list_filter = ("country", "is_active")
    search_fields = ("name", "code")


@admin.register(BorderCrossingEvent)
class BorderCrossingEventAdmin(admin.ModelAdmin):
    list_display = (
        "border_post",
        "trip",
        "shipment",
        "event_type",
        "latitude",
        "longitude",
        "timestamp",
    )
    list_filter = ("event_type", "border_post", "timestamp")
    search_fields = ("trip__trip_number", "shipment__tracking_number", "notes")


@admin.register(CustomsDeclaration)
class CustomsDeclarationAdmin(admin.ModelAdmin):
    list_display = (
        "declaration_number",
        "shipment",
        "hs_code",
        "declared_value",
        "duty_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("declaration_number", "hs_code", "goods_description")


@admin.register(CorridorRoute)
class CorridorRouteAdmin(admin.ModelAdmin):
    list_display = ("corridor_name", "route", "corridor_type", "is_treaty_route", "created_at")
    list_filter = ("corridor_type", "is_treaty_route")
    search_fields = ("corridor_name",)


@admin.register(RegionalAgent)
class RegionalAgentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "country", "phone", "email", "is_active", "organization")
    list_filter = ("country", "is_active", "organization")
    search_fields = ("name", "company", "email")
