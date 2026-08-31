from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count

from .models import Warehouse, WarehouseZone, WarehouseShelf, WarehouseBin, WarehouseMovement

ITEMS_PER_PAGE = 25


@login_required
def warehouse_list(request):
    queryset = Warehouse.objects.select_related('branch', 'manager')

    search = request.GET.get('q', '')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(branch__name__icontains=search)
        )

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    warehouses = paginator.get_page(page)

    total_capacity = sum(w.capacity for w in queryset)
    total_occupancy = sum(w.current_occupancy for w in queryset)

    return render(request, 'warehouse/warehouse_list.html', {
        'warehouses': warehouses,
        'search': search,
        'total_capacity': total_capacity,
        'total_occupancy': total_occupancy,
    })


@login_required
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(
        Warehouse.objects.select_related('branch', 'manager'),
        pk=pk,
    )
    zones = warehouse.zones.filter(is_active=True).prefetch_related('shelves', 'shelves__bins')
    recent_movements = warehouse.movements.select_related(
        'shipment', 'package', 'scanned_by', 'from_zone', 'to_zone'
    )[:20]

    from cargo.models import Shipment
    cargo_in_warehouse = Shipment.objects.filter(
        current_warehouse=warehouse, is_deleted=False
    ).select_related('customer')[:20]

    from packages.models import Package
    packages_in_warehouse = Package.objects.filter(
        current_warehouse=warehouse
    ).select_related('shipment')[:20]

    return render(request, 'warehouse/warehouse_detail.html', {
        'warehouse': warehouse,
        'zones': zones,
        'recent_movements': recent_movements,
        'cargo_in_warehouse': cargo_in_warehouse,
        'packages_in_warehouse': packages_in_warehouse,
    })


