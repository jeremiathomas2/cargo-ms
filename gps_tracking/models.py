import uuid
from django.db import models


class GPSDevice(models.Model):
    STATUS_CHOICES = [('online', 'Online'), ('offline', 'Offline'), ('maintenance', 'Maintenance'), ('retired', 'Retired')]
    TYPE_CHOICES = [('vehicle', 'Vehicle Tracker'), ('cargo', 'Cargo Tracker'), ('portable', 'Portable')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracker_id = models.CharField(max_length=50, unique=True)
    imei = models.CharField(max_length=20, unique=True)
    serial_number = models.CharField(max_length=50, blank=True)
    device_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='vehicle')
    sim_number = models.CharField(max_length=20, blank=True)
    network_provider = models.CharField(max_length=50, blank=True)
    battery_level = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='offline')
    last_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_speed = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    last_heading = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_altitude = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    last_update = models.DateTimeField(null=True, blank=True)
    assigned_vehicle = models.ForeignKey('transportation.Vehicle', on_delete=models.SET_NULL, null=True, blank=True, related_name='gps_devices')
    assigned_shipment = models.ForeignKey('cargo.Shipment', on_delete=models.SET_NULL, null=True, blank=True, related_name='gps_devices')
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='gps_devices')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_update']

    def __str__(self):
        return f"{self.tracker_id} ({self.get_device_type_display()})"

    @property
    def is_online(self):
        from django.utils import timezone
        from datetime import timedelta
        if not self.last_update:
            return False
        return self.last_update > timezone.now() - timedelta(minutes=10)


class GPSPosition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='positions')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    heading = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    altitude = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    battery_level = models.PositiveIntegerField(null=True, blank=True)
    ignition = models.BooleanField(null=True, blank=True)
    timestamp = models.DateTimeField(db_index=True)
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.device.tracker_id} @ {self.timestamp}"


class GPSDeviceAssignment(models.Model):
    ASSIGNMENT_TYPES = [('vehicle', 'Vehicle'), ('cargo', 'Cargo'), ('package', 'Package')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='assignments')
    assignment_type = models.CharField(max_length=10, choices=ASSIGNMENT_TYPES)
    vehicle = models.ForeignKey('transportation.Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.SET_NULL, null=True, blank=True)
    package = models.ForeignKey('packages.Package', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    unassigned_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.device} → {self.assignment_type}"


class Geofence(models.Model):
    SHAPE_CHOICES = [('circle', 'Circle'), ('polygon', 'Polygon')]
    TYPE_CHOICES = [('branch', 'Branch'), ('warehouse', 'Warehouse'), ('port', 'Port'), ('airport', 'Airport'), ('border', 'Border Post'), ('delivery_area', 'Delivery Area'), ('custom', 'Custom')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fence_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='custom')
    shape = models.CharField(max_length=10, choices=SHAPE_CHOICES, default='circle')
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radius_meters = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    polygon_coords = models.JSONField(default=list, blank=True, help_text='List of [lat,lng] pairs')
    is_active = models.BooleanField(default=True)
    alert_on_enter = models.BooleanField(default=True)
    alert_on_exit = models.BooleanField(default=True)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='geofences')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GeofenceEvent(models.Model):
    EVENT_TYPES = [('enter', 'Enter'), ('exit', 'Exit')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    geofence = models.ForeignKey(Geofence, on_delete=models.CASCADE, related_name='events')
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='geofence_events')
    event_type = models.CharField(max_length=5, choices=EVENT_TYPES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    trip = models.ForeignKey('transportation.Trip', on_delete=models.SET_NULL, null=True, blank=True, related_name='geofence_events')
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.SET_NULL, null=True, blank=True, related_name='geofence_events')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device} {self.event_type} {self.geofence}"


class GPSAlert(models.Model):
    ALERT_TYPES = [('speed', 'Speed Exceeded'), ('offline', 'Device Offline'), ('low_battery', 'Low Battery'), ('geofence', 'Geofence Event'), ('deviation', 'Route Deviation'), ('unauthorized', 'Unauthorized Movement')]
    SEVERITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=15, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    message = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device} - {self.alert_type} ({self.severity})"
