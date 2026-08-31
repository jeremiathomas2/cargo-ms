from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.conf import settings
import os

from .models import Document, DocumentTemplate

ITEMS_PER_PAGE = 25


@login_required
def document_list(request):
    queryset = Document.objects.select_related('template', 'shipment', 'customer', 'invoice', 'created_by')

    search = request.GET.get('q', '')
    doc_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    if search:
        queryset = queryset.filter(
            Q(document_number__icontains=search) |
            Q(title__icontains=search) |
            Q(shipment__tracking_id__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )
    if doc_type:
        queryset = queryset.filter(document_type=doc_type)
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    documents = paginator.get_page(page)

    doc_types = DocumentTemplate.objects.values_list('document_type', flat=True).distinct()

    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'search': search,
        'type_filter': doc_type,
        'status_filter': status,
        'doc_types': doc_types,
        'status_choices': Document.STATUS_CHOICES,
    })


@login_required
def document_detail(request, pk):
    document = get_object_or_404(
        Document.objects.select_related('template', 'shipment', 'customer', 'invoice', 'delivery', 'claim', 'created_by'),
        pk=pk,
    )
    versions = document.versions.all()

    return render(request, 'documents/document_detail.html', {
        'document': document,
        'versions': versions,
    })


@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not document.file:
        raise Http404('No file attached to this document.')

    file_path = document.file.path
    if not os.path.exists(file_path):
        raise Http404('File not found on disk.')

    with open(file_path, 'rb') as f:
        file_data = f.read()

    content_type = 'application/octet-stream'
    file_name = os.path.basename(file_path)
    ext = os.path.splitext(file_name)[1].lower()
    content_type_map = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
    }
    content_type = content_type_map.get(ext, 'application/octet-stream')

    response = HttpResponse(file_data, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@login_required
def document_generate(request, type, entity_id):
    if request.method != 'POST':
        messages.error(request, 'POST method required to generate documents.')
        return redirect('documents:list')

    template = DocumentTemplate.objects.filter(
        document_type=type,
        is_active=True,
    ).first()

    if not template:
        messages.error(request, f'No active template found for document type: {type}')
        return redirect('documents:list')

    shipment = None
    customer = None
    invoice = None
    delivery = None
    claim = None

    if type in ('booking_confirmation', 'cargo_receipt', 'waybill', 'shipping_label', 'manifest', 'loading_sheet', 'dispatch_note'):
        from cargo.models import Shipment
        shipment = Shipment.objects.filter(pk=entity_id).first()
    elif type in ('quotation', 'invoice', 'receipt'):
        from billing.models import Invoice
        invoice = Invoice.objects.filter(pk=entity_id).first()
        if invoice:
            customer = invoice.customer
            shipment = invoice.shipment
    elif type in ('delivery_note', 'proof_of_delivery', 'trip_sheet'):
        from delivery.models import Delivery
        delivery = Delivery.objects.filter(pk=entity_id).first()
        if delivery:
            shipment = delivery.shipment
    elif type in ('claim_form', 'damage_report'):
        from claims.models import Claim
        claim = Claim.objects.filter(pk=entity_id).first()
        if claim:
            shipment = claim.shipment
            customer = claim.customer

    doc_number = Document.generate_document_number(type) if hasattr(Document, 'generate_document_number') else None
    from core.utils import generate_document_number
    prefix_map = {
        'booking_confirmation': 'BKCF',
        'cargo_receipt': 'CR',
        'waybill': 'WB',
        'shipping_label': 'SL',
        'manifest': 'MAN',
        'loading_sheet': 'LS',
        'dispatch_note': 'DN',
        'quotation': 'QT',
        'invoice': 'INV',
        'receipt': 'RCP',
        'delivery_note': 'DLN',
        'proof_of_delivery': 'POD',
        'trip_sheet': 'TS',
        'claim_form': 'CLM',
        'damage_report': 'DMG',
    }
    prefix = prefix_map.get(type, 'DOC')
    doc_number = generate_document_number(prefix)

    document = Document(
        document_number=doc_number,
        template=template,
        document_type=type,
        title=f'{template.name} - {entity_id}',
        shipment=shipment,
        customer=customer,
        invoice=invoice,
        delivery=delivery,
        claim=claim,
        status='generated',
        created_by=request.user,
    )

    if hasattr(request, 'user') and hasattr(request.user, 'organization'):
        document.organization = request.user.organization

    document.save()

    messages.success(request, f'Document {doc_number} generated successfully.')
    return redirect('documents:detail', pk=document.pk)
