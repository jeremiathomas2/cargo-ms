import secrets
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Avg

from accounts.models import User, Role, UserProfile
from customers.models import Customer
from .models import ShipmentTemplate, CorporateAPIKey, BulkBookingUpload


@login_required
def settings_dashboard(request):
    total_users = User.objects.filter(is_active=True).count()
    total_roles = Role.objects.filter(is_active=True).count()
    template_count = ShipmentTemplate.objects.count()
    key_count = CorporateAPIKey.objects.filter(is_active=True).count()

    return render(request, 'self_service/dashboard.html', {
        'user_count': total_users,
        'role_count': total_roles,
        'template_count': template_count,
        'key_count': key_count,
    })


@login_required
def shipment_templates(request):
    queryset = ShipmentTemplate.objects.select_related("customer", "created_by").order_by("-created_at")
    search = request.GET.get("q", "")
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(origin__icontains=search) |
            Q(destination__icontains=search) |
            Q(customer__company_name__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )
    paginator = Paginator(queryset, 20)
    templates_page = paginator.get_page(request.GET.get("page", 1))

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "create_template":
            name = request.POST.get("name", "").strip()
            customer_id = request.POST.get("customer", "")
            origin = request.POST.get("origin", "").strip()
            destination = request.POST.get("destination", "").strip()
            if name and customer_id and origin and destination:
                try:
                    customer = Customer.objects.get(pk=customer_id)
                except Customer.DoesNotExist:
                    messages.error(request, "Please choose a valid customer.")
                else:
                    weight_raw = request.POST.get("weight", "").strip()
                    ShipmentTemplate.objects.create(
                        name=name,
                        customer=customer,
                        origin=origin,
                        destination=destination,
                        cargo_type=request.POST.get("cargo_type", "").strip(),
                        description=request.POST.get("description", "").strip(),
                        weight=Decimal(weight_raw) if weight_raw else None,
                        special_handling=request.POST.get("special_handling", "").strip(),
                        is_recurring=request.POST.get("is_recurring") == "on",
                        recurrence_interval=request.POST.get("recurrence_interval") or None,
                        created_by=request.user,
                    )
                    messages.success(request, f'Template "{name}" created.')
            else:
                messages.error(request, "Name, customer, origin and destination are required.")
        elif action == "delete_template":
            try:
                template = ShipmentTemplate.objects.get(pk=request.POST.get("template_id"))
                template.delete()
                messages.success(request, "Template deleted.")
            except ShipmentTemplate.DoesNotExist:
                messages.error(request, "Template not found.")
        return redirect("self_service:shipment_templates")

    return render(request, "self_service/shipment_templates.html", {
        "templates_page": templates_page,
        "customers": Customer.objects.filter(status="active").order_by("company_name", "first_name", "last_name"),
        "search": search,
        "recurring_count": queryset.filter(is_recurring=True).count(),
        "customer_count": Customer.objects.filter(status="active").count(),
        "recurrence_choices": ShipmentTemplate.RecurrenceInterval.choices,
    })


@login_required
def api_keys(request):
    queryset = CorporateAPIKey.objects.select_related("customer").order_by("-created_at")
    customer_filter = request.GET.get("customer", "")
    if customer_filter:
        queryset = queryset.filter(customer_id=customer_filter)
    paginator = Paginator(queryset, 20)
    keys_page = paginator.get_page(request.GET.get("page", 1))

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "create_key":
            key_name = request.POST.get("key_name", "").strip()
            customer_id = request.POST.get("customer", "")
            if key_name and customer_id:
                try:
                    customer = Customer.objects.get(pk=customer_id)
                except Customer.DoesNotExist:
                    messages.error(request, "Please choose a valid customer.")
                else:
                    CorporateAPIKey.objects.create(
                        customer=customer,
                        key_name=key_name,
                        api_key=secrets.token_hex(16),
                        secret_key=secrets.token_hex(32),
                        rate_limit=int(request.POST.get("rate_limit") or 1000),
                    )
                    messages.success(request, f'API key "{key_name}" created.')
            else:
                messages.error(request, "Key name and customer are required.")
        elif action == "toggle_key":
            try:
                key = CorporateAPIKey.objects.get(pk=request.POST.get("key_id"))
                key.is_active = not key.is_active
                key.save(update_fields=["is_active"])
                state = "activated" if key.is_active else "revoked"
                messages.success(request, f'API key "{key.key_name}" {state}.')
            except CorporateAPIKey.DoesNotExist:
                messages.error(request, "API key not found.")
        elif action == "delete_key":
            try:
                key = CorporateAPIKey.objects.get(pk=request.POST.get("key_id"))
                key.delete()
                messages.success(request, "API key deleted.")
            except CorporateAPIKey.DoesNotExist:
                messages.error(request, "API key not found.")
        return redirect("self_service:api_keys")

    return render(request, "self_service/api_keys.html", {
        "keys_page": keys_page,
        "customers": Customer.objects.filter(status="active").order_by("company_name", "first_name", "last_name"),
        "customer_filter": customer_filter,
        "active_count": CorporateAPIKey.objects.filter(is_active=True).count(),
        "avg_rate_limit": CorporateAPIKey.objects.aggregate(avg_rate_limit=Avg("rate_limit"))["avg_rate_limit"] or 0,
    })


