import json
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from audit.models import AuditLog
from core.middleware import get_current_request

logger = logging.getLogger(__name__)


def _create_audit_log(user, action, entity_type, entity_id=None, details=None, entity_str=""):
    ip_address = None
    request = get_current_request()
    if request:
        from core.utils import get_client_ip
        ip_address = get_client_ip(request)
        if user is None and request.user.is_authenticated:
            user = request.user

    try:
        details = details or {}
        AuditLog.objects.create(
            actor=user,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else "",
            entity_str=str(entity_str) if entity_str else str(entity_id or ""),
            after_data=details if isinstance(details, dict) else {},
            details=json.dumps(details, default=str) if isinstance(details, dict) else str(details or ""),
            ip_address=ip_address,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000] if request else "",
            request_id=request.META.get("HTTP_X_REQUEST_ID", "") if request else "",
            branch=getattr(user, "branch", None) if user else None,
            organization=getattr(user, "organization", None) if user else None,
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")


@receiver(post_save, sender='cargo.Shipment')
def audit_cargo_status_change(sender, instance, created, update_fields=None, **kwargs):
    if created:
        _create_audit_log(
            user=getattr(instance, 'created_by', None),
            action='create',
            entity_type='Shipment',
            entity_id=instance.pk,
            entity_str=getattr(instance, 'tracking_id', None),
            details={
                'tracking_id': getattr(instance, 'tracking_id', None),
                'status': instance.status,
                'origin': getattr(instance, 'origin', None),
                'destination': getattr(instance, 'destination', None),
            },
        )
    else:
        if update_fields and 'status' in update_fields:
            _create_audit_log(
                user=getattr(instance, 'created_by', None),
                action='status_change',
                entity_type='Shipment',
                entity_id=instance.pk,
                entity_str=getattr(instance, 'tracking_id', None),
                details={
                    'tracking_id': getattr(instance, 'tracking_id', None),
                    'status': instance.status,
                },
            )


@receiver(post_save, sender='payments.Payment')
def audit_payment_creation(sender, instance, created, **kwargs):
    if created:
        _create_audit_log(
            user=getattr(instance, 'recorded_by', None),
            action='payment',
            entity_type='Payment',
            entity_id=instance.pk,
            entity_str=getattr(instance, 'payment_number', None),
            details={
                'payment_number': getattr(instance, 'payment_number', None),
                'amount': str(getattr(instance, 'amount', 0)),
                'currency': getattr(instance, 'currency', 'TZS'),
                'payment_method': str(getattr(instance.payment_method, 'code', '') if instance.payment_method else ''),
                'status': instance.status,
            },
        )


@receiver(post_save, sender='delivery.Delivery')
def audit_delivery_confirmation(sender, instance, created, update_fields=None, **kwargs):
    if update_fields and 'status' in update_fields and instance.status == 'delivered':
        _create_audit_log(
            user=getattr(instance, 'assigned_to', None),
            action='delivery',
            entity_type='Delivery',
            entity_id=instance.pk,
            entity_str=getattr(instance, 'delivery_number', None),
            details={
                'delivery_number': getattr(instance, 'delivery_number', None),
                'status': instance.status,
            },
        )