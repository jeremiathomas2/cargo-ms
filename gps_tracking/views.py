from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta
import json

from .models import GPSDevice, GPSPosition, Geofence, GeofenceEvent, GPSAlert

ITEMS_PER_PAGE = 25


@login_required
def gps_dashboard(request):
    total_devices = GPSDevice.objects.filter(is_active=True).count()
    online_devices = GPSDevice.objects.filter(status='online', is_active=True).count()
    offline_devices = GPSDevice.objects.filter(status='offline', is_active=True).count()

    recent_alerts = GPSAlert.objects.filter(acknowledged=False).select_related('device').order_by('-created_at')[:10]

    now = timezone.now()
    recent_positions = GPSPosition.objects.filter(
        timestamp__gte=now - timedelta(hours=1)
    ).select_related('device').order_by('-timestamp')[:20]

    device_type_counts = list(
        GPSDevice.objects.filter(is_active=True)
        .values('device_type')
        .annotate(count=Count('id'))
    )

    return render(request, 'gps_tracking/dashboard.html', {
        'total_devices': total_devices,
        'online_devices': online_devices,
        'offline_devices': offline_devices,
        'recent_alerts': recent_alerts,
        'recent_positions': recent_positions,
        'device_type_counts': device_type_counts,
    })


@login_required
def device_list(request):
    queryset = GPSDevice.objects.select_related('assigned_vehicle', 'assigned_shipment')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    device_type = request.GET.get('type', '')

    if search:
        queryset = queryset.filter(
            Q(tracker_id__icontains=search) |
            Q(imei__icontains=search) |
            Q(serial_number__icontains=search) |
            Q(sim_number__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)
    if device_type:
        queryset = queryset.filter(device_type=device_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    devices = paginator.get_page(page)

    return render(request, 'gps_tracking/device_list.html', {
        'devices': devices,
        'search': search,
        'status_filter': status,
        'type_filter': device_type,
        'status_choices': GPSDevice.STATUS_CHOICES,
        'type_choices': GPSDevice.TYPE_CHOICES,
    })


@login_required
def device_detail(request, pk):
    device = get_object_or_404(
        GPSDevice.objects.select_related('assigned_vehicle', 'assigned_shipment'),
        pk=pk,
    )
    recent_positions = device.positions.all()[:50]
    recent_alerts = device.alerts.all()[:20]
    recent_geofence_events = device.geofence_events.select_related('geofence').all()[:20]

    return render(request, 'gps_tracking/device_detail.html', {
        'device': device,
        'recent_positions': recent_positions,
        'recent_alerts': recent_alerts,
        'recent_geofence_events': recent_geofence_events,
    })


@login_required
def live_tracking(request):
    devices = GPSDevice.objects.filter(
        status='online', is_active=True
    ).select_related('assigned_vehicle')

    device_data = []
    for d in devices:
        if d.last_latitude and d.last_longitude:
            device_data.append({
                'id': str(d.pk),
                'tracker_id': d.tracker_id,
                'lat': float(d.last_latitude),
                'lng': float(d.last_longitude),
                'speed': float(d.last_speed),
                'heading': float(d.last_heading),
                'vehicle': d.assigned_vehicle.registration_number if d.assigned_vehicle else '',
                'last_update': d.last_update.isoformat() if d.last_update else '',
            })

    geofences = Geofence.objects.filter(is_active=True)
    geofence_data = []
    for g in geofences:
        geofence_data.append({
            'id': str(g.pk),
            'name': g.name,
            'type': g.fence_type,
            'shape': g.shape,
            'center_lat': float(g.center_latitude) if g.center_latitude else None,
            'center_lng': float(g.center_longitude) if g.center_longitude else None,
            'radius': float(g.radius_meters),
            'polygon': g.polygon_coords,
        })

    return render(request, 'gps_tracking/live_tracking.html', {
        'devices_json': json.dumps(device_data),
        'geofences_json': json.dumps(geofence_data),
        'devices': devices,
    })


@login_required
def geofence_list(request):
    queryset = Geofence.objects.all()

    search = request.GET.get('q', '')
    fence_type = request.GET.get('type', '')

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    if fence_type:
        queryset = queryset.filter(fence_type=fence_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    geofences = paginator.get_page(page)

    return render(request, 'gps_tracking/geofence_list.html', {
        'geofences': geofences,
        'search': search,
        'type_filter': fence_type,
        'type_choices': Geofence.TYPE_CHOICES,
    })


@login_required
def gps_history(request):
    device_id = request.GET.get('device_id', '')
    hours = int(request.GET.get('hours', 24))

    devices = GPSDevice.objects.filter(is_active=True)
    positions = []
    selected_device = None

    if device_id:
        selected_device = get_object_or_404(GPSDevice, pk=device_id)
        since = timezone.now() - timedelta(hours=hours)
        positions = selected_device.positions.filter(timestamp__gte=since).order_by('timestamp')

    position_data = []
    for p in positions:
        position_data.append({
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'speed': float(p.speed),
            'heading': float(p.heading),
            'timestamp': p.timestamp.isoformat(),
        })

    return render(request, 'gps_tracking/gps_history.html', {
        'devices': devices,
        'selected_device': selected_device,
        'device_id': device_id,
        'hours': hours,
        'positions_json': json.dumps(position_data),
        'position_count': len(position_data),
    })


@login_required
def gps_ingest(request, tracker_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        device = GPSDevice.objects.get(tracker_id=tracker_id)
    except GPSDevice.DoesNotExist:
        return JsonResponse({'error': f'Device {tracker_id} not found'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    lat = data.get('lat') or data.get('latitude')
    lng = data.get('lng') or data.get('longitude')
    speed = data.get('speed', 0)
    heading = data.get('heading', 0)
    altitude = data.get('altitude', 0)
    battery = data.get('battery')
    ignition = data.get('ignition')
    timestamp_str = data.get('timestamp')

    if lat is None or lng is None:
        return JsonResponse({'error': 'lat and lng are required'}, status=400)

    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid lat/lng values'}, status=400)

    if timestamp_str:
        try:
            from django.utils.dateparse import parse_datetime
            timestamp = parse_datetime(timestamp_str)
            if timestamp is None:
                from datetime import datetime
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            timestamp = timezone.now()
    else:
        timestamp = timezone.now()

    position = GPSPosition.objects.create(
        device=device,
        latitude=lat,
        longitude=lng,
        speed=float(speed),
        heading=float(heading),
        altitude=float(altitude),
        battery_level=int(battery) if battery is not None else None,
        ignition=ignition,
        timestamp=timestamp,
        raw_data=data,
    )

    device.last_latitude = lat
    device.last_longitude = lng
    device.last_speed = float(speed)
    device.last_heading = float(heading)
    device.last_altitude = float(altitude)
    device.last_update = timestamp
    if battery is not None:
        device.battery_level = int(battery)
    device.status = 'online'
    device.save(update_fields=[
        'last_latitude', 'last_longitude', 'last_speed', 'last_heading',
        'last_altitude', 'last_update', 'battery_level', 'status',
    ])

    if device.battery_level < 20:
        GPSAlert.objects.get_or_create(
            device=device,
            alert_type='low_battery',
            acknowledged=False,
            defaults={'message': f'Low battery: {device.battery_level}%', 'severity': 'medium'},
        )

    return JsonResponse({
        'status': 'ok',
        'position_id': str(position.pk),
        'device': device.tracker_id,
    })


@login_required
def gps_positions_api(request, device_id):
    device = get_object_or_404(GPSDevice, pk=device_id)
    hours = int(request.GET.get('hours', 24))
    limit = int(request.GET.get('limit', 1000))

    since = timezone.now() - timedelta(hours=hours)
    positions = device.positions.filter(timestamp__gte=since).order_by('timestamp')[:limit]

    position_data = []
    for p in positions:
        position_data.append({
            'id': str(p.pk),
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'speed': float(p.speed),
            'heading': float(p.heading),
            'altitude': float(p.altitude),
            'battery': p.battery_level,
            'ignition': p.ignition,
            'timestamp': p.timestamp.isoformat(),
        })

    return JsonResponse({
        'device': device.tracker_id,
        'positions': position_data,
        'count': len(position_data),
    })
