import uuid

from django.db import models


class SLALevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    target_transit_hours = models.DecimalField(max_digits=8, decimal_places=2)
    max_transit_hours = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "SLA Level"
        verbose_name_plural = "SLA Levels"

    def __str__(self):
        return f"{self.name} ({self.code})"


class SLABreach(models.Model):
    class Severity(models.TextChoices):
        MINOR = "minor", "Minor"
        MAJOR = "major", "Major"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.CASCADE,
        related_name="sla_breaches",
    )
    sla_level = models.ForeignKey(
        SLALevel,
        on_delete=models.CASCADE,
        related_name="breaches",
    )
    expected_arrival = models.DateTimeField()
    actual_arrival = models.DateTimeField(null=True, blank=True)
    breach_duration_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    escalated = models.BooleanField(default=False)
    escalated_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="escalated_breaches",
    )
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "SLA Breach"
        verbose_name_plural = "SLA Breaches"

    def __str__(self):
        return f"Breach for {self.shipment} - {self.severity}"


class Watchlist(models.Model):
    class EntityType(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADDRESS = "address", "Address"
        PHONE = "phone", "Phone"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=10, choices=EntityType.choices)
    entity_value = models.CharField(max_length=500)
    reason = models.TextField()
    added_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="added_watchlist_items",
    )
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-added_at"]
        verbose_name = "Watchlist"
        verbose_name_plural = "Watchlists"

    def __str__(self):
        return f"Watchlist: {self.entity_type} - {self.entity_value}"


class RiskScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.CASCADE,
        related_name="risk_scores",
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    risk_factors = models.JSONField(default=list, blank=True)
    flags = models.JSONField(default=list, blank=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_risk_scores",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Risk Score"
        verbose_name_plural = "Risk Scores"

    def __str__(self):
        return f"Risk score {self.risk_score} for {self.shipment}"
