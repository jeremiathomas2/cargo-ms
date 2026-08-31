from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import AuditLog

ITEMS_PER_PAGE = 50


@login_required
def audit_log_list(request):
    queryset = AuditLog.objects.select_related('actor', 'branch')

    action = request.GET.get('action', '')
    entity_type = request.GET.get('entity_type', '')
    actor_id = request.GET.get('actor', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('q', '')

    if action:
        queryset = queryset.filter(action=action)
    if entity_type:
        queryset = queryset.filter(entity_type__icontains=entity_type)
    if actor_id:
        queryset = queryset.filter(actor_id=actor_id)
    if date_from:
        queryset = queryset.filter(timestamp__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(timestamp__date__lte=date_to)
    if search:
        queryset = queryset.filter(
            Q(entity_str__icontains=search) |
            Q(entity_id__icontains=search) |
            Q(details__icontains=search)
        )

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    logs = paginator.get_page(page)

    from accounts.models import User
    actors = User.objects.filter(is_active=True).order_by('username')[:100]

    return render(request, 'audit/audit_log_list.html', {
        'logs': logs,
        'action': action,
        'entity_type': entity_type,
        'actor_id': actor_id,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
        'action_choices': AuditLog.ACTION_CHOICES,
        'actors': actors,
    })
