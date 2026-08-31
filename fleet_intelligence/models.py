import uuid

from django.db import models


class DriverScorecard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(
        "transportation.Driver",
        on_delete=models.CASCADE,
        related_name="scorecards",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    speeding_events = models.PositiveIntegerField(default=0)
    harsh_braking_events = models.PositiveIntegerField(default=0)
    on_time_deliveries = models.PositiveIntegerField(default=0)
    total_deliveries = models.PositiveIntegerField(default=0)
    avg_speed = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_speed = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fuel_consumed_l = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period_end"]
        verbose_name = "Driver Scorecard"
        verbose_name_plural = "Driver Scorecards"

    def __str__(self):
        return f"Scorecard for {self.driver} ({self.period_start} to {self.period_end})"


class VehicleMaintenance(models.Model):
    class MaintenanceType(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CORRECTIVE = "corrective", "Corrective"
        EMERGENCY = "emergency", "Emergency"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        "transportation.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    maintenance_type = models.CharField(max_length=12, choices=MaintenanceType.choices)
    description = models.TextField()
    mileage_at_service = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    next_service_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_service_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    performed_by = models.CharField(max_length=200, blank=True, default="")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Vehicle Maintenance"
        verbose_name_plural = "Vehicle Maintenance Records"

    def __str__(self):
        return f"{self.maintenance_type} for {self.vehicle} - {self.status}"


class FuelLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        "transportation.Vehicle",
        on_delete=models.CASCADE,
        related_name="fuel_logs",
    )
    date = models.DateField()
    odometer_km = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_liters = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_liter = models.DecimalField(max_digits=8, decimal_places=2)
    station = models.CharField(max_length=200, blank=True, default="")
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fuel_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Fuel Log"
        verbose_name_plural = "Fuel Logs"

    def __str__(self):
        return f"Fuel log for {self.vehicle} on {self.date}"


class CarbonEmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.CASCADE,
        related_name="carbon_emissions",
    )
    trip = models.ForeignKey(
        "transportation.Trip",
        on_delete=models.CASCADE,
        related_name="carbon_emissions",
    )
    vehicle = models.ForeignKey(
        "transportation.Vehicle",
        on_delete=models.CASCADE,
        related_name="carbon_emissions",
    )
    distance_km = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_consumed_l = models.DecimalField(max_digits=10, decimal_places=2)
    emission_factor = models.DecimalField(max_digits=8, decimal_places=4)
    total_emissions_kg = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Carbon Emission"
        verbose_name_plural = "Carbon Emissions"

    def __str__(self):
        return f"Emissions for {self.shipment} - {self.total_emissions_kg}kg CO2"
