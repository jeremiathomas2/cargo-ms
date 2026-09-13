from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import ETAProjection, RouteOptimization, AnomalyDetection, DemandForecast, PricingRecommendation

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    projections = ETAProjection.objects.select_related("shipment").order_by("-created_at")[:8]
    optimizations = RouteOptimization.objects.select_related("trip").order_by("-created_at")[:8]
    anomalies = AnomalyDetection.objects.select_related("device").order_by("-detected_at")[:8]
    forecasts = DemandForecast.objects.select_related("route").order_by("-created_at")[:8]
    pricing = PricingRecommendation.objects.select_related("route").order_by("-created_at")[:8]

    return render(request, "ai_intelligence/dashboard.html", {
        "num_projections": ETAProjection.objects.count(),
        "num_anomalies_open": AnomalyDetection.objects.filter(acknowledged=False).count(),
        "num_optimizations": RouteOptimization.objects.count(),
        "num_pricing": PricingRecommendation.objects.filter(is_approved=False).count(),
        "projections": projections,
        "optimizations": optimizations,
        "anomalies": anomalies,
        "forecasts": forecasts,
        "pricing": pricing,
        "anomaly_types": AnomalyDetection.AnomalyType.choices,
        "severity_choices": AnomalyDetection.Severity.choices,
    })


@login_required
def eta_list(request):
    queryset = ETAProjection.objects.select_related("shipment").order_by("-created_at")
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(
            Q(shipment__tracking_id__icontains=q) | Q(model_version__icontains=q)
        )
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    projections = paginator.get_page(request.GET.get("page", 1))
    return render(request, "ai_intelligence/eta_list.html", {"projections": projections, "search": q})


@login_required
def anomaly_list(request):
    queryset = AnomalyDetection.objects.select_related("device")
    severity = request.GET.get("severity", "")
    anomaly_type = request.GET.get("type", "")
    if severity:
        queryset = queryset.filter(severity=severity)
    if anomaly_type:
        queryset = queryset.filter(anomaly_type=anomaly_type)
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    anomalies = paginator.get_page(request.GET.get("page", 1))
    return render(request, "ai_intelligence/anomaly_list.html", {
        "anomalies": anomalies,
        "severity_filter": severity,
        "type_filter": anomaly_type,
        "severity_choices": AnomalyDetection.Severity.choices,
        "anomaly_types": AnomalyDetection.AnomalyType.choices,
    })


@login_required
def optimization_list(request):
    queryset = RouteOptimization.objects.select_related("trip").order_by("-created_at")
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    optimizations = paginator.get_page(request.GET.get("page", 1))
    return render(request, "ai_intelligence/optimization_list.html", {"optimizations": optimizations})


@login_required
def pricing_list(request):
    queryset = PricingRecommendation.objects.select_related("route").order_by("-created_at")
    approved = request.GET.get("approved", "")
    if approved in ("0", "1"):
        queryset = queryset.filter(is_approved=(approved == "1"))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    pricing = paginator.get_page(request.GET.get("page", 1))
    for rec in pricing.object_list:
        rec.delta = rec.suggested_rate - rec.current_rate
    return render(request, "ai_intelligence/pricing_list.html", {
        "pricing": pricing,
        "approved_filter": approved,
    })