from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from cargo.models import Shipment


def tracking_home(request):
    return render(request, 'public_tracking/home.html')


def tracking_result(request, tracking_id):
    shipment = Shipment.objects.filter(
        tracking_id=tracking_id,
        public_tracking_enabled=True,
        is_deleted=False,
    ).select_related('origin_branch', 'destination_branch').first()

    if not shipment:
        return render(request, 'public_tracking/result.html', {
            'tracking_id': tracking_id,
            'found': False,
        })

    status_timeline = shipment.status_history.order_by('created_at').values(
        'previous_status', 'new_status', 'location', 'reason', 'created_at'
    )

    public_timeline = []
    internal_statuses = {'sorted', 'loaded', 'customs_hold'}
    for entry in status_timeline:
        if entry['new_status'] not in internal_statuses:
            public_timeline.append({
                'status': entry['new_status'],
                'location': entry['location'],
                'description': entry['reason'],
                'timestamp': entry['created_at'],
            })

    context = {
        'found': True,
        'tracking_id': shipment.tracking_id,
        'status': shipment.status,
        'status_display': shipment.get_status_display(),
        'origin': shipment.origin,
        'destination': shipment.destination,
        'estimated_arrival': shipment.estimated_arrival,
        'actual_arrival': shipment.actual_arrival,
        'delivered_at': shipment.delivered_at,
        'num_packages': shipment.num_packages,
        'cargo_type': shipment.get_cargo_type_display(),
        'created_at': shipment.created_at,
        'timeline': public_timeline,
    }
    return render(request, 'public_tracking/result.html', context)
