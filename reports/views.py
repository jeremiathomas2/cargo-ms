from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv
import json

from cargo.models import Shipment
from billing.models import Invoice
from payments.models import Payment
from customers.models import Customer
from saas_config.models import Organization
from .models import ReportTemplate, ReportExport


REPORT_TYPES = {
    'shipment_summary': {
        'name': 'Shipment Summary',
        'description': 'Overview of all shipments with status breakdown',
    },
    'revenue': {
        'name': 'Revenue Report',
        'description': 'Revenue breakdown by period',
    },
    'customer_shipments': {
        'name': 'Customer Shipments',
        'description': 'Shipments per customer',
    },
    'branch_performance': {
        'name': 'Branch Performance',
        'description': 'Performance metrics per branch',
    },
    'delivery_performance': {
        'name': 'Delivery Performance',
        'description': 'Delivery success rates and timing',
    },
}


@login_required
def reports_dashboard(request):
    return render(request, 'reports/dashboard.html', {
        'report_types': REPORT_TYPES,
    })


@login_required
def report_view(request, report_type):
    if report_type not in REPORT_TYPES:
        return HttpResponse('Report type not found', status=404)

    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)
    report_info = REPORT_TYPES[report_type]

    data = {}
    title = report_info['name']

    if report_type == 'shipment_summary':
        total = Shipment.objects.filter(is_deleted=False, created_at__gte=since).count()
        by_status = list(
            Shipment.objects.filter(is_deleted=False, created_at__gte=since)
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        by_cargo_type = list(
            Shipment.objects.filter(is_deleted=False, created_at__gte=since)
            .values('cargo_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        data = {
            'total': total,
            'by_status': by_status,
            'by_cargo_type': by_cargo_type,
        }

    elif report_type == 'revenue':
        total_revenue = Invoice.objects.filter(status='paid', created_at__gte=since).aggregate(
            total=Sum('total')
        )['total'] or 0
        total_payments = Payment.objects.filter(status='verified', created_at__gte=since).aggregate(
            total=Sum('amount')
        )['total'] or 0
        pending = Invoice.objects.filter(status__in=['unpaid', 'partially_paid']).aggregate(
            total=Sum('balance')
        )['total'] or 0
        by_month_qs = (
            Payment.objects.filter(status='verified', created_at__gte=since)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        by_month = [
            {
                'month': row['month'].strftime('%Y-%m') if row['month'] else '',
                'total': float(row['total'] or 0),
            }
            for row in by_month_qs
        ]
        data = {
            'total_revenue': total_revenue,
            'total_payments': total_payments,
            'pending_amount': pending,
            'by_month': by_month,
        }

    elif report_type == 'customer_shipments':
        customer_data = list(
            Shipment.objects.filter(is_deleted=False, created_at__gte=since)
            .values('customer__first_name', 'customer__last_name', 'customer__company_name')
            .annotate(count=Count('id'), total_cost=Sum('total_cost'))
            .order_by('-count')[:50]
        )
        data = {'customers': customer_data}

    elif report_type == 'branch_performance':
        branch_data = list(
            Shipment.objects.filter(is_deleted=False, created_at__gte=since)
            .values('origin_branch__name')
            .annotate(count=Count('id'), total_cost=Sum('total_cost'))
            .order_by('-count')
        )
        data = {'branches': branch_data}

    elif report_type == 'delivery_performance':
        from delivery.models import Delivery
        total_deliveries = Delivery.objects.filter(created_at__gte=since).count()
        successful = Delivery.objects.filter(status='delivered', created_at__gte=since).count()
        failed = Delivery.objects.filter(status='failed', created_at__gte=since).count()
        returned = Delivery.objects.filter(status='returned', created_at__gte=since).count()
        data = {
            'total_deliveries': total_deliveries,
            'successful': successful,
            'failed': failed,
            'returned': returned,
            'success_rate': round(successful / total_deliveries * 100, 1) if total_deliveries else 0,
        }

    return render(request, 'reports/report_view.html', {
        'report_type': report_type,
        'title': title,
        'description': report_info['description'],
        'data': data,
        'days': days,
        'since': since,
    })


@login_required
def report_templates(request):
    queryset = ReportTemplate.objects.select_related("organization").order_by("name")
    search = request.GET.get("q", "")
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(report_type__icontains=search) |
            Q(organization__name__icontains=search)
        )
    paginator = Paginator(queryset, 20)
    templates = paginator.get_page(request.GET.get("page", 1))

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "create_template":
            name = request.POST.get("name", "").strip()
            report_type = request.POST.get("report_type", "").strip()
            org_id = request.POST.get("organization", "")
            if name and report_type in ReportTemplate.ReportType.values and org_id:
                organization = Organization.objects.filter(pk=org_id).first()
                if organization:
                    ReportTemplate.objects.create(
                        name=name,
                        report_type=report_type,
                        organization=organization,
                        is_active=request.POST.get("is_active") == "on",
                    )
                    messages.success(request, f'Report template "{name}" created.')
                else:
                    messages.error(request, "Please choose a valid organization.")
            else:
                messages.error(request, "Name, report type and organization are required.")
        elif action == "toggle_template":
            template = ReportTemplate.objects.filter(pk=request.POST.get("template_id")).first()
            if template:
                template.is_active = not template.is_active
                template.save(update_fields=["is_active"])
                messages.success(request, f'Template "{template.name}" {"activated" if template.is_active else "deactivated"}.')
            else:
                messages.error(request, "Report template not found.")
        elif action == "delete_template":
            template = ReportTemplate.objects.filter(pk=request.POST.get("template_id")).first()
            if template:
                template.delete()
                messages.success(request, "Report template deleted.")
            else:
                messages.error(request, "Report template not found.")
        return redirect("reports:templates")

    return render(request, "reports/templates.html", {
        "templates": templates,
        "organizations": Organization.objects.order_by("name"),
        "report_type_choices": ReportTemplate.ReportType.choices,
        "search": search,
    })


@login_required
def report_exports(request):
    queryset = ReportExport.objects.select_related("template", "requested_by").order_by("-created_at")
    status_filter = request.GET.get("status", "")
    if status_filter in ReportExport.Status.values:
        queryset = queryset.filter(status=status_filter)
    paginator = Paginator(queryset, 20)
    exports = paginator.get_page(request.GET.get("page", 1))

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "create_export":
            report_type = request.POST.get("report_type", "").strip()
            export_format = request.POST.get("export_format", "pdf")
            if report_type in ReportTemplate.ReportType.values and export_format in ReportExport.ExportFormat.values:
                template = ReportTemplate.objects.filter(
                    report_type=report_type, is_active=True, organization_id=request.POST.get("organization")
                ).first()
                ReportExport.objects.create(
                    template=template,
                    report_type=report_type,
                    export_format=export_format,
                    requested_by=request.user,
                    parameters={"days": 30},
                    status=ReportExport.Status.PENDING,
                )
                messages.success(request, "Export queued. Check back here for download.")
            else:
                messages.error(request, "Please choose a valid report type and format.")
        elif action == "delete_export":
            export = ReportExport.objects.filter(pk=request.POST.get("export_id")).first()
            if export:
                export.delete()
                messages.success(request, "Export removed.")
            else:
                messages.error(request, "Export not found.")
        return redirect("reports:exports")

    return render(request, "reports/exports.html", {
        "exports": exports,
        "status_filter": status_filter,
        "report_type_choices": ReportTemplate.ReportType.choices,
        "format_choices": ReportExport.ExportFormat.choices,
        "organizations": Organization.objects.order_by("name"),
        "completed_count": ReportExport.objects.filter(status=ReportExport.Status.COMPLETED).count(),
        "pending_count": ReportExport.objects.filter(status=ReportExport.Status.PENDING).count(),
    })


@login_required
def report_export(request, report_type):
    if report_type not in REPORT_TYPES:
        return HttpResponse('Report type not found', status=404)

    export_format = request.GET.get('format', 'csv')
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    if report_type == 'shipment_summary':
        shipments = Shipment.objects.filter(is_deleted=False, created_at__gte=since).select_related('customer')

        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="shipment_summary_{timezone.now().strftime("%Y%m%d")}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Tracking ID', 'Customer', 'Origin', 'Destination', 'Status', 'Cargo Type', 'Created'])
            for s in shipments:
                writer.writerow([
                    s.tracking_id,
                    s.customer.full_name if s.customer else '',
                    s.origin,
                    s.destination,
                    s.get_status_display(),
                    s.get_cargo_type_display(),
                    s.created_at.strftime('%Y-%m-%d %H:%M'),
                ])
            return response

        elif export_format == 'json':
            data = list(shipments.values(
                'tracking_id', 'origin', 'destination', 'status', 'cargo_type', 'created_at'
            )[:1000])
            response = HttpResponse(json.dumps(data, default=str), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="shipment_summary_{timezone.now().strftime("%Y%m%d")}.json"'
            return response

    elif report_type == 'revenue':
        invoices = Invoice.objects.filter(created_at__gte=since).select_related('customer')

        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="revenue_report_{timezone.now().strftime("%Y%m%d")}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Invoice Number', 'Customer', 'Total', 'Amount Paid', 'Balance', 'Status', 'Date'])
            for inv in invoices:
                writer.writerow([
                    inv.invoice_number,
                    inv.customer.full_name if inv.customer else '',
                    str(inv.total),
                    str(inv.amount_paid),
                    str(inv.balance),
                    inv.get_status_display(),
                    inv.created_at.strftime('%Y-%m-%d'),
                ])
            return response

    return HttpResponse('Export format not supported', status=400)
