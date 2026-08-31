from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta


@login_required
def index(request):
    from cargo.models import Shipment
    from payments.models import Payment
    from customers.models import Customer
    from gps_tracking.models import GPSDevice
    from transportation.models import Vehicle, Trip

    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    total_shipments = Shipment.objects.filter(is_deleted=False).count()
    in_transit = Shipment.objects.filter(status='in_transit', is_deleted=False).count()
    at_warehouse = Shipment.objects.filter(status='in_warehouse', is_deleted=False).count()
    delivered_today = Shipment.objects.filter(status='delivered', delivered_at__date=today).count()
    pending_payments = Payment.objects.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    active_alerts = GPSDevice.objects.filter(status='offline').count()

    recent_shipments = Shipment.objects.filter(is_deleted=False).select_related('customer').order_by('-created_at')[:20]

    monthly_data = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=30 * i)
        count = Shipment.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month,
            is_deleted=False
        ).count()
        monthly_data.append({'month': month_date.strftime('%b'), 'count': count})

    status_data = list(
        Shipment.objects.filter(is_deleted=False)
        .values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Fleet data
    vehicles = Vehicle.objects.filter(is_active=True)
    on_route_vehicles = vehicles.filter(status='on_route')
    
    # Cross-border shipments
    cross_border_shipments = Shipment.objects.filter(
        is_deleted=False,
        status='in_transit'
    ).select_related('customer').order_by('-created_at')[:5]

    # Delivery schedule
    upcoming_deliveries = Shipment.objects.filter(
        is_deleted=False,
        status__in=['ready_for_delivery', 'out_for_delivery']
    ).select_related('customer').order_by('estimated_arrival')[:10]

    context = {
        'total_shipments': total_shipments,
        'in_transit': in_transit,
        'at_warehouse': at_warehouse,
        'delivered_today': delivered_today,
        'pending_payments': pending_payments,
        'active_alerts': active_alerts,
        'recent_shipments': recent_shipments,
        'monthly_data': monthly_data,
        'status_data': status_data,
        'today': today,
        'vehicles': vehicles,
        'on_route_vehicles': on_route_vehicles,
        'cross_border_shipments': cross_border_shipments,
        'upcoming_deliveries': upcoming_deliveries,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def operations(request):
    from cargo.models import Shipment
    from transportation.models import Trip

    active_trips = Trip.objects.filter(status__in=['active', 'in_transit']).select_related('vehicle', 'driver', 'route')
    recent_shipments = Shipment.objects.filter(is_deleted=False).select_related('customer').order_by('-created_at')[:10]

    return render(request, 'dashboard/operations.html', {
        'active_trips': active_trips,
        'recent_shipments': recent_shipments,
    })


@login_required
def transportation_dashboard(request):
    from transportation.models import Vehicle, Driver, Trip

    vehicles = Vehicle.objects.filter(is_active=True)
    drivers = Driver.objects.filter(is_active=True)
    active_trips = Trip.objects.filter(status__in=['active', 'in_transit']).select_related('vehicle', 'driver')

    return render(request, 'dashboard/transportation.html', {
        'total_vehicles': vehicles.count(),
        'available_vehicles': vehicles.filter(status='available').count(),
        'on_route_vehicles': vehicles.filter(status='on_route').count(),
        'total_drivers': drivers.count(),
        'active_trips': active_trips,
    })


@login_required
def finance_dashboard(request):
    from billing.models import Invoice
    from payments.models import Payment

    total_invoices = Invoice.objects.count()
    unpaid_invoices = Invoice.objects.filter(status__in=['unpaid', 'partially_paid']).count()
    total_revenue = Invoice.objects.filter(status='paid').aggregate(total=Sum('total'))['total'] or 0
    pending_amount = Invoice.objects.filter(status__in=['unpaid', 'partially_paid']).aggregate(
        total=Sum('balance')
    )['total'] or 0
    recent_payments = Payment.objects.select_related('customer').order_by('-created_at')[:10]

    return render(request, 'dashboard/finance.html', {
        'total_invoices': total_invoices,
        'unpaid_invoices': unpaid_invoices,
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'recent_payments': recent_payments,
    })
