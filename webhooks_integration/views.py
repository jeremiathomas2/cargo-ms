from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import WebhookSubscription, WebhookDelivery, IntegrationLog

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    subscriptions = WebhookSubscription.objects.select_related("organization").order_by("-created_at")[:8]
    deliveries = WebhookDelivery.objects.select_related("subscription").order_by("-created_at")[:8]
    logs = IntegrationLog.objects.select_related("organization").order_by("-created_at")[:8]

    return render(request, "webhooks_integration/dashboard.html", {
        "num_subscriptions": WebhookSubscription.objects.count(),
        "num_active": WebhookSubscription.objects.filter(is_active=True).count(),
        "num_failed": WebhookDelivery.objects.filter(delivered=False).count(),
        "num_logs": IntegrationLog.objects.count(),
        "subscriptions": subscriptions,
        "deliveries": deliveries,
        "logs": logs,
    })


@login_required
def subscription_list(request):
    queryset = WebhookSubscription.objects.select_related("organization").order_by("-created_at")
    active = request.GET.get("active", "")
    if active in ("0", "1"):
        queryset = queryset.filter(is_active=(active == "1"))
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(Q(url__icontains=q) | Q(organization__name__icontains=q) | Q(events__icontains=q))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    subscriptions = paginator.get_page(request.GET.get("page", 1))
    return render(request, "webhooks_integration/subscription_list.html", {
        "subscriptions": subscriptions,
        "active_filter": active,
        "search": q,
    })


@login_required
def delivery_list(request):
    queryset = WebhookDelivery.objects.select_related("subscription").order_by("-created_at")
    delivered = request.GET.get("delivered", "")
    if delivered in ("0", "1"):
        queryset = queryset.filter(delivered=(delivered == "1"))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    deliveries = paginator.get_page(request.GET.get("page", 1))
    return render(request, "webhooks_integration/delivery_list.html", {
        "deliveries": deliveries,
        "delivered_filter": delivered,
    })


@login_required
def log_list(request):
    queryset = IntegrationLog.objects.select_related("organization").order_by("-created_at")
    direction = request.GET.get("direction", "")
    status = request.GET.get("status", "")
    if direction:
        queryset = queryset.filter(direction=direction)
    if status:
        queryset = queryset.filter(status=status)
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(Q(integration_name__icontains=q) | Q(organization__name__icontains=q))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    logs = paginator.get_page(request.GET.get("page", 1))
    return render(request, "webhooks_integration/log_list.html", {
        "logs": logs,
        "direction_filter": direction,
        "status_filter": status,
        "search": q,
        "direction_choices": IntegrationLog.Direction.choices,
    })