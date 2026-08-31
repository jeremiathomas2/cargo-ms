from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from .models import Claim, ClaimDocument

ITEMS_PER_PAGE = 25


@login_required
def claim_list(request):
    queryset = Claim.objects.select_related('shipment', 'customer', 'assigned_to', 'created_by')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    claim_type = request.GET.get('type', '')

    if search:
        queryset = queryset.filter(
            Q(claim_number__icontains=search) |
            Q(shipment__tracking_id__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer__company_name__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)
    if claim_type:
        queryset = queryset.filter(claim_type=claim_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    claims = paginator.get_page(page)

    return render(request, 'claims/claim_list.html', {
        'claims': claims,
        'search': search,
        'status_filter': status,
        'type_filter': claim_type,
        'status_choices': Claim.STATUS_CHOICES,
        'type_choices': Claim.CLAIM_TYPES,
    })


@login_required
def claim_create(request, shipment_pk):
    from cargo.models import Shipment, CargoEvent

    shipment = get_object_or_404(Shipment, pk=shipment_pk, is_deleted=False)

    if request.method == 'POST':
        try:
            claim_type = request.POST.get('claim_type', '')
            severity = request.POST.get('severity', 'medium')
            description = request.POST.get('description', '').strip()
            claimed_value = float(request.POST.get('claimed_value', 0))

            if not claim_type or not description:
                messages.error(request, 'Claim type and description are required.')
                return redirect('claims:create', shipment_pk=shipment_pk)

            claim = Claim.objects.create(
                shipment=shipment,
                customer=shipment.customer,
                claim_type=claim_type,
                severity=severity,
                description=description,
                claimed_value=claimed_value,
                created_by=request.user,
                status='submitted',
            )

            uploaded_files = request.FILES.getlist('documents')
            doc_type = request.POST.get('doc_type', 'other')
            for f in uploaded_files:
                ClaimDocument.objects.create(
                    claim=claim,
                    title=f.name,
                    file=f,
                    document_type=doc_type,
                    uploaded_by=request.user,
                )

            CargoEvent.objects.create(
                shipment=shipment,
                event_type='exception',
                description=f'Claim {claim.claim_number} created: {claim.get_claim_type_display()}',
                created_by=request.user,
            )

            messages.success(request, f'Claim {claim.claim_number} created successfully.')
            return redirect('claims:detail', pk=claim.pk)

        except Exception as e:
            messages.error(request, f'Error creating claim: {str(e)}')

    return render(request, 'claims/claim_form.html', {
        'shipment': shipment,
        'type_choices': Claim.CLAIM_TYPES,
        'severity_choices': Claim.SEVERITY_CHOICES,
    })


@login_required
def claim_detail(request, pk):
    claim = get_object_or_404(
        Claim.objects.select_related('shipment', 'customer', 'assigned_to', 'created_by'),
        pk=pk,
    )
    documents = claim.documents.all()

    valid_status_transitions = {
        'submitted': ['under_investigation', 'rejected'],
        'under_investigation': ['approved', 'rejected'],
        'approved': ['compensated', 'closed'],
        'rejected': ['closed'],
        'compensated': ['closed'],
        'closed': [],
    }
    allowed_transitions = valid_status_transitions.get(claim.status, [])

    return render(request, 'claims/claim_detail.html', {
        'claim': claim,
        'documents': documents,
        'allowed_transitions': allowed_transitions,
    })


@login_required
def claim_update_status(request, pk):
    claim = get_object_or_404(Claim, pk=pk)

    if request.method != 'POST':
        messages.error(request, 'POST method required.')
        return redirect('claims:detail', pk=pk)

    new_status = request.POST.get('status', '')
    resolution = request.POST.get('resolution', '').strip()
    approved_value = request.POST.get('approved_value')
    compensation_amount = request.POST.get('compensation_amount')

    valid_status_transitions = {
        'submitted': ['under_investigation', 'rejected'],
        'under_investigation': ['approved', 'rejected'],
        'approved': ['compensated', 'closed'],
        'rejected': ['closed'],
        'compensated': ['closed'],
        'closed': [],
    }

    allowed = valid_status_transitions.get(claim.status, [])
    if new_status not in allowed:
        messages.error(
            request,
            f'Invalid transition from "{claim.get_status_display()}" to "{new_status}". '
            f'Allowed: {", ".join(allowed) if allowed else "none (terminal)"}'
        )
        return redirect('claims:detail', pk=pk)

    claim.status = new_status
    if resolution:
        claim.resolution = resolution
    if approved_value:
        claim.approved_value = float(approved_value)
    if compensation_amount:
        claim.compensation_amount = float(compensation_amount)
    if new_status in ('closed', 'compensated', 'rejected'):
        from django.utils import timezone
        claim.resolved_at = timezone.now()
    claim.save()

    from cargo.models import CargoEvent
    CargoEvent.objects.create(
        shipment=claim.shipment,
        event_type='note',
        description=f'Claim {claim.claim_number} status updated to {claim.get_status_display()}' +
                    (f': {resolution}' if resolution else ''),
        created_by=request.user,
    )

    messages.success(request, f'Claim status updated to "{claim.get_status_display()}".')
    return redirect('claims:detail', pk=pk)
