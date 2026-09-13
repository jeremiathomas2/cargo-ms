from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import USSDSession, IVRCall, OfflineSyncQueue, Translation

ITEMS_PER_PAGE = 25


@login_required
def dashboard(request):
    ussd = USSDSession.objects.order_by("-created_at")[:8]
    ivr = IVRCall.objects.order_by("-created_at")[:8]
    sync = OfflineSyncQueue.objects.select_related("user").order_by("-created_at")[:8]

    return render(request, "access_channels/dashboard.html", {
        "num_ussd": USSDSession.objects.count(),
        "num_ivr": IVRCall.objects.count(),
        "num_sync_pending": OfflineSyncQueue.objects.filter(synced=False).count(),
        "num_languages": Translation.objects.values("language_code").distinct().count(),
        "ussd": ussd,
        "ivr": ivr,
        "sync": sync,
        "ussd_statuses": USSDSession.Status.choices,
        "ivr_statuses": IVRCall.Status.choices,
    })


@login_required
def ussd_list(request):
    queryset = USSDSession.objects.order_by("-created_at")
    status = request.GET.get("status", "")
    if status:
        queryset = queryset.filter(status=status)
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(
            Q(session_id__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(tracking_number__icontains=q)
        )
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    sessions = paginator.get_page(request.GET.get("page", 1))
    return render(request, "access_channels/ussd_list.html", {
        "sessions": sessions,
        "status_filter": status,
        "search": q,
        "status_choices": USSDSession.Status.choices,
    })


@login_required
def ivr_list(request):
    queryset = IVRCall.objects.order_by("-created_at")
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    calls = paginator.get_page(request.GET.get("page", 1))
    return render(request, "access_channels/ivr_list.html", {"calls": calls})


@login_required
def sync_queue_list(request):
    queryset = OfflineSyncQueue.objects.select_related("user").order_by("-created_at")
    synced = request.GET.get("synced", "")
    if synced in ("0", "1"):
        queryset = queryset.filter(synced=(synced == "1"))
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    items = paginator.get_page(request.GET.get("page", 1))
    return render(request, "access_channels/sync_queue_list.html", {
        "items": items,
        "synced_filter": synced,
    })


@login_required
def translation_list(request):
    queryset = Translation.objects.order_by("language_code", "key")
    lang = request.GET.get("lang", "")
    if lang:
        queryset = queryset.filter(language_code=lang)
    q = request.GET.get("q", "")
    if q:
        queryset = queryset.filter(Q(key__icontains=q) | Q(value__icontains=q))
    languages = Translation.objects.values_list("language_code", flat=True).distinct()[:20]
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    translations = paginator.get_page(request.GET.get("page", 1))
    return render(request, "access_channels/translation_list.html", {
        "translations": translations,
        "lang_filter": lang,
        "search": q,
        "languages": languages,
    })