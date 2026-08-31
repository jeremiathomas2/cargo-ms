from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import Shipment, ShipmentStatusHistory, CargoEvent, CargoNote

VALID_TRANSITIONS = {
    'booked': ['awaiting_receiving', 'cancelled'],
    'awaiting_receiving': ['received', 'cancelled'],
    'received': ['in_warehouse'],
    'in_warehouse': ['sorted', 'ready_for_dispatch'],
    'sorted': ['ready_for_dispatch'],
    'ready_for_dispatch': ['loaded'],
    'loaded': ['in_transit'],
    'in_transit': ['arrived_destination', 'customs_hold'],
    'arrived_destination': ['ready_for_delivery', 'customs_hold'],
    'customs_hold': ['in_transit', 'ready_for_delivery'],
    'ready_for_delivery': ['out_for_delivery'],
    'out_for_delivery': ['delivery_attempted', 'delivered'],
    'delivery_attempted': ['out_for_delivery', 'delivered', 'returned'],
    'delivered': [],
    'returned': [],
    'lost': [],
    'damaged': [],
    'cancelled': [],
}

ITEMS_PER_PAGE = 25


@login_required
def shipment_list(request):
    queryset = Shipment.objects.filter(is_deleted=False).select_related('customer', 'origin_branch', 'destination_branch')

    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')
    cargo_type = request.GET.get('cargo_type', '')
    priority = request.GET.get('priority', '')

    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if search:
        queryset = queryset.filter(
            Q(tracking_id__icontains=search) |
            Q(booking_number__icontains=search) |
            Q(waybill_number__icontains=search) |
            Q(sender_name__icontains=search) |
            Q(receiver_name__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer__company_name__icontains=search)
        )
    if cargo_type:
        queryset = queryset.filter(cargo_type=cargo_type)
    if priority:
        queryset = queryset.filter(priority=priority)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    shipments = paginator.get_page(page)

    # Get all possible status choices
    all_statuses = [status for status, _ in Shipment.STATUS_CHOICES]
    
    # Get actual counts from database
    actual_counts = dict(
        Shipment.objects.filter(is_deleted=False)
        .values_list('status')
        .annotate(count=Count('id'))
        .values_list('status', 'count')
    )
    
    # Ensure all statuses are present in the dictionary with default 0
    status_counts = {status: actual_counts.get(status, 0) for status in all_statuses}

    return render(request, 'cargo/shipment_list.html', {
        'shipments': shipments,
        'status_filter': status_filter,
        'search': search,
        'cargo_type': cargo_type,
        'priority': priority,
        'status_counts': status_counts,
        'status_choices': Shipment.STATUS_CHOICES,
        'cargo_type_choices': Shipment.CARGO_TYPE_CHOICES,
        'priority_choices': Shipment.PRIORITY_CHOICES,
    })


