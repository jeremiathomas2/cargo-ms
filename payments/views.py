from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
import json

from .models import Payment, PaymentMethod, PaymentTransaction, Refund

ITEMS_PER_PAGE = 25


@login_required
def payment_list(request):
    queryset = Payment.objects.select_related('customer', 'invoice', 'payment_method', 'recorded_by')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    method = request.GET.get('method', '')

    if search:
        queryset = queryset.filter(
            Q(payment_number__icontains=search) |
            Q(reference_number__icontains=search) |
            Q(transaction_id__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer__company_name__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)
    if method:
        queryset = queryset.filter(payment_method__code=method)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    payments = paginator.get_page(page)

    payment_methods = PaymentMethod.objects.filter(is_active=True)

    return render(request, 'payments/payment_list.html', {
        'payments': payments,
        'search': search,
        'status_filter': status,
        'method_filter': method,
        'status_choices': Payment.STATUS_CHOICES,
        'payment_methods': payment_methods,
    })


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related('customer', 'invoice', 'payment_method', 'recorded_by', 'verified_by'),
        pk=pk,
    )
    transactions = payment.transactions.all()
    refunds = payment.refunds.all()

    return render(request, 'payments/payment_detail.html', {
        'payment': payment,
        'transactions': transactions,
        'refunds': refunds,
    })


@login_required
def payment_create(request, invoice_pk):
    from billing.models import Invoice

    invoice = get_object_or_404(Invoice, pk=invoice_pk)

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            payment_method_id = request.POST.get('payment_method')
            reference_number = request.POST.get('reference_number', '').strip()
            notes = request.POST.get('notes', '')

            if amount <= 0:
                messages.error(request, 'Payment amount must be greater than zero.')
                return redirect('payments:create', invoice_pk=invoice_pk)

            if invoice.balance <= 0:
                messages.error(request, 'This invoice is already fully paid.')
                return redirect('payments:create', invoice_pk=invoice_pk)

            payment_method = PaymentMethod.objects.get(pk=payment_method_id)

            payment = Payment.objects.create(
                customer=invoice.customer,
                invoice=invoice,
                amount=amount,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes,
                currency=invoice.currency,
                recorded_by=request.user,
                status='verified',
            )

            invoice.amount_paid += amount
            invoice.recalculate_status()

            from cargo.models import CargoEvent
            if invoice.shipment:
                CargoEvent.objects.create(
                    shipment=invoice.shipment,
                    event_type='note',
                    description=f'Payment {payment.payment_number} of {invoice.currency} {amount:,.2f} recorded',
                    created_by=request.user,
                )

            messages.success(request, f'Payment {payment.payment_number} recorded successfully.')
            return redirect('payments:detail', pk=payment.pk)

        except PaymentMethod.DoesNotExist:
            messages.error(request, 'Invalid payment method selected.')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')

    payment_methods = PaymentMethod.objects.filter(is_active=True)

    return render(request, 'payments/payment_form.html', {
        'invoice': invoice,
        'payment_methods': payment_methods,
    })


@login_required
def payment_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    provider = data.get('provider', 'unknown')
    provider_ref = data.get('reference', '')
    provider_status = data.get('status', '')
    amount = data.get('amount', 0)
    idempotency_key = data.get('idempotency_key', '')

    if not provider_ref:
        return JsonResponse({'error': 'Reference is required'}, status=400)

    existing = PaymentTransaction.objects.filter(
        provider=provider,
        provider_ref=provider_ref,
    ).first()
    if existing:
        return JsonResponse({'status': 'already_processed', 'transaction_id': str(existing.pk)})

    if idempotency_key:
        existing_by_key = PaymentTransaction.objects.filter(
            idempotency_key=idempotency_key,
        ).first()
        if existing_by_key:
            return JsonResponse({'status': 'already_processed', 'transaction_id': str(existing_by_key.pk)})

    transaction = PaymentTransaction(
        provider=provider,
        provider_ref=provider_ref,
        provider_status=provider_status,
        amount=float(amount),
        idempotency_key=idempotency_key,
        raw_request=data,
    )

    transaction_status_map = {
        'completed': 'success',
        'successful': 'success',
        'failed': 'failed',
        'pending': 'pending',
        'timeout': 'timeout',
    }
    transaction.status = transaction_status_map.get(provider_status.lower(), 'pending')
    transaction.save()

    payment_number = data.get('payment_number', '')
    if payment_number:
        try:
            payment = Payment.objects.get(payment_number=payment_number)
            if provider_status.lower() in ('completed', 'successful'):
                payment.status = 'verified'
                payment.verified_at = timezone.now()
                payment.save(update_fields=['status', 'verified_at'])
            elif provider_status.lower() == 'failed':
                payment.status = 'failed'
                payment.save(update_fields=['status'])
        except Payment.DoesNotExist:
            pass

    return JsonResponse({
        'status': 'ok',
        'transaction_id': str(transaction.pk),
    })
