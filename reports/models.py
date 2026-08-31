import uuid

from django.db import models


class ReportTemplate(models.Model):
    class ReportType(models.TextChoices):
        DAILY_CARGO = "daily_cargo", "Daily Cargo Report"
        MONTHLY_CARGO = "monthly_cargo", "Monthly Cargo Report"
        REVENUE = "revenue", "Revenue Report"
        OUTSTANDING_BALANCES = "outstanding_balances", "Outstanding Balances"
        BRANCH_PERFORMANCE = "branch_performance", "Branch Performance"
        DESTINATION_ANALYSIS = "destination_analysis", "Destination Analysis"
        DELIVERY_PERFORMANCE = "delivery_performance", "Delivery Performance"
        DELAYED_SHIPMENTS = "delayed_shipments", "Delayed Shipments"
        LOST_DAMAGED = "lost_damaged", "Lost & Damaged"
        WAREHOUSE_UTILIZATION = "warehouse_utilization", "Warehouse Utilization"
        VEHICLE_UTILIZATION = "vehicle_utilization", "Vehicle Utilization"
        DRIVER_PERFORMANCE = "driver_performance", "Driver Performance"
        GPS_HISTORY = "gps_history", "GPS History"
        PAYMENT_RECONCILIATION = "payment_reconciliation", "Payment Reconciliation"
        CUSTOMER_STATEMENT = "customer_statement", "Customer Statement"
        AUDIT_REPORT = "audit_report", "Audit Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=ReportType.choices)
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(
        "saas_config.Organization",
        on_delete=models.CASCADE,
        related_name="report_templates",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"

    def __str__(self):
        return f"{self.name} ({self.report_type})"


class ReportExport(models.Model):
    class ExportFormat(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel"
        CSV = "csv", "CSV"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATING = "generating", "Generating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exports",
    )
    report_type = models.CharField(max_length=30, choices=ReportTemplate.ReportType.choices)
    export_format = models.CharField(max_length=10, choices=ExportFormat.choices, default=ExportFormat.PDF)
    parameters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="reports/", blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="report_exports",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Report Export"
        verbose_name_plural = "Report Exports"

    def __str__(self):
        return f"{self.report_type} ({self.export_format}) - {self.status}"
