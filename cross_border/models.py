import uuid

from django.db import models


class BorderPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    geofence = models.ForeignKey(
        "gps_tracking.Geofence",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="border_posts",
    )
    expected_dwell_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Border Post"
        verbose_name_plural = "Border Posts"

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.country}"


class BorderCrossingEvent(models.Model):
    class EventType(models.TextChoices):
        ENTRY = "entry", "Entry"
        EXIT = "exit", "Exit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    border_post = models.ForeignKey(
        BorderPost,
        on_delete=models.CASCADE,
        related_name="crossing_events",
    )
    trip = models.ForeignKey(
        "transportation.Trip",
        on_delete=models.CASCADE,
        related_name="border_crossing_events",
    )
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.CASCADE,
        related_name="border_crossing_events",
    )
    device = models.ForeignKey(
        "gps_tracking.GPSDevice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="border_crossing_events",
    )
    event_type = models.CharField(max_length=10, choices=EventType.choices)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    documents_checked = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Border Crossing Event"
        verbose_name_plural = "Border Crossing Events"

    def __str__(self):
        return f"{self.event_type} at {self.border_post} - {self.trip}"


class CustomsDeclaration(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        "cargo.Shipment",
        on_delete=models.CASCADE,
        related_name="customs_declarations",
    )
    declaration_number = models.CharField(max_length=100, unique=True)
    hs_code = models.CharField(max_length=20)
    goods_description = models.TextField()
    declared_value = models.DecimalField(max_digits=14, decimal_places=2)
    duty_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customs Declaration"
        verbose_name_plural = "Customs Declarations"

    def __str__(self):
        return f"Declaration {self.declaration_number} - {self.status}"


class CorridorRoute(models.Model):
    class CorridorType(models.TextChoices):
        CENTRAL = "central", "Central Corridor"
        SOUTHERN = "southern", "Southern Corridor"
        NORTHERN = "northern", "Northern Corridor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        "transportation.Route",
        on_delete=models.CASCADE,
        related_name="corridor_routes",
    )
    corridor_name = models.CharField(max_length=200)
    corridor_type = models.CharField(max_length=10, choices=CorridorType.choices)
    countries = models.JSONField(default=list, blank=True)
    is_treaty_route = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["corridor_name"]
        verbose_name = "Corridor Route"
        verbose_name_plural = "Corridor Routes"

    def __str__(self):
        return f"{self.corridor_name} ({self.corridor_type})"


class RegionalAgent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    address = models.TextField(blank=True, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    assigned_shipments = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(
        "saas_config.Organization",
        on_delete=models.CASCADE,
        related_name="regional_agents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Regional Agent"
        verbose_name_plural = "Regional Agents"

    def __str__(self):
        return f"{self.name} ({self.company}) - {self.country}"
