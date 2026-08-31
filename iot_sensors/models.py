import uuid

from django.db import models


class SensorDevice(models.Model):
    class SensorType(models.TextChoices):
        TEMPERATURE = "temperature", "Temperature"
        HUMIDITY = "humidity", "Humidity"
        SHOCK = "shock", "Shock"
        LIGHT = "light", "Light"
        DOOR = "door", "Door"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracker_id = models.CharField(max_length=100, unique=True)
    sensor_type = models.CharField(max_length=20, choices=SensorType.choices)
    serial_number = models.CharField(max_length=100)
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sensor_devices",
    )
    package = models.ForeignKey(
        "packages.Package",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sensor_devices",
    )
    is_active = models.BooleanField(default=True)
    battery_level = models.PositiveIntegerField(default=100)
    last_reading = models.JSONField(default=dict, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sensor Device"
        verbose_name_plural = "Sensor Devices"

    def __str__(self):
        return f"{self.tracker_id} ({self.sensor_type})"


class SensorReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sensor = models.ForeignKey(
        SensorDevice,
        on_delete=models.CASCADE,
        related_name="readings",
    )
    temperature = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shock_level = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    light_exposure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    door_open = models.BooleanField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Sensor Reading"
        verbose_name_plural = "Sensor Readings"

    def __str__(self):
        return f"Reading from {self.sensor} at {self.timestamp}"


class SensorAlert(models.Model):
    class AlertType(models.TextChoices):
        TEMP_HIGH = "temp_high", "Temperature High"
        TEMP_LOW = "temp_low", "Temperature Low"
        HUMIDITY_HIGH = "humidity_high", "Humidity High"
        SHOCK_DETECTED = "shock_detected", "Shock Detected"
        DOOR_TAMPERED = "door_tampered", "Door Tampered"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sensor = models.ForeignKey(
        SensorDevice,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    message = models.TextField()
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_sensor_alerts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sensor Alert"
        verbose_name_plural = "Sensor Alerts"

    def __str__(self):
        return f"{self.alert_type} - {self.severity} - {self.sensor}"


class DigitalSeal(models.Model):
    class Status(models.TextChoices):
        INTACT = "intact", "Intact"
        TAMPERED = "tampered", "Tampered"
        BROKEN = "broken", "Broken"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seal_id = models.CharField(max_length=50, unique=True)
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.CASCADE,
        related_name="digital_seals",
    )
    package = models.ForeignKey(
        "packages.Package",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="digital_seals",
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INTACT)
    applied_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applied_digital_seals",
    )
    verified_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_digital_seals",
    )

    class Meta:
        ordering = ["-applied_at"]
        verbose_name = "Digital Seal"
        verbose_name_plural = "Digital Seals"

    def __str__(self):
        return f"Seal {self.seal_id} - {self.status}"
