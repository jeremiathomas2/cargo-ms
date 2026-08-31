import uuid
from django.db import models


class Package(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('in_warehouse', 'In Warehouse'),
        ('sorted', 'Sorted'),
        ('loaded', 'Loaded'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]
    TYPE_CHOICES = [
        ('box', 'Box'),
        ('crate', 'Crate'),
        ('pallet', 'Pallet'),
        ('bag', 'Bag'),
        ('drum', 'Drum'),
        ('container', 'Container'),
        ('envelope', 'Envelope'),
        ('other', 'Other'),
    ]
    CONDITION_CHOICES = [
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.CASCADE, related_name='packages')
    package_number = models.CharField(max_length=30, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    qr_code = models.CharField(max_length=255, blank=True)
    package_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='box')
    description = models.CharField(max_length=200, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    length = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='cm')
    width = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='cm')
    height = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='cm')
    volume = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    current_warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='packages')
    current_zone = models.ForeignKey('warehouse.WarehouseZone', on_delete=models.SET_NULL, null=True, blank=True, related_name='packages')
    current_bin = models.ForeignKey('warehouse.WarehouseBin', on_delete=models.SET_NULL, null=True, blank=True, related_name='packages')
    assigned_gps = models.ForeignKey('gps_tracking.GPSDevice', on_delete=models.SET_NULL, null=True, blank=True, related_name='tracked_packages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['package_number']

    def __str__(self):
        return f"{self.package_number} - {self.shipment.tracking_id}"

    def save(self, *args, **kwargs):
        if not self.package_number:
            from core.utils import generate_document_number
            self.package_number = generate_document_number('PKG')
        super().save(*args, **kwargs)


class PackageItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hs_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['description']

    def __str__(self):
        return f"{self.description} (x{self.quantity})"
