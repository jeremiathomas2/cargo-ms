import uuid
from django.db import models


class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='branches')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Tanzania')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_headquarters = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    manager = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_branches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class BranchSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.OneToOneField(Branch, on_delete=models.CASCADE, related_name='settings')
    operating_hours_start = models.TimeField(default='08:00')
    operating_hours_end = models.TimeField(default='17:00')
    timezone = models.CharField(max_length=50, default='Africa/Dar_es_Salaam')
    currency = models.CharField(max_length=10, default='TZS')
    tracking_prefix = models.CharField(max_length=10, default='CMS')
    auto_receive = models.BooleanField(default=False)
    auto_dispatch = models.BooleanField(default=False)
    gps_required = models.BooleanField(default=True)
    insurance_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.branch}"
