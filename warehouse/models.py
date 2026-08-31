import uuid
from django.db import models


class Warehouse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='warehouses')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='warehouses')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacity = models.PositiveIntegerField(default=1000, help_text='Max package capacity')
    current_occupancy = models.PositiveIntegerField(default=0)
    manager = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_warehouses')
    is_active = models.BooleanField(default=True)
    temperature_controlled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def utilization_percent(self):
        return (self.current_occupancy / self.capacity * 100) if self.capacity else 0


class WarehouseZone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    zone_type = models.CharField(max_length=20, choices=[
        ('storage', 'Storage'), ('receiving', 'Receiving'), ('dispatch', 'Dispatch'),
        ('sorting', 'Sorting'), ('hazmat', 'Hazmat'), ('cold', 'Cold Storage'),
    ], default='storage')
    capacity = models.PositiveIntegerField(default=500)
    current_occupancy = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('warehouse', 'code')
        ordering = ['code']

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"


class WarehouseShelf(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, related_name='shelves')
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    max_bins = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('zone', 'code')
        ordering = ['code']

    def __str__(self):
        return f"{self.zone} - {self.name}"


class WarehouseBin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shelf = models.ForeignKey(WarehouseShelf, on_delete=models.CASCADE, related_name='bins')
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    max_capacity = models.PositiveIntegerField(default=50)
    current_occupancy = models.PositiveIntegerField(default=0)
    is_occupied = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shelf', 'code')
        ordering = ['code']

    def __str__(self):
        return f"{self.shelf} - {self.name}"


class WarehouseMovement(models.Model):
    MOVEMENT_TYPES = [
        ('receiving', 'Receiving'), ('putaway', 'Put-away'),
        ('internal', 'Internal Move'), ('picking', 'Picking'),
        ('dispatch', 'Dispatch'), ('return', 'Return'),
        ('stocktake', 'Stocktake'), ('adjustment', 'Adjustment'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.CASCADE, null=True, blank=True, related_name='warehouse_movements')
    package = models.ForeignKey('packages.Package', on_delete=models.CASCADE, null=True, blank=True, related_name='warehouse_movements')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPES)
    from_zone = models.ForeignKey(WarehouseZone, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_from_zone')
    from_shelf = models.ForeignKey(WarehouseShelf, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_from_shelf')
    from_bin = models.ForeignKey(WarehouseBin, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_from_bin')
    to_zone = models.ForeignKey(WarehouseZone, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_to_zone')
    to_shelf = models.ForeignKey(WarehouseShelf, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_to_shelf')
    to_bin = models.ForeignKey(WarehouseBin, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_to_bin')
    scanned_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    barcode_scan = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type} - {self.shipment or self.package}"
