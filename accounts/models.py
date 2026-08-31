import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    """System roles with granular permissions"""
    ROLE_CHOICES = [
        ('super_admin', 'Super Administrator'),
        ('system_admin', 'System Administrator'),
        ('head_office_manager', 'Head Office Manager'),
        ('branch_manager', 'Branch Manager'),
        ('booking_officer', 'Booking Officer'),
        ('customer_service', 'Customer Service Officer'),
        ('warehouse_officer', 'Warehouse Officer'),
        ('dispatch_officer', 'Dispatch Officer'),
        ('transport_manager', 'Transport Manager'),
        ('driver', 'Driver'),
        ('delivery_officer', 'Delivery Officer'),
        ('accountant', 'Accountant'),
        ('finance_manager', 'Finance Manager'),
        ('auditor', 'Auditor'),
        ('customer', 'Customer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.display_name


class Permission(models.Model):
    """Granular permissions"""
    MODULE_CHOICES = [
        ('cargo', 'Cargo'),
        ('package', 'Package'),
        ('warehouse', 'Warehouse'),
        ('vehicle', 'Vehicle'),
        ('driver', 'Driver'),
        ('gps', 'GPS'),
        ('payment', 'Payment'),
        ('invoice', 'Invoice'),
        ('document', 'Document'),
        ('report', 'Report'),
        ('user', 'User'),
        ('settings', 'Settings'),
        ('audit', 'Audit'),
    ]
    ACTION_CHOICES = [
        ('view', 'View'), ('create', 'Create'), ('update', 'Update'),
        ('delete', 'Delete'), ('manage', 'Manage'), ('scan', 'Scan'),
        ('receive', 'Receive'), ('dispatch', 'Dispatch'), ('transfer', 'Transfer'),
        ('deliver', 'Deliver'), ('cancel', 'Cancel'), ('assign', 'Assign'),
        ('export', 'Export'), ('refund', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.CharField(max_length=30, choices=MODULE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    codename = models.CharField(max_length=60, unique=True, editable=False)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['module', 'action']
    
    def save(self, *args, **kwargs):
        self.codename = f"{self.module}.{self.action}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.codename


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('role', 'permission')
    
    def __str__(self):
        return f"{self.role} - {self.permission}"


class User(AbstractUser):
    """Extended user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def has_admin_role(self):
        return self.role and self.role.name in ('super_admin', 'system_admin')
    
    @property
    def is_auditor(self):
        return self.role and self.role.name == 'auditor'
    
    def has_permission(self, codename):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return self.role.permissions.filter(permission__codename=codename).exists()


class UserProfile(models.Model):
    """Extended profile data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Tanzania')
    date_of_birth = models.DateField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    theme_preference = models.CharField(
        max_length=10, choices=[('light','Light'),('dark','Dark'),('system','System')],
        default='system'
    )
    notification_email = models.BooleanField(default=True)
    notification_sms = models.BooleanField(default=True)
    notification_in_app = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user}"


class UserActivity(models.Model):
    """Track user sessions and activity"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
