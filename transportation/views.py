from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count, Sum, Case, When, IntegerField, Value, F
from django.utils import timezone

from .models import Vehicle, Driver, Trip, Manifest, Route, RouteStop, ManifestShipment

try:
    from branches.models import Branch
except Exception:
    Branch = None

ITEMS_PER_PAGE = 15


def _qs_for_user(request, base_qs):
    if request.user.is_superuser:
        return base_qs
    if hasattr(request.user, 'branch') and request.user.branch_id:
        return base_qs.filter(Q(assigned_branch=request.user.branch) | Q(assigned_branch__isnull=True))
    return base_qs


@login_required
def vehicle_list(request):
    base_qs = Vehicle.objects.select_related('assigned_branch', 'gps_device').prefetch_related('drivers')
    base_qs = _qs_for_user(request, base_qs)

    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    vehicle_type = request.GET.get('type', '').strip()
    branch = request.GET.get('branch', '').strip()
    only_expiring = request.GET.get('expiring', '') == '1'

    queryset = base_qs
    if search:
        queryset = queryset.filter(
            Q(registration_number__icontains=search) |
            Q(make__icontains=search) |
            Q(model_name__icontains=search) |
            Q(assigned_branch__name__icontains=search) |
            Q(assigned_branch__code__icontains=search) |
            Q(drivers__first_name__icontains=search) |
            Q(drivers__last_name__icontains=search)
        ).distinct()
    if status:
        queryset = queryset.filter(status=status)
    if vehicle_type:
        queryset = queryset.filter(vehicle_type=vehicle_type)
    if branch and Branch:
        queryset = queryset.filter(Q(assigned_branch__id=branch) | Q(assigned_branch__code__iexact=branch))
    if only_expiring:
        today = timezone.now().date()
        horizon = today + timedelta(days=30)
        queryset = queryset.filter(
            Q(insurance_expiry__lte=horizon, insurance_expiry__gte=today) |
            Q(inspection_expiry__lte=horizon, inspection_expiry__gte=today) |
            Q(insurance_expiry__lt=today) |
            Q(inspection_expiry__lt=today)
        )

    status_counts = base_qs.aggregate(
        total=Count('id'),
        available=Count(Case(When(status='available', then=1), output_field=IntegerField())),
        on_route=Count(Case(When(status='on_route', then=1), output_field=IntegerField())),
        maintenance=Count(Case(When(status='maintenance', then=1), output_field=IntegerField())),
        retired=Count(Case(When(status='retired', then=1), output_field=IntegerField())),
    )
    type_counts = {row['vehicle_type']: row['count'] for row in
                   base_qs.order_by().values('vehicle_type').annotate(count=Count('id'))}
    type_counts_list = []
    for val, label in Vehicle.TYPE_CHOICES:
        c = type_counts.get(val, 0)
        type_counts_list.append({'value': val, 'label': label, 'count': c})

    totals = base_qs.aggregate(
        total_capacity_kg=Sum('max_capacity_kg', default=0),
        total_volume_m3=Sum('max_volume_m3', default=0),
        total_km=Sum('total_km', default=0),
        total_trips=Sum('total_trips', default=0),
        with_gps=Count(Case(When(gps_device__isnull=False, then=1), output_field=IntegerField())),
    )

    today = timezone.now().date()
    horizon = today + timedelta(days=30)
    expiring_raw = base_qs.filter(
        Q(insurance_expiry__lte=horizon, insurance_expiry__gte=today) |
        Q(inspection_expiry__lte=horizon, inspection_expiry__gte=today) |
        Q(insurance_expiry__lt=today) |
        Q(inspection_expiry__lt=today)
    ).order_by(
        Case(When(insurance_expiry__isnull=False, then='insurance_expiry'), default=F('inspection_expiry'))
    )[:8]
    expiring = list(expiring_raw)
    for v in expiring:
        v.insurance_soon = bool(v.insurance_expiry and v.insurance_expiry <= horizon)
        v.inspection_soon = bool(v.inspection_expiry and v.inspection_expiry <= horizon)

    branches = Branch.objects.all() if Branch else []

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    vehicles = paginator.get_page(page)

    for v in vehicles.object_list:
        trips = float(v.total_trips) if v.total_trips else 0.0
        km = float(v.total_km) if v.total_km else 0.0
        v.utilization_pct = min(100, int(trips * 100 / 90)) if trips > 0 else 0
        cap = 500000
        v.km_util = min(100, int(km / cap * 100)) if km > 0 else 0
        v.utilization_color = (
            'var(--success)' if v.utilization_pct >= 75 else
            'var(--info)' if v.utilization_pct >= 40 else
            'var(--text-faint)'
        )
        v.insurance_soon = bool(v.insurance_expiry and v.insurance_expiry <= horizon)
        v.inspection_soon = bool(v.inspection_expiry and v.inspection_expiry <= horizon)
        v.insurance_overdue = bool(v.insurance_expiry and v.insurance_expiry < today)
        v.inspection_overdue = bool(v.inspection_expiry and v.inspection_expiry < today)
        v.compliance_issue = (
            v.insurance_overdue or v.inspection_overdue or v.insurance_soon or v.inspection_soon
        )

    return render(request, 'transportation/vehicle_list.html', {
        'vehicles': vehicles,
        'search': search,
        'status_filter': status,
        'type_filter': vehicle_type,
        'branch_filter': branch,
        'only_expiring': only_expiring,
        'status_choices': Vehicle.STATUS_CHOICES,
        'type_choices': Vehicle.TYPE_CHOICES,
        'status_counts': status_counts,
        'type_counts': type_counts,
        'type_counts_list': type_counts_list,
        'totals': totals,
        'expiring': expiring,
        'branches': branches,
        'today': today,
        'horizon': horizon,
    })


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(
        Vehicle.objects.select_related('assigned_branch', 'gps_device'),
        pk=pk,
    )
    recent_trips = vehicle.trips.select_related('driver', 'route').order_by('-created_at')[:10]
    drivers = vehicle.drivers.filter(is_active=True)

    return render(request, 'transportation/vehicle_detail.html', {
        'vehicle': vehicle,
        'recent_trips': recent_trips,
        'drivers': drivers,
    })


