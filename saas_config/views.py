from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Organization, OrganizationDomain, TenantQuota

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    organizations = Organization.objects.order_by("name")
    quota = TenantQuota.objects.all()

    total_shipments_used = sum(q.shipments_used for q in quota)
    total_users_used = sum(q.users_used for q in quota)
    total_api_used = sum(q.api_requests_used for q in quota)

    return render(request, "saas_config/dashboard.html", {
        "num_organizations": organizations.count(),
        "num_active": organizations.filter(is_active=True).count(),
        "num_quota": quota.count(),
        "total_users_used": total_users_used,
        "total_shipments_used": total_shipments_used,
        "total_api_used": total_api_used,
        "organizations": organizations[:8],
        "plan_choices": Organization.Plan.choices,
    })


@login_required
def organization_list(request):
    queryset = Organization.objects.order_by("name")
    q = request.GET.get("q", "")
    plan = request.GET.get("plan", "")
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(subdomain__icontains=q) | Q(slug__icontains=q))
    if plan:
        queryset = queryset.filter(plan=plan)
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    organizations = paginator.get_page(request.GET.get("page", 1))
    return render(request, "saas_config/organization_list.html", {
        "organizations": organizations,
        "search": q,
        "plan_filter": plan,
        "plan_choices": Organization.Plan.choices,
    })


@login_required
def organization_detail(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    domains = org.domains.all()
    quota = getattr(org, "quota", None)
    webhooks = org.webhook_subscriptions.all()[:10]
    agents = org.regional_agents.all()[:10]
    return render(request, "saas_config/organization_detail.html", {
        "org": org,
        "domains": domains,
        "quota": quota,
        "webhooks": webhooks,
        "agents": agents,
    })