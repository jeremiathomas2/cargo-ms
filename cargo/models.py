import uuid
from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('awaiting_receiving', 'Awaiting Receiving'),
        ('received', 'Received'),
        ('in_warehouse', 'In Warehouse'),
        ('sorted', 'Sorted'),
        ('ready_for_dispatch', 'Ready for Dispatch'),
        ('loaded', 'Loaded'),
        ('in_transit', 'In Transit'),
        ('arrived_destination', 'Arrived Destination'),
        ('customs_hold', 'Customs Hold'),
        ('ready_for_delivery', 'Ready for Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivery_attempted', 'Delivery Attempted'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    CARGO_TYPE_CHOICES = [
        ('general', 'General Cargo'),
        ('perishable', 'Perishable'),
        ('hazardous', 'Hazardous'),
        ('fragile', 'Fragile'),
        ('oversized', 'Oversized'),
        ('liquid', 'Liquid'),
        ('electronics', 'Electronics'),
        ('textiles', 'Textiles'),
        ('mining', 'Mining Equipment'),
        ('agriculture', 'Agricultural'),
        ('pharmaceutical', 'Pharmaceutical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='shipments')
    tracking_id = models.CharField(max_length=30, unique=True, db_index=True)
    booking_number = models.CharField(max_length=30, unique=True)
    waybill_number = models.CharField(max_length=30, blank=True, unique=True, null=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='shipments')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_shipments')

    sender_name = models.CharField(max_length=200)
    sender_phone = models.CharField(max_length=20)
    sender_address = models.TextField(blank=True)
    sender_city = models.CharField(max_length=100, blank=True)
    receiver_name = models.CharField(max_length=200)
    receiver_phone = models.CharField(max_length=20)
    receiver_address = models.TextField(blank=True)
    receiver_city = models.CharField(max_length=100, blank=True)

    origin_branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='originating_shipments')
    destination_branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='destination_shipments')
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    route = models.ForeignKey('transportation.Route', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')

    cargo_type = models.CharField(max_length=20, choices=CARGO_TYPE_CHOICES, default='general')
    description = models.TextField(blank=True)
    num_packages = models.PositiveIntegerField(default=1)
    actual_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    volumetric_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    charged_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    volume = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    length = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='cm')
    width = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='cm')
    height = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='cm')
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_insured = models.BooleanField(default=False)
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pickup_required = models.BooleanField(default=False)
    delivery_required = models.BooleanField(default=True)
    special_handling = models.TextField(blank=True)
    is_fragile = models.BooleanField(default=False)
    is_perishable = models.BooleanField(default=False)
    is_hazardous = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='booked', db_index=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overpaid', 'Overpaid'),
        ('refunded', 'Refunded'),
    ], default='unpaid')
    current_branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_cargo')
    current_warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_cargo')
    current_location = models.CharField(max_length=200, blank=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    assigned_trip = models.ForeignKey('transportation.Trip', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    assigned_vehicle = models.ForeignKey('transportation.Vehicle', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    assigned_driver = models.ForeignKey('transportation.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    assigned_gps = models.ForeignKey('gps_tracking.GPSDevice', on_delete=models.SET_NULL, null=True, blank=True, related_name='tracked_shipments')

    estimated_departure = models.DateTimeField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    handling_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    qr_code = models.CharField(max_length=255, blank=True)
    barcode = models.CharField(max_length=100, blank=True)

    public_tracking_enabled = models.BooleanField(default=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['origin', 'destination']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.tracking_id} - {self.origin} → {self.destination}"

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            from core.utils import generate_tracking_id
            self.tracking_id = generate_tracking_id()
        if not self.booking_number:
            from core.utils import generate_document_number
            self.booking_number = generate_document_number('BK')
        super().save(*args, **kwargs)


class ShipmentStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=25, blank=True)
    new_status = models.CharField(max_length=25)
    changed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reason = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=[
        ('manual', 'Manual'),
        ('gps', 'GPS'),
        ('scanner', 'Scanner'),
        ('api', 'API'),
        ('automation', 'Automation'),
    ], default='manual')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shipment.tracking_id}: {self.previous_status} → {self.new_status}"


class CargoEvent(models.Model):
    EVENT_TYPES = [
        ('status_change', 'Status Change'),
        ('location_update', 'Location Update'),
        ('assignment', 'Assignment'),
        ('note', 'Note'),
        ('scan', 'Scan'),
        ('exception', 'Exception'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shipment.tracking_id} - {self.event_type}"


class CargoNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    is_internal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.shipment.tracking_id}"


class CargoAssignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('vehicle', 'Vehicle'),
        ('driver', 'Driver'),
        ('gps', 'GPS Device'),
        ('trip', 'Trip'),
        ('warehouse', 'Warehouse'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='assignments')
    assignment_type = models.CharField(max_length=15, choices=ASSIGNMENT_TYPES)
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shipment.tracking_id} - {self.assignment_type}"
