from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import Notification

from accounts.models import UserProfile


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)

    status_filter = request.GET.get('status', '')
    if status_filter == 'unread':
        notifications = notifications.filter(status='unread')
    elif status_filter == 'read':
        notifications = notifications.filter(status='read')

    notifications = notifications.select_related('shipment')[:100]

    unread_count = Notification.objects.filter(recipient=request.user, status='unread').count()

    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'status_filter': status_filter,
        'unread_count': unread_count,
    })


@login_required
def mark_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user,
    )
    notification.mark_read()
    messages.success(request, 'Notification marked as read.')

    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    if request.method != 'POST':
        messages.error(request, 'POST method required.')
        return redirect('notifications:list')

    updated = Notification.objects.filter(
        recipient=request.user,
        status='unread',
    ).update(status='read', read_at=timezone.now())

    messages.success(request, f'{updated} notification(s) marked as read.')
    return redirect('notifications:list')


@login_required
def notification_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.notification_email = request.POST.get('notification_email') == 'on'
        profile.notification_sms = request.POST.get('notification_sms') == 'on'
        profile.notification_in_app = request.POST.get('notification_in_app') == 'on'
        profile.save(update_fields=['notification_email', 'notification_sms', 'notification_in_app', 'updated_at'])
        messages.success(request, 'Notification preferences updated.')
        return redirect('notifications:preferences')

    return render(request, 'notifications/notification_preferences.html', {
        'profile': profile,
    })
