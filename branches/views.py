from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from .models import Branch, BranchSetting

ITEMS_PER_PAGE = 25


@login_required
def branch_list(request):
    queryset = Branch.objects.select_related('manager')

    search = request.GET.get('q', '')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(city__icontains=search) |
            Q(country__icontains=search)
        )

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    branches = paginator.get_page(page)

    return render(request, 'branches/branch_list.html', {
        'branches': branches,
        'search': search,
    })


@login_required
def branch_create(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()

            if not name or not code:
                messages.error(request, 'Name and code are required.')
                return redirect('branches:create')

            branch = Branch(
                name=name,
                code=code,
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                country=request.POST.get('country', 'Tanzania'),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                is_headquarters=request.POST.get('is_headquarters') == 'on',
                is_active=True,
            )

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            if latitude and longitude:
                try:
                    branch.latitude = float(latitude)
                    branch.longitude = float(longitude)
                except (TypeError, ValueError):
                    pass

            branch.save()

            BranchSetting.objects.create(branch=branch)

            messages.success(request, f'Branch {branch.name} created successfully.')
            return redirect('branches:detail', pk=branch.pk)

        except Exception as e:
            messages.error(request, f'Error creating branch: {str(e)}')

    return render(request, 'branches/branch_form.html', {
        'editing': False,
    })


@login_required
def branch_detail(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    settings_obj = None
    if hasattr(branch, 'settings'):
        settings_obj = branch.settings

    staff = branch.staff.all()[:20]
    warehouses = branch.warehouses.all()
    vehicles = branch.vehicles.filter(is_active=True)[:20]
    shipments = branch.originating_shipments.filter(is_deleted=False).order_by('-created_at')[:20]

    return render(request, 'branches/branch_detail.html', {
        'branch': branch,
        'branch_settings': settings_obj,
        'staff': staff,
        'warehouses': warehouses,
        'vehicles': vehicles,
        'shipments': shipments,
    })


@login_required
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == 'POST':
        try:
            branch.name = request.POST.get('name', branch.name)
            branch.code = request.POST.get('code', branch.code)
            branch.address = request.POST.get('address', branch.address)
            branch.city = request.POST.get('city', branch.city)
            branch.country = request.POST.get('country', branch.country)
            branch.phone = request.POST.get('phone', branch.phone)
            branch.email = request.POST.get('email', branch.email)
            branch.is_headquarters = request.POST.get('is_headquarters') == 'on'
            branch.is_active = request.POST.get('is_active', 'on') == 'on'

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            if latitude:
                try:
                    branch.latitude = float(latitude)
                except (TypeError, ValueError):
                    pass
            else:
                branch.latitude = None
            if longitude:
                try:
                    branch.longitude = float(longitude)
                except (TypeError, ValueError):
                    pass
            else:
                branch.longitude = None

            branch.save()

            settings_obj, _ = BranchSetting.objects.get_or_create(branch=branch)
            settings_obj.operating_hours_start = request.POST.get('operating_hours_start', '08:00')
            settings_obj.operating_hours_end = request.POST.get('operating_hours_end', '17:00')
            settings_obj.timezone = request.POST.get('timezone', 'Africa/Dar_es_Salaam')
            settings_obj.currency = request.POST.get('currency', 'TZS')
            settings_obj.tracking_prefix = request.POST.get('tracking_prefix', 'CMS')
            settings_obj.auto_receive = request.POST.get('auto_receive') == 'on'
            settings_obj.auto_dispatch = request.POST.get('auto_dispatch') == 'on'
            settings_obj.gps_required = request.POST.get('gps_required', 'on') == 'on'
            settings_obj.insurance_default = request.POST.get('insurance_default') == 'on'
            settings_obj.save()

            messages.success(request, f'Branch {branch.name} updated successfully.')
            return redirect('branches:detail', pk=branch.pk)

        except Exception as e:
            messages.error(request, f'Error updating branch: {str(e)}')

    settings_obj = None
    if hasattr(branch, 'settings'):
        settings_obj = branch.settings

    return render(request, 'branches/branch_form.html', {
        'branch': branch,
        'branch_settings': settings_obj,
        'editing': True,
    })
