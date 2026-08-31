import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from audit.models import AuditLog
from core.middleware import get_current_request

logger = logging.getLogger(__name__)


def _create_audit_log(user, action, model_name, object_id=None, details=None):
    ip_address = None
    request = get_current_request()
    if request:
        from core.utils import get_client_ip
        ip_address = get_client_ip(request)

    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else None,
            ip_address=ip_address,
            details=details or {},
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")


@receiver(post_save, sender='cargo.Shipment')
def audit_cargo_status_change(sender, instance, created, update_fields=None, **kwargs):
    if update_fields and 'status' in update_fields:
        _create_audit_log(
            user=getattr(instance, 'created_by', None),
            action='status_change',
            model_name='Shipment',
            object_id=instance.pk,
            details={
                'tracking_id': getattr(instance, 'tracking_id', None),
                'status': instance.status,
            },
        )


@receiver(post_save, sender='payments.Payment')
def audit_payment_creation(sender, instance, created, **kwargs):
    if created:
        _create_audit_log(
            user=getattr(instance, 'created_by', None),
            action='payment',
            model_name='Payment',
            object_id=instance.pk,
            details={
                'amount': str(getattr(instance, 'amount', 0)),
                'currency': getattr(instance, 'currency', 'TZS'),
                'payment_method': getattr(instance, 'payment_method', None),
            },
        )


@receiver(post_save, sender='delivery.Delivery')
def audit_delivery_confirmation(sender, instance, created, update_fields=None, **kwargs):
    if update_fields and 'status' in update_fields and instance.status == 'delivered':
        _create_audit_log(
            user=getattr(instance, 'confirmed_by', None),
            action='delivery',
            model_name='Delivery',
            object_id=instance.pk,
            details={
                'status': instance.status,
            },
        )
