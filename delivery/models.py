import uuid
from django.db import models


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('ready', 'Ready for Delivery'),
        ('assigned', 'Assigned'),
        ('out_for_delivery', 'Out for Delivery'),
        ('attempted', 'Attempted'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('returned', 'Returned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.OneToOneField('cargo.Shipment', on_delete=models.CASCADE, related_name='delivery')
    delivery_number = models.CharField(max_length=30, unique=True)
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    driver = models.ForeignKey('transportation.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')
    scheduled_date = models.DateField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    attempted_at = models.DateTimeField(null=True, blank=True)
    return_at = models.DateTimeField(null=True, blank=True)
    delivery_address = models.TextField()
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery {self.delivery_number} - {self.shipment.tracking_id}"

    def save(self, *args, **kwargs):
        if not self.delivery_number:
            from core.utils import generate_document_number
            self.delivery_number = generate_document_number('DEL')
        super().save(*args, **kwargs)


class DeliveryAttempt(models.Model):
    RESULT_CHOICES = [
        ('successful', 'Successful'),
        ('failed_refused', 'Refused'),
        ('failed_no_one', 'No One Home'),
        ('failed_wrong_address', 'Wrong Address'),
        ('failed_damaged', 'Damaged Refused'),
        ('failed_other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.PositiveIntegerField(default=1)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    attempted_at = models.DateTimeField(auto_now_add=True)
    attempted_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey('transportation.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True)
    next_attempt_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        return f"Attempt {self.attempt_number} - {self.delivery.delivery_number}"


class ProofOfDelivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name='proof_of_delivery')
    recipient_name = models.CharField(max_length=200)
    recipient_phone = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=10, blank=True)
    otp_verified = models.BooleanField(default=False)
    signature = models.ImageField(upload_to='pod/signatures/', blank=True, null=True)
    photo = models.ImageField(upload_to='pod/photos/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True)
    delivered_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    delivered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proof of Delivery'
        verbose_name_plural = 'Proofs of Delivery'

    def __str__(self):
        return f"POD - {self.delivery.delivery_number}"
