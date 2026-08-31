import uuid

from django.db import models


class ETAProjection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.CASCADE,
        related_name="eta_projections",
    )
    predicted_arrival = models.DateTimeField()
    confidence_low = models.DateTimeField()
    confidence_high = models.DateTimeField()
    model_version = models.CharField(max_length=50)
    factors = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "ETA Projection"
        verbose_name_plural = "ETA Projections"

    def __str__(self):
        return f"ETA for {self.shipment} - {self.predicted_arrival}"


class RouteOptimization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(
        "transportation.Trip",
        on_delete=models.CASCADE,
        related_name="route_optimizations",
    )
    suggested_route = models.JSONField(default=dict, blank=True)
    estimated_savings_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_savings_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fuel_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_applied = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Route Optimization"
        verbose_name_plural = "Route Optimizations"

    def __str__(self):
        return f"Optimization for trip {self.trip} - {self.estimated_savings_km}km saved"


class AnomalyDetection(models.Model):
    class AnomalyType(models.TextChoices):
        SPEED = "speed", "Speed Anomaly"
        DEVIATION = "deviation", "Route Deviation"
        UNAUTHORIZED = "unauthorized", "Unauthorized Use"
        DWELL = "dwell", "Excessive Dwell"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        "gps_tracking.GPSDevice",
        on_delete=models.CASCADE,
        related_name="anomalies",
    )
    anomaly_type = models.CharField(max_length=20, choices=AnomalyType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True, default="")
    detected_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_anomalies",
    )

    class Meta:
        ordering = ["-detected_at"]
        verbose_name = "Anomaly Detection"
        verbose_name_plural = "Anomaly Detections"

    def __str__(self):
        return f"{self.anomaly_type} - {self.severity} - {self.device}"


class DemandForecast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        "transportation.Route",
        on_delete=models.CASCADE,
        related_name="demand_forecasts",
    )
    forecast_date = models.DateField()
    predicted_volume = models.DecimalField(max_digits=10, decimal_places=2)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Demand Forecast"
        verbose_name_plural = "Demand Forecasts"

    def __str__(self):
        return f"Demand forecast for {self.route} on {self.forecast_date}"


class PricingRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        "transportation.Route",
        on_delete=models.CASCADE,
        related_name="pricing_recommendations",
    )
    suggested_rate = models.DecimalField(max_digits=12, decimal_places=2)
    current_rate = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, default="")
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_pricing_recommendations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pricing Recommendation"
        verbose_name_plural = "Pricing Recommendations"

    def __str__(self):
        return f"Pricing for {self.route} - {self.suggested_rate}"
