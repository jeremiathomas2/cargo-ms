from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from .models import Vehicle, Driver, Trip, Manifest, Route, RouteStop, ManifestShipment

ITEMS_PER_PAGE = 25


@login_required
def vehicle_list(request):
    queryset = Vehicle.objects.select_related('assigned_branch', 'gps_device')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    vehicle_type = request.GET.get('type', '')

    if search:
        queryset = queryset.filter(
            Q(registration_number__icontains=search) |
            Q(make__icontains=search) |
            Q(model_name__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)
    if vehicle_type:
        queryset = queryset.filter(vehicle_type=vehicle_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    vehicles = paginator.get_page(page)

    return render(request, 'transportation/vehicle_list.html', {
        'vehicles': vehicles,
        'search': search,
        'status_filter': status,
        'type_filter': vehicle_type,
        'status_choices': Vehicle.STATUS_CHOICES,
        'type_choices': Vehicle.TYPE_CHOICES,
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
