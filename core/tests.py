import json

from django.test import TestCase

from accounts.models import User
from audit.models import AuditLog
from core.signals import _create_audit_log


class AuditSignalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")

    def test_create_audit_log_uses_actor_fields(self):
        _create_audit_log(
            self.user,
            "config_change",
            "Organization",
            entity_id="uuid-123",
            entity_str="Test Org",
            details={"key": "value"},
        )
        log = AuditLog.objects.get(entity_type="Organization", entity_id="uuid-123")
        self.assertEqual(log.actor, self.user)
        self.assertEqual(log.entity_str, "Test Org")
        self.assertEqual(log.after_data, {"key": "value"})
        self.assertEqual(json.loads(log.details), {"key": "value"})

    def test_create_audit_log_without_user(self):
        _create_audit_log(None, "status_change", "Shipment", entity_id="trk-1")
        log = AuditLog.objects.get(entity_type="Shipment", entity_id="trk-1")
        self.assertIsNone(log.actor)
        self.assertEqual(log.action, "status_change")

    def test_create_audit_log_handles_missing_fields(self):
        _create_audit_log(None, "activity", "Generic")
        self.assertTrue(AuditLog.objects.filter(action="activity", entity_type="Generic").exists())