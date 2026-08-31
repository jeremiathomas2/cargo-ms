import uuid

from django.db import models


class ShipmentTemplate(models.Model):
    class RecurrenceInterval(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Biweekly"
        MONTHLY = "monthly", "Monthly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="shipment_templates",
    )
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    cargo_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)
    special_handling = models.TextField(blank=True, default="")
    is_recurring = models.BooleanField(default=False)
    recurrence_interval = models.CharField(
        max_length=10,
        choices=RecurrenceInterval.choices,
        null=True,
        blank=True,
    )
    last_used = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_shipment_templates",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Shipment Template"
        verbose_name_plural = "Shipment Templates"

    def __str__(self):
        return f"{self.name} - {self.origin} to {self.destination}"


class CorporateAPIKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    key_name = models.CharField(max_length=200)
    api_key = models.CharField(max_length=64, unique=True)
    secret_key = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    rate_limit = models.PositiveIntegerField(default=1000)
    total_requests = models.PositiveIntegerField(default=0)
    last_request_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Corporate API Key"
        verbose_name_plural = "Corporate API Keys"

    def __str__(self):
        return f"{self.key_name} ({self.customer})"


class BulkBookingUpload(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="bulk_booking_uploads",
    )
    file = models.FileField(upload_to="bulk_bookings/")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    error_rows = models.PositiveIntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bulk Booking Upload"
        verbose_name_plural = "Bulk Booking Uploads"

    def __str__(self):
        return f"Bulk upload {self.id} by {self.uploaded_by}"
