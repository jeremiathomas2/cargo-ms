from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from customers.models import Customer
from .models import ShipmentTemplate, CorporateAPIKey, BulkBookingUpload


class SelfServiceUserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")
        self.customer = Customer.objects.create(
            customer_number="C-0001",
            company_name="Test Co",
            phone="+255700000000",
        )

    def login(self):
        self.client.force_login(self.user)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("self_service:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders(self):
        self.login()
        response = self.client.get(reverse("self_service:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_users_roles_theme_numbering_render(self):
        self.login()
        for name in ["users", "roles", "theme", "numbering"]:
            response = self.client.get(reverse(f"self_service:{name}"))
            self.assertEqual(response.status_code, 200, name)

    def test_role_create_with_name_only(self):
        self.login()
        response = self.client.post(
            reverse("self_service:roles"),
            {"action": "create_role", "name": "Dispatcher"},
        )
        self.assertEqual(response.status_code, 302)
        from accounts.models import Role
        self.assertTrue(Role.objects.filter(name="Dispatcher", display_name="Dispatcher").exists())


class ShipmentTemplateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")
        self.customer = Customer.objects.create(
            customer_number="C-0001",
            company_name="Test Co",
            phone="+255700000000",
        )

    def login(self):
        self.client.force_login(self.user)

    def test_create_and_delete_template(self):
        self.login()
        response = self.client.post(
            reverse("self_service:shipment_templates"),
            {
                "action": "create_template",
                "name": "Weekly Route",
                "customer": self.customer.pk,
                "origin": "Dar es Salaam",
                "destination": "Mwanza",
                "weight": "12.5",
                "is_recurring": "on",
                "recurrence_interval": "weekly",
            },
        )
        self.assertEqual(response.status_code, 302)
        template = ShipmentTemplate.objects.get(name="Weekly Route")
        self.assertEqual(template.customer, self.customer)
        self.assertTrue(template.is_recurring)
        self.assertEqual(str(template.weight), "12.50")

        response = self.client.post(
            reverse("self_service:shipment_templates"),
            {"action": "delete_template", "template_id": template.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ShipmentTemplate.objects.filter(pk=template.pk).exists())

    def test_create_template_requires_fields(self):
        self.login()
        response = self.client.post(
            reverse("self_service:shipment_templates"),
            {"action": "create_template", "name": "Missing fields"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ShipmentTemplate.objects.filter(name="Missing fields").exists())

    def test_list_renders(self):
        self.login()
        response = self.client.get(reverse("self_service:shipment_templates"))
        self.assertEqual(response.status_code, 200)


class ApiKeyViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")
        self.customer = Customer.objects.create(
            customer_number="C-0001",
            company_name="Test Co",
            phone="+255700000000",
        )

    def login(self):
        self.client.force_login(self.user)

    def test_create_toggle_delete_key(self):
        self.login()
        response = self.client.post(
            reverse("self_service:api_keys"),
            {"action": "create_key", "key_name": "Production", "customer": self.customer.pk, "rate_limit": "500"},
        )
        self.assertEqual(response.status_code, 302)
        key = CorporateAPIKey.objects.get(key_name="Production")
        self.assertTrue(key.api_key)
        self.assertTrue(key.secret_key)
        self.assertEqual(key.rate_limit, 500)
        self.assertTrue(key.is_active)

        response = self.client.post(
            reverse("self_service:api_keys"),
            {"action": "toggle_key", "key_id": key.pk},
        )
        self.assertEqual(response.status_code, 302)
        key.refresh_from_db()
        self.assertFalse(key.is_active)

        response = self.client.post(
            reverse("self_service:api_keys"),
            {"action": "delete_key", "key_id": key.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CorporateAPIKey.objects.filter(pk=key.pk).exists())

    def test_list_renders(self):
        self.login()
        response = self.client.get(reverse("self_service:api_keys"))
        self.assertEqual(response.status_code, 200)


class BulkUploadViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")

    def login(self):
        self.client.force_login(self.user)

    def test_upload_valid_csv(self):
        self.login()
        file = SimpleUploadedFile("bookings.csv", b"tracking,origin\ntrk-1,Dar")
        response = self.client.post(reverse("self_service:bulk_uploads"), {"action": "upload_file", "file": file})
        self.assertEqual(response.status_code, 302)
        upload = BulkBookingUpload.objects.get(uploaded_by=self.user)
        self.assertEqual(upload.status, BulkBookingUpload.Status.PENDING)

    def test_upload_rejects_wrong_extension(self):
        self.login()
        file = SimpleUploadedFile("notes.txt", b"hello")
        response = self.client.post(reverse("self_service:bulk_uploads"), {"action": "upload_file", "file": file})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BulkBookingUpload.objects.filter(uploaded_by=self.user).exists())

    def test_upload_requires_file(self):
        self.login()
        response = self.client.post(reverse("self_service:bulk_uploads"), {"action": "upload_file"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BulkBookingUpload.objects.filter(uploaded_by=self.user).exists())

    def test_list_renders(self):
        self.login()
        response = self.client.get(reverse("self_service:bulk_uploads"))
        self.assertEqual(response.status_code, 200)