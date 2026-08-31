import uuid
from django.db import models


class Vehicle(models.Model):
    TYPE_CHOICES = [
        ('truck', 'Truck'), ('trailer', 'Trailer'), ('van', 'Van'),
        ('pickup', 'Pickup'), ('flatbed', 'Flatbed'), ('tanker', 'Tanker'),
        ('container_truck', 'Container Truck'), ('motorcycle', 'Motorcycle'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'), ('on_route', 'On Route'),
        ('maintenance', 'Maintenance'), ('retired', 'Retired'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='vehicles')
    registration_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='truck')
    make = models.CharField(max_length=50, blank=True)
    model_name = models.CharField(max_length=50, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=30, blank=True)
    max_capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_volume_m3 = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    assigned_branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    gps_device = models.ForeignKey('gps_tracking.GPSDevice', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_vehicles')
    insurance_expiry = models.DateField(null=True, blank=True)
    inspection_expiry = models.DateField(null=True, blank=True)
    total_km = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_trips = models.PositiveIntegerField(default=0)
    fuel_capacity = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='Liters')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['registration_number']

    def __str__(self):
        return f"{self.registration_number} ({self.get_vehicle_type_display()})"


class Driver(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'), ('on_duty', 'On Duty'),
        ('off_duty', 'Off Duty'), ('on_leave', 'On Leave'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='drivers')
    user = models.OneToOneField('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    license_number = models.CharField(max_length=50)
    license_expiry = models.DateField()
    license_class = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    assigned_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    assigned_branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    total_trips = models.PositiveIntegerField(default=0)
    total_km = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Route(models.Model):
    ROUTE_TYPE_CHOICES = [('domestic', 'Domestic'), ('transit', 'Transit'), ('cross_border', 'Cross-Border')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    route_type = models.CharField(max_length=15, choices=ROUTE_TYPE_CHOICES, default='domestic')
    corridor = models.CharField(max_length=100, blank=True, help_text='Transport corridor name')
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_duration_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.origin} → {self.destination})"


class RouteStop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=200)
    sequence = models.PositiveIntegerField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    estimated_arrival_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sequence']
        unique_together = ('route', 'sequence')

    def __str__(self):
        return f"{self.route.name} - Stop {self.sequence}: {self.name}"


class Trip(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'), ('active', 'Active'),
        ('in_transit', 'In Transit'), ('at_stop', 'At Stop'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip_number = models.CharField(max_length=30, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name='trips')
    manifest = models.ForeignKey('Manifest', on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    gps_device = models.ForeignKey('gps_tracking.GPSDevice', on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planned')
    departure_time = models.DateTimeField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    actual_distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    num_shipments = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.trip_number

    def save(self, *args, **kwargs):
        if not self.trip_number:
            from core.utils import generate_document_number
            self.trip_number = generate_document_number('TRIP')
        super().save(*args, **kwargs)


class Manifest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('locked', 'Locked'),
        ('loaded', 'Loaded'), ('dispatched', 'Dispatched'), ('completed', 'Completed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manifest_number = models.CharField(max_length=30, unique=True)
    trip = models.OneToOneField(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='manifest_detail')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='manifests')
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='manifests')
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    total_shipments = models.PositiveIntegerField(default=0)
    total_packages = models.PositiveIntegerField(default=0)
    total_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_volume_m3 = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='locked_manifests')
    dispatched_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_manifests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.manifest_number

    def save(self, *args, **kwargs):
        if not self.manifest_number:
            from core.utils import generate_document_number
            self.manifest_number = generate_document_number('MAN')
        super().save(*args, **kwargs)


class ManifestShipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manifest = models.ForeignKey(Manifest, on_delete=models.CASCADE, related_name='manifest_shipments')
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.CASCADE, related_name='manifest_entries')
    loaded_at = models.DateTimeField(null=True, blank=True)
    loaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    unloaded_at = models.DateTimeField(null=True, blank=True)
    unloaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='unloaded_manifests')
    position = models.PositiveIntegerField(default=0, help_text='Loading position on vehicle')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('manifest', 'shipment')
        ordering = ['position']

    def __str__(self):
        return f"{self.manifest.manifest_number} - {self.shipment.tracking_id}"
