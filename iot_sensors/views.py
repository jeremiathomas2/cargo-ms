from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import SensorDevice, SensorReading, SensorAlert

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    devices = SensorDevice.objects.select_related("shipment", "package").all()
    alerts = SensorAlert.objects.select_related("sensor").order_by("-created_at")[:10]

    num_devices = devices.count()
    num_active = devices.filter(is_active=True).count()
    num_alerts_open = SensorAlert.objects.filter(acknowledged=False).count()
    low_battery = devices.filter(battery_level__lt=20).count()

    recent_readings = SensorReading.objects.select_related("sensor").order_by("-timestamp")[:10]

    return render(request, "iot_sensors/dashboard.html", {
        "num_devices": num_devices,
        "num_active": num_active,
        "num_alerts_open": num_alerts_open,
        "low_battery": low_battery,
        "devices": devices[:8],
        "alerts": alerts,
        "recent_readings": recent_readings,
        "sensor_types": SensorDevice.SensorType.choices,
    })


@login_required
def sensor_list(request):
    queryset = SensorDevice.objects.select_related("shipment", "package")

    search = request.GET.get("q", "")
    sensor_type = request.GET.get("type", "")
    if search:
        queryset = queryset.filter(
            Q(tracker_id__icontains=search) |
            Q(serial_number__icontains=search) |
            Q(shipment__tracking_id__icontains=search)
        )
    if sensor_type:
        queryset = queryset.filter(sensor_type=sensor_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    devices = paginator.get_page(request.GET.get("page", 1))

    return render(request, "iot_sensors/sensor_list.html", {
        "devices": devices,
        "search": search,
        "type_filter": sensor_type,
        "type_choices": SensorDevice.SensorType.choices,
    })


@login_required
def sensor_detail(request, pk):
    device = get_object_or_404(
        SensorDevice.objects.select_related("shipment", "package"), pk=pk
    )
    readings = device.readings.order_by("-timestamp")[:50]
    alerts = device.alerts.order_by("-created_at")[:20]

    return render(request, "iot_sensors/sensor_detail.html", {
        "device": device,
        "readings": readings,
        "alerts": alerts,
    })


@login_required
def alert_list(request):
    queryset = SensorAlert.objects.select_related("sensor", "acknowledged_by")

    severity = request.GET.get("severity", "")
    acknowledged = request.GET.get("acknowledged", "")
    if severity:
        queryset = queryset.filter(severity=severity)
    if acknowledged in ("0", "1"):
        queryset = queryset.filter(acknowledged=(acknowledged == "1"))

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    alerts = paginator.get_page(request.GET.get("page", 1))

    return render(request, "iot_sensors/alert_list.html", {
        "alerts": alerts,
        "severity_filter": severity,
        "ack_filter": acknowledged,
        "severity_choices": SensorAlert.Severity.choices,
    })