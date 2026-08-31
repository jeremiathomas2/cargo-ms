from rest_framework import serializers
from cargo.models import Shipment, ShipmentStatusHistory, CargoEvent
from packages.models import Package
from customers.models import Customer
from transportation.models import Vehicle, Driver, Trip, Manifest, Route
from warehouse.models import Warehouse
from gps_tracking.models import GPSDevice, GPSPosition, Geofence
from delivery.models import Delivery
from billing.models import Invoice, InvoiceItem
from payments.models import Payment
from documents.models import Document
from notifications.models import Notification
from claims.models import Claim
from branches.models import Branch


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'


class ShipmentStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentStatusHistory
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    shipment_tracking = serializers.CharField(source='shipment.tracking_id', read_only=True)

    class Meta:
        model = Package
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Driver
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class TripSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.registration_number', read_only=True)
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)

    class Meta:
        model = Trip
        fields = '__all__'


class ManifestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = '__all__'


class WarehouseSerializer(serializers.ModelSerializer):
    utilization_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = Warehouse
        fields = '__all__'


class GPSDeviceSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(read_only=True)

    class Meta:
        model = GPSDevice
        fields = '__all__'


class GPSPositionSerializer(serializers.ModelSerializer):
    device_tracker = serializers.CharField(source='device.tracker_id', read_only=True)

    class Meta:
        model = GPSPosition
        fields = '__all__'


class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):
    shipment_tracking = serializers.CharField(source='shipment.tracking_id', read_only=True)

    class Meta:
        model = Delivery
        fields = '__all__'


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class ClaimSerializer(serializers.ModelSerializer):
    shipment_tracking = serializers.CharField(source='shipment.tracking_id', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = Claim
        fields = '__all__'
