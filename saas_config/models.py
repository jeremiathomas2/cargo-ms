import uuid

from django.db import models


class Organization(models.Model):
    class Plan(models.TextChoices):
        FREE = "free", "Free"
        STANDARD = "standard", "Standard"
        ENTERPRISE = "enterprise", "Enterprise"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subdomain = models.CharField(max_length=200, blank=True, default="")
    logo = models.ImageField(upload_to="organizations/logos/", blank=True)
    favicon = models.ImageField(upload_to="organizations/favicons/", blank=True)
    primary_color = models.CharField(max_length=7, default="#D96A16")
    secondary_color = models.CharField(max_length=7, default="#38AEF2")
    accent_color = models.CharField(max_length=7, default="#6D5BD0")
    currency = models.CharField(max_length=10, default="TZS")
    timezone = models.CharField(max_length=50, default="Africa/Dar_es_Salaam")
    is_active = models.BooleanField(default=True)
    plan = models.CharField(max_length=10, choices=Plan.choices, default=Plan.FREE)
    max_users = models.PositiveIntegerField(null=True, blank=True)
    max_shipments = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class OrganizationDomain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="domains",
    )
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "domain"]
        verbose_name = "Organization Domain"
        verbose_name_plural = "Organization Domains"

    def __str__(self):
        return f"{self.domain} ({self.organization})"


class TenantQuota(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="quota",
    )
    users_used = models.PositiveIntegerField(default=0)
    shipments_used = models.PositiveIntegerField(default=0)
    storage_used_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    api_requests_used = models.PositiveIntegerField(default=0)
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        verbose_name = "Tenant Quota"
        verbose_name_plural = "Tenant Quotas"

    def __str__(self):
        return f"Quota for {self.organization}"
