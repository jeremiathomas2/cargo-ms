from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import DriverScorecard, VehicleMaintenance, FuelLog, CarbonEmission

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    scorecards = DriverScorecard.objects.select_related("driver").order_by("-period_end")[:8]
    maintenance = VehicleMaintenance.objects.select_related("vehicle").order_by("-created_at")[:8]
    fuel = FuelLog.objects.select_related("vehicle").order_by("-date")[:8]
    emissions = CarbonEmission.objects.select_related("vehicle").order_by("-created_at")[:8]

    return render(request, "fleet_intelligence/dashboard.html", {
        "num_scorecards": DriverScorecard.objects.count(),
        "num_maintenance": VehicleMaintenance.objects.filter(status__in=["scheduled", "in_progress"]).count(),
        "num_fuel": FuelLog.objects.count(),
        "num_emissions": CarbonEmission.objects.count(),
        "scorecards": scorecards,
        "maintenance": maintenance,
        "fuel": fuel,
        "emissions": emissions,
    })


@login_required
def scorecard_list(request):
    queryset = DriverScorecard.objects.select_related("driver").order_by("-period_end")
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(
            Q(driver__first_name__icontains=q) |
            Q(driver__last_name__icontains=q) |
            Q(driver__license_number__icontains=q)
        )
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    scorecards = paginator.get_page(request.GET.get("page", 1))
    return render(request, "fleet_intelligence/scorecard_list.html", {"scorecards": scorecards, "search": q})


@login_required
def maintenance_list(request):
    queryset = VehicleMaintenance.objects.select_related("vehicle").order_by("-created_at")
    status = request.GET.get("status", "")
    mtype = request.GET.get("type", "")
    if status:
        queryset = queryset.filter(status=status)
    if mtype:
        queryset = queryset.filter(maintenance_type=mtype)
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    records = paginator.get_page(request.GET.get("page", 1))
    return render(request, "fleet_intelligence/maintenance_list.html", {
        "records": records,
        "status_filter": status,
        "type_filter": mtype,
        "status_choices": VehicleMaintenance.Status.choices,
        "type_choices": VehicleMaintenance.MaintenanceType.choices,
    })


@login_required
def fuel_log_list(request):
    queryset = FuelLog.objects.select_related("vehicle").order_by("-date")
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    logs = paginator.get_page(request.GET.get("page", 1))
    return render(request, "fleet_intelligence/fuel_log_list.html", {"logs": logs})


@login_required
def emission_list(request):
    queryset = CarbonEmission.objects.select_related("vehicle", "shipment").order_by("-created_at")
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    emissions = paginator.get_page(request.GET.get("page", 1))
    return render(request, "fleet_intelligence/emission_list.html", {"emissions": emissions})