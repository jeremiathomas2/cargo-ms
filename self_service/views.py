from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from accounts.models import User, Role, UserProfile


@login_required
def settings_dashboard(request):
    total_users = User.objects.filter(is_active=True).count()
    total_roles = Role.objects.filter(is_active=True).count()

    return render(request, 'self_service/dashboard.html', {
        'total_users': total_users,
        'total_roles': total_roles,
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
            display_name = request.POST.get('display_name', '').strip()
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
