from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from core.permissions import IsSuperAdmin, IsAdminUser

from cargo.models import Shipment
from packages.models import Package
from customers.models import Customer
from transportation.models import Vehicle, Driver, Trip, Manifest
from warehouse.models import Warehouse
from gps_tracking.models import GPSDevice, GPSPosition, Geofence
from delivery.models import Delivery
from billing.models import Invoice
from payments.models import Payment
from documents.models import Document
from notifications.models import Notification
from claims.models import Claim
from branches.models import Branch

from .serializers import (
    ShipmentSerializer, PackageSerializer, CustomerSerializer,
    VehicleSerializer, DriverSerializer, TripSerializer,
    ManifestSerializer, WarehouseSerializer, GPSDeviceSerializer,
    GPSPositionSerializer, GeofenceSerializer, DeliverySerializer,
    InvoiceSerializer, PaymentSerializer, DocumentSerializer,
    NotificationSerializer, ClaimSerializer, BranchSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.filter(is_deleted=False).select_related('customer')
    serializer_class = ShipmentSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '')
        status_param = self.request.query_params.get('status', '')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(tracking_id__icontains=search) |
                Q(booking_number__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search)
            )
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.select_related('shipment')
    serializer_class = PackageSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(package_number__icontains=search) |
                Q(barcode__icontains=search) |
                Q(shipment__tracking_id__icontains=search)
            )
        return qs


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(customer_number__icontains=search)
            )
        return qs


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related('assigned_branch')
    serializer_class = VehicleSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '')
        status_param = self.request.query_params.get('status', '')
        if search:
            qs = qs.filter(registration_number__icontains=search)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.select_related('assigned_vehicle')
    serializer_class = DriverSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search)
            )
        return qs


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('vehicle', 'driver', 'route')
    serializer_class = TripSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status', '')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class ManifestViewSet(viewsets.ModelViewSet):
    queryset = Manifest.objects.select_related('vehicle', 'driver', 'trip')
    serializer_class = ManifestSerializer
    pagination_class = StandardPagination


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.select_related('branch', 'manager')
    serializer_class = WarehouseSerializer
    pagination_class = StandardPagination


class GPSDeviceViewSet(viewsets.ModelViewSet):
    queryset = GPSDevice.objects.select_related('assigned_vehicle', 'assigned_shipment')
    serializer_class = GPSDeviceSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status', '')
        device_type = self.request.query_params.get('type', '')
        if status_param:
            qs = qs.filter(status=status_param)
        if device_type:
            qs = qs.filter(device_type=device_type)
        return qs


class GPSPositionViewSet(viewsets.ModelViewSet):
    queryset = GPSPosition.objects.select_related('device')
    serializer_class = GPSPositionSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        device_id = self.request.query_params.get('device_id', '')
        if device_id:
            qs = qs.filter(device_id=device_id)
        return qs


class GeofenceViewSet(viewsets.ModelViewSet):
    queryset = Geofence.objects.all()
    serializer_class = GeofenceSerializer
    pagination_class = StandardPagination


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.select_related('shipment', 'driver')
    serializer_class = DeliverySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status', '')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('customer', 'shipment')
    serializer_class = InvoiceSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status', '')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('customer', 'invoice', 'payment_method')
    serializer_class = PaymentSerializer
    pagination_class = StandardPagination


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('template', 'shipment', 'customer')
    serializer_class = DocumentSerializer
    pagination_class = StandardPagination


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related('recipient')
    serializer_class = NotificationSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'pk'):
            if not self.request.user.is_superuser:
                qs = qs.filter(recipient=self.request.user)
        return qs


class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.select_related('shipment', 'customer')
    serializer_class = ClaimSerializer
    pagination_class = StandardPagination


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.select_related('manager')
    serializer_class = BranchSerializer
    pagination_class = StandardPagination


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    try:
        data = json.loads(request.body) if hasattr(request, 'body') else request.data
    except (json.JSONDecodeError, Exception):
        return Response({'error': 'Invalid JSON'}, status=400)

    email = data.get('email', '')
    password = data.get('password', '')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=400)

    from accounts.models import User
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=401)

    if not user.check_password(password):
        return Response({'error': 'Invalid credentials'}, status=401)

    if not user.is_active:
        return Response({'error': 'Account is disabled'}, status=403)

    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.pk),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': str(user.role) if user.role else None,
            },
        })
    except ImportError:
        return Response({
            'access': 'demo-token-' + str(user.pk),
            'refresh': 'demo-refresh-' + str(user.pk),
            'user': {
                'id': str(user.pk),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
        })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        data = json.loads(request.body) if hasattr(request, 'body') else request.data
    except (json.JSONDecodeError, Exception):
        return Response({'error': 'Invalid JSON'}, status=400)

    refresh_token_str = data.get('refresh', '')
    if not refresh_token_str:
        return Response({'error': 'Refresh token is required'}, status=400)

    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken(refresh_token_str)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    except ImportError:
        return Response({'error': 'JWT library not installed'}, status=500)
    except Exception:
        return Response({'error': 'Invalid or expired refresh token'}, status=401)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def public_tracking_api(request, tracking_id):
    from cargo.models import Shipment as CargoShipment

    shipment = CargoShipment.objects.filter(
        tracking_id=tracking_id,
        public_tracking_enabled=True,
        is_deleted=False,
    ).first()

    if not shipment:
        return Response({'error': 'Shipment not found', 'tracking_id': tracking_id}, status=404)

    status_timeline = shipment.status_history.order_by('created_at').values(
        'new_status', 'location', 'reason', 'created_at'
    )

    internal_statuses = {'sorted', 'loaded'}
    timeline = []
    for entry in status_timeline:
        if entry['new_status'] not in internal_statuses:
            timeline.append({
                'status': entry['new_status'],
                'location': entry.get('location', ''),
                'description': entry.get('reason', ''),
                'timestamp': entry['created_at'].isoformat() if entry['created_at'] else None,
            })

    return Response({
        'tracking_id': shipment.tracking_id,
        'status': shipment.status,
        'status_display': shipment.get_status_display(),
        'origin': shipment.origin,
        'destination': shipment.destination,
        'estimated_arrival': shipment.estimated_arrival.isoformat() if shipment.estimated_arrival else None,
        'delivered_at': shipment.delivered_at.isoformat() if shipment.delivered_at else None,
        'num_packages': shipment.num_packages,
        'cargo_type': shipment.get_cargo_type_display(),
        'timeline': timeline,
    })


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok'})


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def health_db(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return Response({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return Response({'status': 'error', 'database': str(e)}, status=500)
