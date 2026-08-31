import uuid
from django.db import models


class Claim(models.Model):
    CLAIM_TYPES = [
        ('lost', 'Lost Cargo'),
        ('damaged', 'Damaged Cargo'),
        ('missing', 'Missing Package'),
        ('wrong_delivery', 'Wrong Delivery'),
        ('delay', 'Delay'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_investigation', 'Under Investigation'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('compensated', 'Compensated'),
        ('closed', 'Closed'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim_number = models.CharField(max_length=30, unique=True)
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.CASCADE, related_name='claims')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='claims')
    claim_type = models.CharField(max_length=15, choices=CLAIM_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    description = models.TextField()
    claimed_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approved_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    compensation_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_claims')
    investigation_notes = models.TextField(blank=True)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='claims')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_claims')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.claim_number} - {self.get_claim_type_display()}"

    def save(self, *args, **kwargs):
        if not self.claim_number:
            from core.utils import generate_document_number
            self.claim_number = generate_document_number('CLM')
        super().save(*args, **kwargs)


class ClaimDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='claims/documents/')
    document_type = models.CharField(max_length=30, choices=[
        ('photo', 'Photo'),
        ('report', 'Report'),
        ('receipt', 'Receipt'),
        ('police_report', 'Police Report'),
        ('other', 'Other'),
    ])
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.claim.claim_number}"
