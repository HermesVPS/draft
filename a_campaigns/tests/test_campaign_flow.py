import io

from django.contrib.auth.models import User
from django.test import TestCase

from a_campaigns.models import Campaign


class CampaignContactFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="flow", email="flow@x.com", password="x")
        self.client.force_login(self.user)

    def _create_campaign(self):
        response = self.client.post(
            "/campaigns/new/",
            {
                "name": "Q4",
                "subject_original": "Hi [Name]",
                "body_original": "Hello [Company]",
                "batch_size": "8",
                "safe_punctuation_enabled": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        return Campaign.objects.get(owner=self.user)

    def test_full_contact_flow(self):
        campaign = self._create_campaign()

        # Upload CSV
        csv_data = b"Name,Company,Email,Secondary Email\nAlice,Acme,alice@x.com,bob@x.com\nBad,,bad-email,\n"
        response = self.client.post(
            f"/campaigns/{campaign.id}/contacts/",
            {"contacts_file": io.BytesIO(csv_data)},
            # client uses multipart automatically; provide filename via SimpleUploadedFile
        )
        # Re-post with a proper uploaded file object
        from django.core.files.uploadedfile import SimpleUploadedFile

        upload = SimpleUploadedFile("contacts.csv", csv_data, content_type="text/csv")
        response = self.client.post(f"/campaigns/{campaign.id}/contacts/", {"contacts_file": upload})
        self.assertEqual(response.status_code, 200)  # mapping form

        # Map columns (auto-detected names)
        response = self.client.post(
            f"/campaigns/{campaign.id}/contacts/map/",
            {
                "name": "Name",
                "company": "Company",
                "email": "Email",
                "secondary email": "Secondary Email",
                "role": "",
            },
        )
        self.assertEqual(response.status_code, 302)  # PRG to contacts

        # Validation summary
        response = self.client.get(f"/campaigns/{campaign.id}/contacts/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")

        recipients = campaign.recipients.all()
        self.assertEqual(recipients.count(), 2)
        alice = recipients.get(source_row_number=2)
        self.assertEqual(alice.validation_status, "valid")
        self.assertEqual(alice.secondary_emails, ["bob@x.com"])

        bad = recipients.get(source_row_number=3)
        self.assertEqual(bad.validation_status, "invalid")
        self.assertIn("Missing company", bad.validation_issues)

    def test_error_report(self):
        campaign = self._create_campaign()
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_data = b"Name,Company,Email\nBad,,bad\n"
        upload = SimpleUploadedFile("contacts.csv", csv_data, content_type="text/csv")
        self.client.post(f"/campaigns/{campaign.id}/contacts/", {"contacts_file": upload})
        self.client.post(
            f"/campaigns/{campaign.id}/contacts/map/",
            {"name": "Name", "company": "Company", "email": "Email", "secondary email": "", "role": ""},
        )
        response = self.client.get(f"/campaigns/{campaign.id}/contacts/errors/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
