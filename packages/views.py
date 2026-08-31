from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import Package

ITEMS_PER_PAGE = 25


@login_required
def package_list(request):
    queryset = Package.objects.select_related('shipment', 'current_warehouse', 'current_zone', 'current_bin')

    search = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    if search:
        from django.db.models import Q
        queryset = queryset.filter(
            Q(package_number__icontains=search) |
            Q(barcode__icontains=search) |
            Q(description__icontains=search) |
            Q(shipment__tracking_id__icontains=search)
        )
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    packages = paginator.get_page(page)

    return render(request, 'packages/package_list.html', {
        'packages': packages,
        'search': search,
        'status_filter': status_filter,
        'status_choices': Package.STATUS_CHOICES,
    })


@login_required
def package_detail(request, pk):
    package = get_object_or_404(
        Package.objects.select_related('shipment', 'current_warehouse', 'current_zone', 'current_bin', 'assigned_gps'),
        pk=pk,
    )
    items = package.items.all()
    movements = package.warehouse_movements.all()[:20]

    return render(request, 'packages/package_detail.html', {
        'package': package,
        'items': items,
        'movements': movements,
    })


@login_required
def package_scan(request, pk):
    package = get_object_or_404(Package, pk=pk)

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('packages:detail', pk=pk)

    scanned_barcode = request.POST.get('barcode', '').strip()
    action = request.POST.get('action', 'verify')

    if scanned_barcode and scanned_barcode != package.barcode:
        messages.error(request, f'Barcode mismatch. Expected {package.barcode}, got {scanned_barcode}.')
        return redirect('packages:detail', pk=pk)

    status_map = {
        'receive': 'received',
        'warehouse': 'in_warehouse',
        'sort': 'sorted',
        'load': 'loaded',
        'transit': 'in_transit',
        'deliver': 'delivered',
        'damage': 'damaged',
        'lost': 'lost',
    }

    new_status = status_map.get(action)
    if new_status:
        old_status = package.status
        package.status = new_status
        package.save()

        from cargo.models import CargoEvent
        CargoEvent.objects.create(
            shipment=package.shipment,
            event_type='scan',
            description=f'Package {package.package_number} scanned: {old_status} → {new_status}',
            created_by=request.user,
            metadata={'package_id': str(package.pk), 'barcode': scanned_barcode},
        )

        messages.success(request, f'Package {package.package_number} status updated to {new_status}.')
    else:
        messages.info(request, f'Package {package.package_number} verified via scan.')

    return redirect('packages:detail', pk=pk)


@login_required
def package_move(request, pk):
    from warehouse.models import Warehouse, WarehouseZone, WarehouseShelf, WarehouseBin, WarehouseMovement

    package = get_object_or_404(Package, pk=pk)

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('packages:detail', pk=pk)

    to_warehouse_id = request.POST.get('to_warehouse')
    to_zone_id = request.POST.get('to_zone')
    to_shelf_id = request.POST.get('to_shelf')
    to_bin_id = request.POST.get('to_bin')
    notes = request.POST.get('notes', '')

    to_warehouse = Warehouse.objects.get(pk=to_warehouse_id) if to_warehouse_id else None
    to_zone = WarehouseZone.objects.get(pk=to_zone_id) if to_zone_id else None
    to_shelf = WarehouseShelf.objects.get(pk=to_shelf_id) if to_shelf_id else None
    to_bin = WarehouseBin.objects.get(pk=to_bin_id) if to_bin_id else None

    from_warehouse = package.current_warehouse
    from_zone = package.current_zone
    from_shelf = package.current_bin

    WarehouseMovement.objects.create(
        shipment=package.shipment,
        package=package,
        warehouse=to_warehouse or from_warehouse,
        movement_type='internal',
        from_zone=from_zone,
        from_bin=from_shelf,
        to_zone=to_zone,
        to_bin=to_bin,
        scanned_by=request.user,
        notes=notes,
        barcode_scan=package.barcode,
    )

    if to_warehouse:
        if from_warehouse and from_warehouse != to_warehouse:
            if from_warehouse.current_occupancy > 0:
                from_warehouse.current_occupancy -= 1
                from_warehouse.save(update_fields=['current_occupancy'])
            to_warehouse.current_occupancy += 1
            to_warehouse.save(update_fields=['current_occupancy'])

        package.current_warehouse = to_warehouse
    if to_zone:
        package.current_zone = to_zone
    if to_bin:
        package.current_bin = to_bin

    package.save()

    from cargo.models import CargoEvent
    CargoEvent.objects.create(
        shipment=package.shipment,
        event_type='location_update',
        description=f'Package {package.package_number} moved to {to_warehouse or "same warehouse"}',
        created_by=request.user,
        metadata={'package_id': str(package.pk)},
    )

    messages.success(request, f'Package {package.package_number} moved successfully.')
    return redirect('packages:detail', pk=pk)
