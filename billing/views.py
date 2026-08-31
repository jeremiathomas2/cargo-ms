from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

from .models import (
    Quotation, QuotationItem, Invoice, InvoiceItem,
    PricingRule, Tax, Discount,
)

ITEMS_PER_PAGE = 25


@login_required
def quotation_list(request):
    queryset = Quotation.objects.select_related('customer', 'created_by')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if search:
        queryset = queryset.filter(
            Q(quotation_number__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer__company_name__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    quotations = paginator.get_page(page)

    return render(request, 'billing/quotation_list.html', {
        'quotations': quotations,
        'search': search,
        'status_filter': status,
        'status_choices': Quotation.STATUS_CHOICES,
    })


@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(
        Quotation.objects.select_related('customer', 'created_by'),
        pk=pk,
    )
    items = quotation.items.all()

    return render(request, 'billing/quotation_detail.html', {
        'quotation': quotation,
        'items': items,
    })


@login_required
def invoice_list(request):
    queryset = Invoice.objects.select_related('customer', 'shipment', 'created_by')

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if search:
        queryset = queryset.filter(
            Q(invoice_number__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(customer__company_name__icontains=search) |
            Q(shipment__tracking_id__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    invoices = paginator.get_page(page)

    return render(request, 'billing/invoice_list.html', {
        'invoices': invoices,
        'search': search,
        'status_filter': status,
        'status_choices': Invoice.STATUS_CHOICES,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer', 'shipment', 'quotation', 'created_by'),
        pk=pk,
    )
    items = invoice.items.all()
    payments = invoice.payments.all().select_related('payment_method', 'recorded_by')

    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'items': items,
        'payments': payments,
    })


@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as pdf_canvas
        from io import BytesIO
    except ImportError:
        messages.error(request, 'ReportLab is not installed. Cannot generate PDF.')
        return redirect('billing:invoice_detail', pk=pk)

    buffer = BytesIO()
    p = pdf_canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica", 18)
    p.drawString(72, 750, "INVOICE")

    p.setFont("Helvetica", 11)
    p.drawString(72, 720, f"Invoice Number: {invoice.invoice_number}")
    p.drawString(72, 705, f"Customer: {invoice.customer}")
    p.drawString(72, 690, f"Date: {invoice.created_at.strftime('%d %B %Y')}")

    if invoice.due_date:
        p.drawString(72, 675, f"Due Date: {invoice.due_date.strftime('%d %B %Y')}")

    if invoice.shipment:
        p.drawString(72, 660, f"Shipment: {invoice.shipment.tracking_id}")
        y_offset = 645
    else:
        y_offset = 660

    p.setFont("Helvetica", 10)
    p.drawString(72, y_offset, f"Status: {invoice.get_status_display()}")
    y_offset -= 30

    p.setFont("Helvetica", 10)
    p.drawString(72, y_offset, "Description")
    p.drawString(350, y_offset, "Qty")
    p.drawString(400, y_offset, "Unit Price")
    p.drawString(480, y_offset, "Total")
    y_offset -= 5

    p.line(72, y_offset, 550, y_offset)
    y_offset -= 15

    for item in items:
        p.drawString(72, y_offset, str(item.description)[:50])
        p.drawString(350, y_offset, str(item.quantity))
        p.drawString(400, y_offset, f"{item.unit_price:,.2f}")
        p.drawString(480, y_offset, f"{item.total:,.2f}")
        y_offset -= 18

    y_offset -= 10
    p.line(72, y_offset, 550, y_offset)
    y_offset -= 20

    p.drawString(72, y_offset, f"Subtotal:")
    p.drawString(480, y_offset, f"{invoice.currency} {invoice.subtotal:,.2f}")
    y_offset -= 18

    p.drawString(72, y_offset, f"Tax:")
    p.drawString(480, y_offset, f"{invoice.currency} {invoice.tax_amount:,.2f}")
    y_offset -= 18

    if invoice.discount_amount > 0:
        p.drawString(72, y_offset, f"Discount:")
        p.drawString(480, y_offset, f"-{invoice.currency} {invoice.discount_amount:,.2f}")
        y_offset -= 18

    p.setFont("Helvetica", 12)
    p.drawString(72, y_offset, f"Total:")
    p.drawString(480, y_offset, f"{invoice.currency} {invoice.total:,.2f}")
    y_offset -= 20

    p.setFont("Helvetica", 11)
    p.drawString(72, y_offset, f"Amount Paid: {invoice.currency} {invoice.amount_paid:,.2f}")
    y_offset -= 18
    p.drawString(72, y_offset, f"Balance Due: {invoice.currency} {invoice.balance:,.2f}")

    if invoice.notes:
        y_offset -= 40
        p.setFont("Helvetica", 9)
        p.drawString(72, y_offset, "Notes:")
        y_offset -= 14
        p.drawString(72, y_offset, invoice.notes[:100])

    p.setFont("Helvetica", 8)
    p.drawString(72, 100, "Shehena Cargo Management System - Generated Document")
    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
    return response


@login_required
def pricing_list(request):
    pricing_rules = PricingRule.objects.all()
    taxes = Tax.objects.filter(is_active=True)
    discounts = Discount.objects.filter(is_active=True)

    search = request.GET.get('q', '')
    if search:
        pricing_rules = pricing_rules.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    paginator = Paginator(pricing_rules, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    rules = paginator.get_page(page)

    return render(request, 'billing/pricing_list.html', {
        'pricing_rules': rules,
        'taxes': taxes,
        'discounts': discounts,
        'search': search,
    })
