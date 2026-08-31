import uuid
from django.db import models


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('status_change', 'Status Change'),
        ('payment', 'Payment'),
        ('delivery', 'Delivery'),
        ('export', 'Export'),
        ('config_change', 'Config Change'),
        ('permission_change', 'Permission Change'),
        ('assign', 'Assign'),
        ('dispatch', 'Dispatch'),
        ('receive', 'Receive'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=50)
    entity_str = models.CharField(max_length=200, blank=True)
    before_data = models.JSONField(default=dict, blank=True)
    after_data = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    request_id = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='audit_logs')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"{self.action} {self.entity_type}:{self.entity_id} by {self.actor}"
