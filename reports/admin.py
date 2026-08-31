from django.contrib import admin

from .models import ReportExport, ReportTemplate


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "report_type",
        "is_active",
        "organization",
        "created_at",
    )
    list_filter = ("report_type", "is_active", "organization")
    search_fields = ("name",)


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = (
        "report_type",
        "export_format",
        "template",
        "status",
        "requested_by",
        "created_at",
        "completed_at",
    )
    list_filter = ("export_format", "status", "report_type", "created_at")
    search_fields = ("report_type",)
