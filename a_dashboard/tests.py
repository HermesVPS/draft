from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/account/", response["Location"])
