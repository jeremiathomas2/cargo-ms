from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from saas_config.models import Organization
from .models import ReportTemplate, ReportExport


class ReportPageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")

    def login(self):
        self.client.force_login(self.user)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders(self):
        self.login()
        response = self.client.get(reverse("reports:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_all_report_types_render(self):
        self.login()
        for key in ["shipment_summary", "revenue", "customer_shipments", "branch_performance", "delivery_performance"]:
            response = self.client.get(reverse("reports:report", kwargs={"report_type": key}))
            self.assertEqual(response.status_code, 200, key)

    def test_unknown_report_type_404(self):
        self.login()
        response = self.client.get(reverse("reports:report", kwargs={"report_type": "nope"}))
        self.assertEqual(response.status_code, 404)


class ReportTemplateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")
        self.org = Organization.objects.create(name="Test Org", slug="test-org")

    def login(self):
        self.client.force_login(self.user)

    def test_create_delete_template(self):
        self.login()
        response = self.client.post(
            reverse("reports:templates"),
            {
                "action": "create_template",
                "name": "Weekly Revenue",
                "report_type": "revenue",
                "organization": self.org.pk,
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        template = ReportTemplate.objects.get(name="Weekly Revenue")
        self.assertEqual(template.report_type, "revenue")
        self.assertEqual(template.organization, self.org)
        self.assertTrue(template.is_active)

        response = self.client.post(
            reverse("reports:templates"),
            {"action": "delete_template", "template_id": template.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ReportTemplate.objects.filter(pk=template.pk).exists())

    def test_toggle_template(self):
        self.login()
        template = ReportTemplate.objects.create(
            name="Monthly", report_type="monthly_cargo", organization=self.org
        )
        response = self.client.post(
            reverse("reports:templates"),
            {"action": "toggle_template", "template_id": template.pk},
        )
        self.assertEqual(response.status_code, 302)
        template.refresh_from_db()
        self.assertFalse(template.is_active)

    def test_templates_renders(self):
        self.login()
        response = self.client.get(reverse("reports:templates"))
        self.assertEqual(response.status_code, 200)


class ReportExportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")
        self.org = Organization.objects.create(name="Test Org", slug="test-org")

    def login(self):
        self.client.force_login(self.user)

    def test_create_export(self):
        self.login()
        response = self.client.post(
            reverse("reports:exports"),
            {"action": "create_export", "report_type": "revenue", "export_format": "csv"},
        )
        self.assertEqual(response.status_code, 302)
        export = ReportExport.objects.get(requested_by=self.user)
        self.assertEqual(export.status, ReportExport.Status.PENDING)
        self.assertEqual(export.report_type, "revenue")

    def test_create_export_linked_template(self):
        self.login()
        template = ReportTemplate.objects.create(
            name="Revenue Weekly", report_type="revenue", organization=self.org, is_active=True
        )
        response = self.client.post(
            reverse("reports:exports"),
            {"action": "create_export", "report_type": "revenue", "export_format": "pdf", "organization": self.org.pk},
        )
        self.assertEqual(response.status_code, 302)
        export = ReportExport.objects.get(requested_by=self.user)
        self.assertEqual(export.template, template)

    def test_exports_renders(self):
        self.login()
        response = self.client.get(reverse("reports:exports"))
        self.assertEqual(response.status_code, 200)