@login_required
def shipment_create(request):
    from customers.models import Customer
    from branches.models import Branch
    from transportation.models import Route

    if request.method == 'POST':
        try:
            customer = Customer.objects.get(pk=request.POST.get('customer'))

            shipment = Shipment(
                customer=customer,
                created_by=request.user,
                sender_name=request.POST.get('sender_name', ''),
                sender_phone=request.POST.get('sender_phone', ''),
                sender_address=request.POST.get('sender_address', ''),
                sender_city=request.POST.get('sender_city', ''),
                receiver_name=request.POST.get('receiver_name', ''),
                receiver_phone=request.POST.get('receiver_phone', ''),
                receiver_address=request.POST.get('receiver_address', ''),
                receiver_city=request.POST.get('receiver_city', ''),
                origin=request.POST.get('origin', ''),
                destination=request.POST.get('destination', ''),
                cargo_type=request.POST.get('cargo_type', 'general'),
                description=request.POST.get('description', ''),
                num_packages=int(request.POST.get('num_packages', 1)),
                actual_weight=float(request.POST.get('actual_weight', 0)),
                volumetric_weight=float(request.POST.get('volumetric_weight', 0)),
                charged_weight=float(request.POST.get('charged_weight', 0)),
                declared_value=float(request.POST.get('declared_value', 0)),
                is_insured=request.POST.get('is_insured') == 'on',
                insurance_amount=float(request.POST.get('insurance_amount', 0)),
                pickup_required=request.POST.get('pickup_required') == 'on',
                delivery_required=request.POST.get('delivery_required', 'on') == 'on',
                special_handling=request.POST.get('special_handling', ''),
                is_fragile=request.POST.get('is_fragile') == 'on',
                is_perishable=request.POST.get('is_perishable') == 'on',
                is_hazardous=request.POST.get('is_hazardous') == 'on',
                priority=request.POST.get('priority', 'normal'),
                shipping_cost=float(request.POST.get('shipping_cost', 0)),
                handling_fee=float(request.POST.get('handling_fee', 0)),
                insurance_fee=float(request.POST.get('insurance_fee', 0)),
                total_cost=float(request.POST.get('total_cost', 0)),
                status='booked',
            )

            origin_branch_id = request.POST.get('origin_branch')
            if origin_branch_id:
                shipment.origin_branch = Branch.objects.get(pk=origin_branch_id)

            dest_branch_id = request.POST.get('destination_branch')
            if dest_branch_id:
                shipment.destination_branch = Branch.objects.get(pk=dest_branch_id)

            route_id = request.POST.get('route')
            if route_id:
                shipment.route = Route.objects.get(pk=route_id)

            shipment.save()

            ShipmentStatusHistory.objects.create(
                shipment=shipment,
                previous_status='',
                new_status='booked',
                changed_by=request.user,
                reason='Shipment booked',
                source='manual',
            )

            CargoEvent.objects.create(
                shipment=shipment,
                event_type='status_change',
                description=f'Shipment booked with tracking ID {shipment.tracking_id}',
                created_by=request.user,
            )

            messages.success(request, f'Shipment {shipment.tracking_id} created successfully.')
            return redirect('cargo:detail', pk=shipment.pk)

        except Customer.DoesNotExist:
            messages.error(request, 'Invalid customer selected.')
        except Exception as e:
            messages.error(request, f'Error creating shipment: {str(e)}')

    customers = Customer.objects.filter(status='active')
    branches = Branch.objects.filter(is_active=True)
    routes = Route.objects.filter(is_active=True)

    return render(request, 'cargo/shipment_form.html', {
        'customers': customers,
        'branches': branches,
        'routes': routes,
        'cargo_type_choices': Shipment.CARGO_TYPE_CHOICES,
        'priority_choices': Shipment.PRIORITY_CHOICES,
        'editing': False,
    })


@login_required
def shipment_detail(request, pk):
    shipment = get_object_or_404(
        Shipment.objects.select_related(
            'customer', 'origin_branch', 'destination_branch',
            'current_branch', 'current_warehouse', 'route',
            'assigned_trip', 'assigned_vehicle', 'assigned_driver', 'created_by',
        ),
        pk=pk, is_deleted=False,
    )
    status_history = shipment.status_history.all()[:20]
    events = shipment.events.all()[:20]
    notes = shipment.notes.all()[:20]
    packages = shipment.packages.all()

    allowed_transitions = VALID_TRANSITIONS.get(shipment.status, [])

    return render(request, 'cargo/shipment_detail.html', {
        'shipment': shipment,
        'status_history': status_history,
        'events': events,
        'notes': notes,
        'packages': packages,
        'allowed_transitions': allowed_transitions,
    })


