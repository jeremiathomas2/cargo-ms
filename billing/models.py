import uuid
from django.db import models


class PricingRule(models.Model):
    CALCULATION_CHOICES = [
        ('flat', 'Flat Rate'),
        ('per_kg', 'Per KG'),
        ('per_cbm', 'Per CBM'),
        ('per_km', 'Per KM'),
        ('percentage', 'Percentage'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    origin = models.CharField(max_length=200, blank=True)
    destination = models.CharField(max_length=200, blank=True)
    cargo_type = models.CharField(max_length=20, blank=True)
    calculation = models.CharField(max_length=15, choices=CALCULATION_CHOICES, default='flat')
    base_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0, help_text='Higher priority = checked first')
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='pricing_rules')
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='pricing_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_calculation_display()})"


class Tax(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text='Percentage')
    is_active = models.BooleanField(default=True)
    applies_to = models.CharField(max_length=20, choices=[('shipping', 'Shipping'), ('handling', 'Handling'), ('all', 'All')], default='all')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class Discount(models.Model):
    TYPE_CHOICES = [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='percentage')
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_shipments = models.PositiveIntegerField(default=0)
    max_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='discounts')
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Insurance(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('expired', 'Expired'), ('claimed', 'Claimed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.CASCADE, related_name='insurances')
    policy_number = models.CharField(max_length=30, unique=True)
    insured_value = models.DecimalField(max_digits=12, decimal_places=2)
    premium = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    provider = models.CharField(max_length=100, blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.policy_number} - {self.shipment.tracking_id}"


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quotation_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='quotations')
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    cargo_type = models.CharField(max_length=20, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    volume = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    num_packages = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='TZS')
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.quotation_number

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            from core.utils import generate_document_number
            self.quotation_number = generate_document_number('QT')
        super().save(*args, **kwargs)


class QuotationItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['description']

    def __str__(self):
        return self.description


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overpaid', 'Overpaid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='invoices')
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='TZS')
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from core.utils import generate_document_number
            self.invoice_number = generate_document_number('INV')
        super().save(*args, **kwargs)

    def recalculate_status(self):
        from decimal import Decimal
        self.balance = self.total - self.amount_paid
        if self.amount_paid <= 0:
            self.status = 'unpaid' if self.status != 'draft' else 'draft'
        elif self.balance <= 0:
            self.status = 'paid' if self.balance == 0 else 'overpaid'
        elif self.amount_paid < self.total:
            self.status = 'partially_paid'
        self.save(update_fields=['balance', 'status', 'updated_at'])


class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['description']

    def __str__(self):
        return self.description
