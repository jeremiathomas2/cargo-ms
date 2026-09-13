from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import BorderPost, BorderCrossingEvent, CustomsDeclaration, CorridorRoute, RegionalAgent

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    border_posts = BorderPost.objects.all().order_by("name")
    declarations = CustomsDeclaration.objects.order_by("-created_at")[:8]
    crossings = BorderCrossingEvent.objects.select_related("border_post", "trip").order_by("-timestamp")[:8]
    corridors = CorridorRoute.objects.order_by("corridor_name")[:8]

    return render(request, "cross_border/dashboard.html", {
        "num_posts": border_posts.count(),
        "num_declarations": CustomsDeclaration.objects.count(),
        "pending_declarations": CustomsDeclaration.objects.filter(status="draft").count(),
        "num_crossings": BorderCrossingEvent.objects.count(),
        "border_posts": border_posts[:8],
        "declarations": declarations,
        "crossings": crossings,
        "corridors": corridors,
        "status_choices": CustomsDeclaration.Status.choices,
        "corridor_types": CorridorRoute.CorridorType.choices,
    })


@login_required
def border_post_list(request):
    queryset = BorderPost.objects.all()
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(code__icontains=q) | Q(country__icontains=q))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page", 1))
    return render(request, "cross_border/border_post_list.html", {"posts": posts, "search": q})


@login_required
def declaration_list(request):
    queryset = CustomsDeclaration.objects.select_related("shipment").order_by("-created_at")
    status = request.GET.get("status", "")
    if status:
        queryset = queryset.filter(status=status)
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(Q(declaration_number__icontains=q) | Q(hs_code__icontains=q) | Q(shipment__tracking_id__icontains=q))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    declarations = paginator.get_page(request.GET.get("page", 1))
    return render(request, "cross_border/declaration_list.html", {
        "declarations": declarations,
        "status_filter": status,
        "search": q,
        "status_choices": CustomsDeclaration.Status.choices,
    })


@login_required
def crossing_list(request):
    queryset = BorderCrossingEvent.objects.select_related("border_post", "trip", "shipment")
    event_type = request.GET.get("type", "")
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    crossings = paginator.get_page(request.GET.get("page", 1))
    return render(request, "cross_border/crossing_list.html", {
        "crossings": crossings,
        "type_filter": event_type,
        "event_types": BorderCrossingEvent.EventType.choices,
    })


@login_required
def corridor_list(request):
    queryset = CorridorRoute.objects.select_related("route").order_by("corridor_name")
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    corridors = paginator.get_page(request.GET.get("page", 1))
    return render(request, "cross_border/corridor_list.html", {"corridors": corridors})


@login_required
def agent_list(request):
    queryset = RegionalAgent.objects.order_by("name")
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(country__icontains=q) | Q(company__icontains=q))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    agents = paginator.get_page(request.GET.get("page", 1))
    return render(request, "cross_border/agent_list.html", {"agents": agents, "search": q})