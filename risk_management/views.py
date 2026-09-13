from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import SLALevel, SLABreach, Watchlist, RiskScore

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    breaches = SLABreach.objects.select_related("shipment", "sla_level").order_by("-created_at")[:8]
    watchlist = Watchlist.objects.select_related("added_by").order_by("-added_at")[:8]
    risks = RiskScore.objects.select_related("shipment").order_by("-created_at")[:8]

    open_breaches = SLABreach.objects.filter(resolved=False)
    high_risk = sum(1 for r in RiskScore.objects.all() if r.risk_score >= 70)

    return render(request, "risk_management/dashboard.html", {
        "num_breaches": open_breaches.filter(severity__in=["critical", "major"]).count(),
        "num_open_breaches": open_breaches.count(),
        "num_watchlist": Watchlist.objects.filter(is_active=True).count(),
        "num_high_risk": high_risk,
        "breaches": breaches,
        "watchlist": watchlist,
        "risks": risks,
        "severity_choices": SLABreach.Severity.choices,
    })


@login_required
def breach_list(request):
    queryset = SLABreach.objects.select_related("shipment", "sla_level")
    severity = request.GET.get("severity", "")
    resolved = request.GET.get("resolved", "")
    if severity:
        queryset = queryset.filter(severity=severity)
    if resolved in ("0", "1"):
        queryset = queryset.filter(resolved=(resolved == "1"))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    breaches = paginator.get_page(request.GET.get("page", 1))
    return render(request, "risk_management/breach_list.html", {
        "breaches": breaches,
        "severity_filter": severity,
        "resolved_filter": resolved,
        "severity_choices": SLABreach.Severity.choices,
    })


@login_required
def watchlist_list(request):
    queryset = Watchlist.objects.select_related("added_by")
    active = request.GET.get("active", "")
    if active in ("0", "1"):
        queryset = queryset.filter(is_active=(active == "1"))
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(Q(entity_value__icontains=q) | Q(reason__icontains=q))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    items = paginator.get_page(request.GET.get("page", 1))
    return render(request, "risk_management/watchlist_list.html", {
        "items": items,
        "active_filter": active,
        "search": q,
    })


@login_required
def risk_score_list(request):
    queryset = RiskScore.objects.select_related("shipment").order_by("-created_at")
    reviewed = request.GET.get("reviewed", "")
    if reviewed in ("0", "1"):
        queryset = queryset.filter(reviewed=(reviewed == "1"))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    risks = paginator.get_page(request.GET.get("page", 1))
    return render(request, "risk_management/risk_score_list.html", {
        "risks": risks,
        "reviewed_filter": reviewed,
    })


@login_required
def sla_level_list(request):
    levels = SLALevel.objects.order_by("name")
    return render(request, "risk_management/sla_level_list.html", {"levels": levels})