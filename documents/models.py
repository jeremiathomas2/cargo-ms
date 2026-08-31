import uuid
from django.db import models


class DocumentTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    document_type = models.CharField(max_length=30, choices=[
        ('booking_confirmation', 'Booking Confirmation'),
        ('cargo_receipt', 'Cargo Receipt'),
        ('quotation', 'Quotation'),
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('waybill', 'Waybill'),
        ('shipping_label', 'Shipping Label'),
        ('package_label', 'Package Label'),
        ('manifest', 'Manifest'),
        ('loading_sheet', 'Loading Sheet'),
        ('dispatch_note', 'Dispatch Note'),
        ('trip_sheet', 'Trip Sheet'),
        ('delivery_note', 'Delivery Note'),
        ('proof_of_delivery', 'Proof of Delivery'),
        ('claim_form', 'Claim Form'),
        ('damage_report', 'Damage Report'),
        ('payment_statement', 'Payment Statement'),
        ('customs_declaration', 'Customs Declaration'),
        ('transit_bond', 'Transit Bond Document'),
    ])
    subject = models.CharField(max_length=200, blank=True)
    body_html = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='document_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Document(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent'),
        ('archived', 'Archived'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_number = models.CharField(max_length=30, unique=True)
    template = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    document_type = models.CharField(max_length=30)
    title = models.CharField(max_length=200)

    # Polymorphic links (nullable FK to various entities)
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    invoice = models.ForeignKey('billing.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    delivery = models.ForeignKey('delivery.Delivery', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    claim = models.ForeignKey('claims.Claim', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_documents')

    file = models.FileField(upload_to='documents/%Y/%m/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    version = models.PositiveIntegerField(default=1)

    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.document_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.document_number:
            from core.utils import generate_document_number
            prefix = self.document_type[:3].upper() if self.document_type else 'DOC'
            self.document_number = generate_document_number(prefix)
        super().save(*args, **kwargs)


class DocumentVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to='documents/versions/%Y/%m/')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ('document', 'version_number')

    def __str__(self):
        return f"{self.document.document_number} v{self.version_number}"
