import uuid
from django.db import models


class NotificationTemplate(models.Model):
    CHANNEL_CHOICES = [
        ('in_app', 'In App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]
    EVENT_CHOICES = [
        ('booking_created', 'Booking Created'),
        ('cargo_received', 'Cargo Received'),
        ('cargo_dispatched', 'Cargo Dispatched'),
        ('cargo_in_transit', 'Cargo In Transit'),
        ('cargo_arrived', 'Cargo Arrived'),
        ('ready_for_delivery', 'Ready for Delivery'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('payment_received', 'Payment Received'),
        ('invoice_generated', 'Invoice Generated'),
        ('payment_overdue', 'Payment Overdue'),
        ('claim_update', 'Claim Update'),
        ('gps_alert', 'GPS Alert'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    event = models.CharField(max_length=25, choices=EVENT_CHOICES)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    subject_template = models.CharField(max_length=200, blank=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey('saas_config.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='notification_templates')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event', 'channel']
        unique_together = ('event', 'channel', 'organization')

    def __str__(self):
        return f"{self.get_event_display()} - {self.get_channel_display()}"


class Notification(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('archived', 'Archived'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=25)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    link = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    shipment = models.ForeignKey('cargo.Shipment', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.recipient}"

    def mark_read(self):
        from django.utils import timezone
        self.status = 'read'
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at'])


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ('in_app', 'In App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    recipient_address = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.channel} → {self.recipient_address} ({self.status})"
