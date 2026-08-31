from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Delivery, DeliveryAttempt, ProofOfDelivery

ITEMS_PER_PAGE = 25


@login_required
def delivery_list(request):
    queryset = Delivery.objects.select_related('shipment', 'assigned_to', 'driver')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if search:
        from django.db.models import Q
        queryset = queryset.filter(
            Q(delivery_number__icontains=search) |
            Q(shipment__tracking_id__icontains=search) |
            Q(delivery_address__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    deliveries = paginator.get_page(page)

    return render(request, 'delivery/delivery_list.html', {
        'deliveries': deliveries,
        'search': search,
        'status_filter': status,
        'status_choices': Delivery.STATUS_CHOICES,
    })


@login_required
def delivery_detail(request, pk):
    delivery = get_object_or_404(
        Delivery.objects.select_related('shipment', 'assigned_to', 'driver'),
        pk=pk,
    )
    attempts = delivery.attempts.select_related('attempted_by', 'driver').all()
    pod = None
    if hasattr(delivery, 'proof_of_delivery'):
        pod = delivery.proof_of_delivery

    return render(request, 'delivery/delivery_detail.html', {
        'delivery': delivery,
        'attempts': attempts,
        'pod': pod,
    })


@login_required
def proof_of_delivery(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)

    if hasattr(delivery, 'proof_of_delivery'):
        messages.info(request, 'Proof of delivery already exists for this delivery.')
        return redirect('delivery:detail', pk=pk)

    if request.method == 'POST':
        recipient_name = request.POST.get('recipient_name', '').strip()
        recipient_phone = request.POST.get('recipient_phone', '').strip()
        otp_code = request.POST.get('otp_code', '').strip()
        notes = request.POST.get('notes', '')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not recipient_name:
            messages.error(request, 'Recipient name is required.')
            return redirect('delivery:pod', pk=pk)

        pod = ProofOfDelivery(
            delivery=delivery,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            otp_code=otp_code,
            otp_verified=bool(otp_code),
            notes=notes,
            delivered_by=request.user,
        )

        if latitude and longitude:
            try:
                pod.latitude = float(latitude)
                pod.longitude = float(longitude)
            except (TypeError, ValueError):
                pass

        signature = request.FILES.get('signature')
        if signature:
            pod.signature = signature

        photo = request.FILES.get('photo')
        if photo:
            pod.photo = photo

        pod.save()

        delivery.status = 'delivered'
        delivery.delivered_at = timezone.now()
        delivery.save()

        from cargo.models import Shipment, ShipmentStatusHistory, CargoEvent
        shipment = delivery.shipment
        old_status = shipment.status
        shipment.status = 'delivered'
        shipment.delivered_at = timezone.now()
        shipment.save()

        ShipmentStatusHistory.objects.create(
            shipment=shipment,
            previous_status=old_status,
            new_status='delivered',
            changed_by=request.user,
            reason='Proof of delivery recorded',
            source='manual',
        )
        CargoEvent.objects.create(
            shipment=shipment,
            event_type='status_change',
            description=f'Delivery confirmed. Recipient: {recipient_name}',
            created_by=request.user,
        )

        messages.success(request, 'Proof of delivery recorded successfully.')
        return redirect('delivery:detail', pk=pk)

    return render(request, 'delivery/proof_of_delivery.html', {
        'delivery': delivery,
    })


@login_required
def delivery_attempt(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('delivery:detail', pk=pk)

    result = request.POST.get('result', '')
    notes = request.POST.get('notes', '')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    next_attempt_date = request.POST.get('next_attempt_date')

    if not result:
        messages.error(request, 'Result is required.')
        return redirect('delivery:detail', pk=pk)

    attempt_number = delivery.attempts.count() + 1

    attempt = DeliveryAttempt(
        delivery=delivery,
        attempt_number=attempt_number,
        result=result,
        attempted_by=request.user,
        driver=delivery.driver,
        notes=notes,
    )

    if latitude and longitude:
        try:
            attempt.latitude = float(latitude)
            attempt.longitude = float(longitude)
        except (TypeError, ValueError):
            pass

    if next_attempt_date:
        try:
            from datetime import datetime
            attempt.next_attempt_date = datetime.strptime(next_attempt_date, '%Y-%m-%d').date()
        except ValueError:
            pass

    attempt.save()

    delivery.attempted_at = timezone.now()

    if result == 'successful':
        delivery.status = 'delivered'
        delivery.delivered_at = timezone.now()
    else:
        delivery.status = 'attempted'

    delivery.save()

    from cargo.models import CargoEvent
    CargoEvent.objects.create(
        shipment=delivery.shipment,
        event_type='note',
        description=f'Delivery attempt #{attempt_number}: {result}' + (f' - {notes}' if notes else ''),
        created_by=request.user,
    )

    messages.success(request, f'Delivery attempt #{attempt_number} recorded.')
    return redirect('delivery:detail', pk=pk)
