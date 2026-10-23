from django.contrib.auth.models import User
from django.test import TestCase

from a_campaigns.models import Campaign, RecipientValidationStatus
from a_campaigns.services.contacts import normalize_address_set, persist_recipients

MAPPING = {"name": "Name", "company": "Company", "email": "Email", "secondary email": "Secondary Email", "role": "Role"}


def make_row(name, company, email, secondary="", role=""):
    return {"Name": name, "Company": company, "Email": email, "Secondary Email": secondary, "Role": role}


class NormalizeAddressSetTests(TestCase):
    def test_sorted_deduplicated_lowercase(self):
        result = normalize_address_set("B@x.com", ["a@x.com", "b@x.com"])
        self.assertEqual(result, "a@x.com;b@x.com")

    def test_primary_included(self):
        result = normalize_address_set("z@x.com", [])
        self.assertEqual(result, "z@x.com")


class PersistRecipientsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", email="u@x.com", password="x")
        self.campaign = Campaign.objects.create(owner=self.user, name="C")

    def test_persists_valid_and_invalid(self):
        rows = [make_row("Alice", "Acme", "alice@x.com"), make_row("", "", "")]
        result = persist_recipients(self.campaign, rows, MAPPING)
        self.assertEqual(self.campaign.recipients.count(), 2)

        alice = self.campaign.recipients.get(source_row_number=2)
        self.assertEqual(alice.validation_status, RecipientValidationStatus.VALID)
        self.assertEqual(alice.validation_issues, [])
        self.assertEqual(alice.salutation_name, "Alice")

        broken = self.campaign.recipients.get(source_row_number=3)
        self.assertEqual(broken.validation_status, RecipientValidationStatus.INVALID)
        self.assertIn("Missing name", broken.validation_issues)

    def test_upsert_preserves_processing_status(self):
        rows = [make_row("Alice", "Acme", "alice@x.com")]
        persist_recipients(self.campaign, rows, MAPPING)
        recipient = self.campaign.recipients.get()
        recipient.processing_status = "complete"
        recipient.save()

        persist_recipients(self.campaign, rows, MAPPING)  # re-validate
        recipient.refresh_from_db()
        self.assertEqual(recipient.processing_status, "complete")

    def test_normalized_address_set(self):
        rows = [make_row("Alice", "Acme", "Alice@x.com", "b@x.com")]
        persist_recipients(self.campaign, rows, MAPPING)
        recipient = self.campaign.recipients.get()
        self.assertEqual(recipient.normalized_address_set, "alice@x.com;b@x.com")