@login_required
def driver_list(request):
    queryset = Driver.objects.select_related('assigned_vehicle', 'assigned_branch')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(license_number__icontains=search) |
            Q(phone__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    drivers = paginator.get_page(page)

    return render(request, 'transportation/driver_list.html', {
        'drivers': drivers,
        'search': search,
        'status_filter': status,
        'status_choices': Driver.STATUS_CHOICES,
    })


@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(
        Driver.objects.select_related('assigned_vehicle', 'assigned_branch', 'user'),
        pk=pk,
    )
    recent_trips = driver.trips.select_related('vehicle', 'route').order_by('-created_at')[:10]

    return render(request, 'transportation/driver_detail.html', {
        'driver': driver,
        'recent_trips': recent_trips,
    })


@login_required
def trip_list(request):
    queryset = Trip.objects.select_related('vehicle', 'driver', 'route', 'manifest', 'gps_device')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if search:
        queryset = queryset.filter(
            Q(trip_number__icontains=search) |
            Q(vehicle__registration_number__icontains=search) |
            Q(driver__first_name__icontains=search) |
            Q(driver__last_name__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    trips = paginator.get_page(page)

    return render(request, 'transportation/trip_list.html', {
        'trips': trips,
        'search': search,
        'status_filter': status,
        'status_choices': Trip.STATUS_CHOICES,
    })


@login_required
def trip_detail(request, pk):
    trip = get_object_or_404(
        Trip.objects.select_related('vehicle', 'driver', 'route', 'manifest', 'gps_device', 'created_by'),
        pk=pk,
    )
    trip_shipments = trip.shipments.select_related('customer').all()
    manifest_obj = None
    manifest_entries = []
    if hasattr(trip, 'manifest_detail') and trip.manifest_detail:
        manifest_obj = trip.manifest_detail
        manifest_entries = manifest_obj.manifest_shipments.select_related('shipment').all()

    route_stops = trip.route.stops.all() if trip.route else []

    return render(request, 'transportation/trip_detail.html', {
        'trip': trip,
        'trip_shipments': trip_shipments,
        'manifest': manifest_obj,
        'manifest_entries': manifest_entries,
        'route_stops': route_stops,
    })


@login_required
def manifest_list(request):
    queryset = Manifest.objects.select_related('vehicle', 'driver', 'trip', 'locked_by', 'created_by')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if search:
        queryset = queryset.filter(
            Q(manifest_number__icontains=search) |
            Q(vehicle__registration_number__icontains=search) |
            Q(driver__first_name__icontains=search) |
            Q(driver__last_name__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    manifests = paginator.get_page(page)

    return render(request, 'transportation/manifest_list.html', {
        'manifests': manifests,
        'search': search,
        'status_filter': status,
        'status_choices': Manifest.STATUS_CHOICES,
    })


@login_required
def manifest_detail(request, pk):
    manifest = get_object_or_404(
        Manifest.objects.select_related('vehicle', 'driver', 'trip', 'locked_by', 'created_by'),
        pk=pk,
    )
    manifest_shipments = manifest.manifest_shipments.select_related(
        'shipment', 'shipment__customer', 'loaded_by'
    ).all()

    return render(request, 'transportation/manifest_detail.html', {
        'manifest': manifest,
        'manifest_shipments': manifest_shipments,
    })


@login_required
def route_list(request):
    queryset = Route.objects.prefetch_related('stops')

    search = request.GET.get('q', '')
    route_type = request.GET.get('type', '')

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(origin__icontains=search) |
            Q(destination__icontains=search)
        )
    if route_type:
        queryset = queryset.filter(route_type=route_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    routes = paginator.get_page(page)

    return render(request, 'transportation/route_list.html', {
        'routes': routes,
        'search': search,
        'type_filter': route_type,
        'route_types': Route.ROUTE_TYPE_CHOICES,
    })
