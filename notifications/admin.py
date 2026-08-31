from django.contrib import admin
from .models import NotificationTemplate, Notification, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'channel', 'is_active', 'organization', 'created_at')
    list_filter = ('event', 'channel', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'notification_type')
    search_fields = ('title', 'message')
    readonly_fields = ('read_at', 'created_at')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('channel', 'recipient_address', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('channel', 'status')
    search_fields = ('recipient_address', 'subject')
    readonly_fields = ('sent_at', 'created_at')