@login_required
def shipment_edit(request, pk):
    from customers.models import Customer
    from branches.models import Branch
    from transportation.models import Route

    shipment = get_object_or_404(Shipment, pk=pk, is_deleted=False)

    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            if customer_id:
                shipment.customer = Customer.objects.get(pk=customer_id)

            shipment.sender_name = request.POST.get('sender_name', shipment.sender_name)
            shipment.sender_phone = request.POST.get('sender_phone', shipment.sender_phone)
            shipment.sender_address = request.POST.get('sender_address', shipment.sender_address)
            shipment.sender_city = request.POST.get('sender_city', shipment.sender_city)
            shipment.receiver_name = request.POST.get('receiver_name', shipment.receiver_name)
            shipment.receiver_phone = request.POST.get('receiver_phone', shipment.receiver_phone)
            shipment.receiver_address = request.POST.get('receiver_address', shipment.receiver_address)
            shipment.receiver_city = request.POST.get('receiver_city', shipment.receiver_city)
            shipment.origin = request.POST.get('origin', shipment.origin)
            shipment.destination = request.POST.get('destination', shipment.destination)
            shipment.cargo_type = request.POST.get('cargo_type', shipment.cargo_type)
            shipment.description = request.POST.get('description', shipment.description)
            shipment.num_packages = int(request.POST.get('num_packages', shipment.num_packages))
            shipment.actual_weight = float(request.POST.get('actual_weight', shipment.actual_weight))
            shipment.volumetric_weight = float(request.POST.get('volumetric_weight', shipment.volumetric_weight))
            shipment.charged_weight = float(request.POST.get('charged_weight', shipment.charged_weight))
            shipment.declared_value = float(request.POST.get('declared_value', shipment.declared_value))
            shipment.is_insured = request.POST.get('is_insured') == 'on'
            shipment.insurance_amount = float(request.POST.get('insurance_amount', shipment.insurance_amount))
            shipment.pickup_required = request.POST.get('pickup_required') == 'on'
            shipment.delivery_required = request.POST.get('delivery_required', 'on') == 'on'
            shipment.special_handling = request.POST.get('special_handling', shipment.special_handling)
            shipment.is_fragile = request.POST.get('is_fragile') == 'on'
            shipment.is_perishable = request.POST.get('is_perishable') == 'on'
            shipment.is_hazardous = request.POST.get('is_hazardous') == 'on'
            shipment.priority = request.POST.get('priority', shipment.priority)
            shipment.shipping_cost = float(request.POST.get('shipping_cost', shipment.shipping_cost))
            shipment.handling_fee = float(request.POST.get('handling_fee', shipment.handling_fee))
            shipment.insurance_fee = float(request.POST.get('insurance_fee', shipment.insurance_fee))
            shipment.total_cost = float(request.POST.get('total_cost', shipment.total_cost))

            origin_branch_id = request.POST.get('origin_branch')
            shipment.origin_branch = Branch.objects.get(pk=origin_branch_id) if origin_branch_id else shipment.origin_branch

            dest_branch_id = request.POST.get('destination_branch')
            shipment.destination_branch = Branch.objects.get(pk=dest_branch_id) if dest_branch_id else shipment.destination_branch

            route_id = request.POST.get('route')
            shipment.route = Route.objects.get(pk=route_id) if route_id else shipment.route

            shipment.save()

            CargoEvent.objects.create(
                shipment=shipment,
                event_type='note',
                description='Shipment details updated',
                created_by=request.user,
            )

            messages.success(request, f'Shipment {shipment.tracking_id} updated successfully.')
            return redirect('cargo:detail', pk=shipment.pk)

        except Exception as e:
            messages.error(request, f'Error updating shipment: {str(e)}')

    customers = Customer.objects.filter(status='active')
    branches = Branch.objects.filter(is_active=True)
    routes = Route.objects.filter(is_active=True)

    return render(request, 'cargo/shipment_form.html', {
        'shipment': shipment,
        'customers': customers,
        'branches': branches,
        'routes': routes,
        'cargo_type_choices': Shipment.CARGO_TYPE_CHOICES,
        'priority_choices': Shipment.PRIORITY_CHOICES,
        'editing': True,
    })


@login_required
def shipment_status_change(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk, is_deleted=False)

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('cargo:detail', pk=pk)

    new_status = request.POST.get('status', '')
    reason = request.POST.get('reason', '')

    allowed = VALID_TRANSITIONS.get(shipment.status, [])
    if new_status not in allowed:
        messages.error(
            request,
            f'Invalid status transition from "{shipment.get_status_display()}" to "{new_status}". '
            f'Allowed transitions: {", ".join(allowed) if allowed else "none (terminal state)"}'
        )
        return redirect('cargo:detail', pk=pk)

    old_status = shipment.status
    shipment.status = new_status

    if new_status == 'delivered':
        shipment.delivered_at = timezone.now()

    shipment.save()

    ShipmentStatusHistory.objects.create(
        shipment=shipment,
        previous_status=old_status,
        new_status=new_status,
        changed_by=request.user,
        reason=reason,
        source='manual',
    )

    CargoEvent.objects.create(
        shipment=shipment,
        event_type='status_change',
        description=f'Status changed from {old_status} to {new_status}' + (f': {reason}' if reason else ''),
        created_by=request.user,
    )

    messages.success(request, f'Shipment status updated to "{shipment.get_status_display()}" successfully.')
    return redirect('cargo:detail', pk=pk)


@login_required
def shipment_search(request):
    return render(request, 'cargo/shipment_search.html')


@login_required
def shipment_api_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    shipments = Shipment.objects.filter(
        Q(tracking_id__icontains=q) |
        Q(booking_number__icontains=q) |
        Q(waybill_number__icontains=q) |
        Q(sender_name__icontains=q) |
        Q(receiver_name__icontains=q),
        is_deleted=False,
    ).select_related('customer')[:20]

    results = []
    for s in shipments:
        results.append({
            'id': str(s.pk),
            'tracking_id': s.tracking_id,
            'booking_number': s.booking_number,
            'status': s.status,
            'status_display': s.get_status_display(),
            'sender_name': s.sender_name,
            'receiver_name': s.receiver_name,
            'origin': s.origin,
            'destination': s.destination,
            'customer': s.customer.full_name if s.customer else '',
            'created_at': s.created_at.strftime('%d %b %Y'),
        })

    return JsonResponse({'results': results})