@login_required
def warehouse_receiving(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    from cargo.models import Shipment, ShipmentStatusHistory, CargoEvent

    awaiting = Shipment.objects.filter(
        status__in=['awaiting_receiving', 'received'],
        current_warehouse=warehouse,
        is_deleted=False,
    ).select_related('customer', 'origin_branch')[:50]

    if request.method == 'POST':
        shipment_id = request.POST.get('shipment_id')
        action = request.POST.get('action', 'receive')

        if shipment_id:
            shipment = get_object_or_404(Shipment, pk=shipment_id, is_deleted=False)

            if action == 'receive':
                old_status = shipment.status
                shipment.status = 'received'
                shipment.current_warehouse = warehouse
                shipment.save()

                ShipmentStatusHistory.objects.create(
                    shipment=shipment,
                    previous_status=old_status,
                    new_status='received',
                    changed_by=request.user,
                    branch=warehouse.branch,
                    location=warehouse.name,
                    reason=f'Received at warehouse {warehouse.name}',
                    source='manual',
                )
                CargoEvent.objects.create(
                    shipment=shipment,
                    event_type='status_change',
                    description=f'Shipment received at warehouse {warehouse.name}',
                    created_by=request.user,
                )
                messages.success(request, f'Shipment {shipment.tracking_id} received.')

            elif action == 'put_away':
                old_status = shipment.status
                shipment.status = 'in_warehouse'
                shipment.save()

                ShipmentStatusHistory.objects.create(
                    shipment=shipment,
                    previous_status=old_status,
                    new_status='in_warehouse',
                    changed_by=request.user,
                    branch=warehouse.branch,
                    location=warehouse.name,
                    reason=f'Put away in warehouse {warehouse.name}',
                    source='manual',
                )
                CargoEvent.objects.create(
                    shipment=shipment,
                    event_type='status_change',
                    description=f'Shipment put away in warehouse {warehouse.name}',
                    created_by=request.user,
                )
                messages.success(request, f'Shipment {shipment.tracking_id} put away in warehouse.')

        return redirect('warehouse:receiving', pk=pk)

    return render(request, 'warehouse/warehouse_receiving.html', {
        'warehouse': warehouse,
        'awaiting_shipments': awaiting,
    })


@login_required
def warehouse_dispatch(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    from cargo.models import Shipment, ShipmentStatusHistory, CargoEvent

    ready_for_dispatch = Shipment.objects.filter(
        status__in=['ready_for_dispatch', 'sorted'],
        current_warehouse=warehouse,
        is_deleted=False,
    ).select_related('customer', 'destination_branch')[:50]

    if request.method == 'POST':
        shipment_id = request.POST.get('shipment_id')
        action = request.POST.get('action', 'dispatch')

        if shipment_id:
            shipment = get_object_or_404(Shipment, pk=shipment_id, is_deleted=False)

            if action == 'sort':
                old_status = shipment.status
                shipment.status = 'sorted'
                shipment.save()

                ShipmentStatusHistory.objects.create(
                    shipment=shipment,
                    previous_status=old_status,
                    new_status='sorted',
                    changed_by=request.user,
                    branch=warehouse.branch,
                    location=warehouse.name,
                    reason='Sorted for dispatch',
                    source='manual',
                )
                CargoEvent.objects.create(
                    shipment=shipment,
                    event_type='status_change',
                    description=f'Shipment sorted for dispatch at {warehouse.name}',
                    created_by=request.user,
                )
                messages.success(request, f'Shipment {shipment.tracking_id} sorted.')

            elif action == 'load':
                old_status = shipment.status
                shipment.status = 'loaded'
                shipment.save()

                ShipmentStatusHistory.objects.create(
                    shipment=shipment,
                    previous_status=old_status,
                    new_status='loaded',
                    changed_by=request.user,
                    branch=warehouse.branch,
                    location=warehouse.name,
                    reason='Loaded for dispatch',
                    source='manual',
                )
                CargoEvent.objects.create(
                    shipment=shipment,
                    event_type='status_change',
                    description=f'Shipment loaded for dispatch at {warehouse.name}',
                    created_by=request.user,
                )
                messages.success(request, f'Shipment {shipment.tracking_id} loaded for dispatch.')

        return redirect('warehouse:dispatch', pk=pk)

    return render(request, 'warehouse/warehouse_dispatch.html', {
        'warehouse': warehouse,
        'ready_shipments': ready_for_dispatch,
    })


@login_required
def warehouse_movements(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    queryset = warehouse.movements.select_related(
        'shipment', 'package', 'scanned_by', 'from_zone', 'to_zone', 'from_bin', 'to_bin'
    )

    movement_type = request.GET.get('type', '')
    if movement_type:
        queryset = queryset.filter(movement_type=movement_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    movements = paginator.get_page(page)

    return render(request, 'warehouse/warehouse_movements.html', {
        'warehouse': warehouse,
        'movements': movements,
        'movement_type': movement_type,
        'movement_types': WarehouseMovement.MOVEMENT_TYPES,
    })


@login_required
def warehouse_zones(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    zones = warehouse.zones.prefetch_related('shelves', 'shelves__bins')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'create_zone':
            zone_name = request.POST.get('zone_name', '').strip()
            zone_code = request.POST.get('zone_code', '').strip()
            zone_type = request.POST.get('zone_type', 'storage')
            capacity = int(request.POST.get('capacity', 500))

            if zone_name and zone_code:
                WarehouseZone.objects.create(
                    warehouse=warehouse,
                    name=zone_name,
                    code=zone_code,
                    zone_type=zone_type,
                    capacity=capacity,
                )
                messages.success(request, f'Zone {zone_name} created.')
            else:
                messages.error(request, 'Zone name and code are required.')

        elif action == 'create_shelf':
            zone_id = request.POST.get('zone_id')
            shelf_name = request.POST.get('shelf_name', '').strip()
            shelf_code = request.POST.get('shelf_code', '').strip()
            max_bins = int(request.POST.get('max_bins', 10))

            if zone_id and shelf_name and shelf_code:
                zone = get_object_or_404(WarehouseZone, pk=zone_id, warehouse=warehouse)
                WarehouseShelf.objects.create(
                    zone=zone,
                    name=shelf_name,
                    code=shelf_code,
                    max_bins=max_bins,
                )
                messages.success(request, f'Shelf {shelf_name} created in zone {zone.name}.')
            else:
                messages.error(request, 'All fields are required.')

        elif action == 'create_bin':
            shelf_id = request.POST.get('shelf_id')
            bin_name = request.POST.get('bin_name', '').strip()
            bin_code = request.POST.get('bin_code', '').strip()
            max_capacity = int(request.POST.get('max_capacity', 50))

            if shelf_id and bin_name and bin_code:
                shelf = get_object_or_404(WarehouseShelf, pk=shelf_id)
                WarehouseBin.objects.create(
                    shelf=shelf,
                    name=bin_name,
                    code=bin_code,
                    max_capacity=max_capacity,
                )
                messages.success(request, f'Bin {bin_name} created on shelf {shelf.name}.')
            else:
                messages.error(request, 'All fields are required.')

        return redirect('warehouse:zones', pk=pk)

    return render(request, 'warehouse/warehouse_zones.html', {
        'warehouse': warehouse,
        'zones': zones,
    })