@login_required
def bulk_uploads(request):
    queryset = BulkBookingUpload.objects.select_related("uploaded_by").order_by("-created_at")
    paginator = Paginator(queryset, 20)
    uploads_page = paginator.get_page(request.GET.get("page", 1))

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "upload_file":
            file = request.FILES.get("file")
            if file:
                if file.name.lower().endswith((".csv", ".xlsx", ".xls")):
                    upload = BulkBookingUpload.objects.create(
                        uploaded_by=request.user,
                        file=file,
                        status=BulkBookingUpload.Status.PENDING,
                    )
                    messages.success(request, f'File "{upload.file.name}" queued for processing.')
                else:
                    messages.error(request, "Only CSV and Excel files (.csv, .xlsx, .xls) are supported.")
            else:
                messages.error(request, "Please choose a file to upload.")
        return redirect("self_service:bulk_uploads")

    return render(request, "self_service/bulk_uploads.html", {
        "uploads_page": uploads_page,
        "completed_count": BulkBookingUpload.objects.filter(status=BulkBookingUpload.Status.COMPLETED).count(),
        "failed_count": BulkBookingUpload.objects.filter(status=BulkBookingUpload.Status.FAILED).count(),
    })


@login_required
def user_management(request):
    users = User.objects.select_related('role', 'branch', 'organization').all()

    search = request.GET.get('q', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )

    if role:
        users = users.filter(role__name=role)
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    roles = Role.objects.filter(is_active=True)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_user':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(pk=user_id)
                role_id = request.POST.get('role')
                user.role = Role.objects.get(pk=role_id) if role_id else None
                user.is_active = request.POST.get('is_active') == 'on'
                user.save(update_fields=['role', 'is_active'])
                messages.success(request, f'User {user.username} updated.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')

        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(pk=user_id)
                if user == request.user:
                    messages.error(request, 'You cannot deactivate yourself.')
                else:
                    user.is_active = False
                    user.save(update_fields=['is_active'])
                    messages.success(request, f'User {user.username} deactivated.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')

        return redirect('self_service:users')

    return render(request, 'self_service/user_management.html', {
        'users': users,
        'roles': roles,
        'search': search,
        'role_filter': role,
        'status_filter': status,
    })


@login_required
def role_management(request):
    roles = Role.objects.prefetch_related('permissions').all()

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'create_role':
            name = request.POST.get('name', '').strip()
            display_name = (request.POST.get('display_name', '').strip() or name)
            description = request.POST.get('description', '')

            if name and display_name:
                if not Role.objects.filter(name=name).exists():
                    Role.objects.create(
                        name=name,
                        display_name=display_name,
                        description=description,
                    )
                    messages.success(request, f'Role "{display_name}" created.')
                else:
                    messages.error(request, f'Role "{name}" already exists.')
            else:
                messages.error(request, 'Name and display name are required.')

        elif action == 'toggle_role':
            role_id = request.POST.get('role_id')
            try:
                role = Role.objects.get(pk=role_id)
                role.is_active = not role.is_active
                role.save(update_fields=['is_active'])
                status = 'activated' if role.is_active else 'deactivated'
                messages.success(request, f'Role "{role.display_name}" {status}.')
            except Role.DoesNotExist:
                messages.error(request, 'Role not found.')

        return redirect('self_service:roles')

    return render(request, 'self_service/role_management.html', {
        'roles': roles,
    })


@login_required
def theme_settings(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.theme_preference = request.POST.get('theme_preference', 'system')
        profile.save(update_fields=['theme_preference', 'updated_at'])
        messages.success(request, 'Theme settings updated.')
        return redirect('self_service:theme')

    return render(request, 'self_service/theme_settings.html', {
        'profile': profile,
    })


@login_required
def numbering_settings(request):
    from django.db import connection

    sequences = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'core_%sequence'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                try:
                    cursor.execute(f"SELECT prefix, year, current_value FROM {table} ORDER BY prefix, year DESC")
                    rows = cursor.fetchall()
                    for row in rows:
                        sequences.append({
                            'table': table,
                            'prefix': row[0],
                            'year': row[1],
                            'current_value': row[2],
                        })
                except Exception:
                    pass
    except Exception:
        pass

    return render(request, 'self_service/numbering_settings.html', {
        'sequences': sequences,
    })
