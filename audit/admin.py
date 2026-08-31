from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'entity_type', 'entity_id', 'actor', 'ip_address', 'organization', 'timestamp')
    list_filter = ('action', 'entity_type')
    search_fields = ('entity_id', 'entity_str', 'details')
    readonly_fields = (
        'actor', 'action', 'entity_type', 'entity_id', 'entity_str',
        'before_data', 'after_data', 'ip_address', 'user_agent', 'branch',
        'request_id', 'details', 'organization', 'timestamp',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
