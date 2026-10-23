from django.test import SimpleTestCase

from a_campaigns.services.validation import (
    campaign_readiness_issues,
    detect_mapping,
    parse_csv,
    validate_contacts,
)

MAPPING = {
    "name": "Name",
    "company": "Company",
    "email": "Email",
    "secondary email": "Secondary Email",
    "role": "Role",
}


def row(name, company, email, secondary="", role=""):
    return {
        "Name": name,
        "Company": company,
        "Email": email,
        "Secondary Email": secondary,
        "Role": role,
    }


class ParseCsvTests(SimpleTestCase):
    def test_basic_csv(self):
        result = parse_csv("name,company,email\nAlice,Acme,alice@x.com\n")
        self.assertEqual(result["headers"], ["name", "company", "email"])
        self.assertEqual(len(result["rows"]), 1)

    def test_quoted_fields_and_commas(self):
        result = parse_csv('name,company,email\n"Smith, John","A, B & Co",j@x.com\n')
        self.assertEqual(result["rows"][0]["company"], "A, B & Co")

    def test_bom_and_empty_rows_dropped(self):
        result = parse_csv("\ufeffname,company,email\n\nAlice,Acme,alice@x.com\n\n")
        self.assertEqual(result["headers"][0], "name")
        self.assertEqual(len(result["rows"]), 1)


class DetectMappingTests(SimpleTestCase):
    def test_case_insensitive(self):
        mapping = detect_mapping(["Name", "Company", "Email Address", "Email"])
        self.assertEqual(mapping["name"], "Name")
        self.assertEqual(mapping["company"], "Company")
        self.assertEqual(mapping["email"], "Email")
        self.assertNotIn("role", mapping)


class ValidateContactsTests(SimpleTestCase):
    def test_valid_contact(self):
        result = validate_contacts([row("Alice", "Acme", "alice@x.com")], MAPPING)
        contact = result["contacts"][0]
        self.assertEqual(contact["issues"], [])
        self.assertEqual(contact["primaryEmail"], "alice@x.com")
        self.assertEqual(contact["salutationName"], "Alice")

    def test_missing_fields(self):
        result = validate_contacts([row("", "", "")], MAPPING)
        self.assertEqual(
            result["contacts"][0]["issues"],
            ["Missing name", "Missing company", "Missing primary email"],
        )

    def test_invalid_primary_email(self):
        result = validate_contacts([row("Alice", "Acme", "not-an-email")], MAPPING)
        self.assertIn("Invalid primary email", result["contacts"][0]["issues"])

    def test_invalid_secondary_email(self):
        result = validate_contacts(
            [row("Alice", "Acme", "alice@x.com", "bad; alice2@x.com")], MAPPING
        )
        self.assertIn("Invalid secondary email", result["contacts"][0]["issues"])

    def test_duplicate_primary(self):
        result = validate_contacts(
            [row("A", "Acme", "dup@x.com"), row("B", "Beta", "dup@x.com")], MAPPING
        )
        self.assertIn("Duplicate primary email (row 2)", result["contacts"][1]["issues"])

    def test_secondary_duplicated_as_primary(self):
        result = validate_contacts(
            [
                row("A", "Acme", "a@x.com", "shared@x.com"),
                row("B", "Beta", "shared@x.com"),
            ],
            MAPPING,
        )
        self.assertIn("Address also used on row 2", result["contacts"][1]["issues"])

    def test_secondary_emails_lowercased(self):
        result = validate_contacts(
            [row("A", "Acme", "a@x.com", "B@X.com; c@x.com")], MAPPING
        )
        self.assertEqual(result["contacts"][0]["secondaryEmails"], ["b@x.com", "c@x.com"])

    def test_unknown_placeholders(self):
        result = validate_contacts([row("A", "Acme", "a@x.com")], MAPPING, ["Name", "Region"])
        self.assertEqual(result["unknownPlaceholders"], ["Region"])

    def test_known_placeholders_not_flagged(self):
        result = validate_contacts(
            [row("A", "Acme", "a@x.com")], MAPPING, ["Name", "Company", "Role", "Email"]
        )
        self.assertEqual(result["unknownPlaceholders"], [])


class CampaignReadinessIssuesTests(SimpleTestCase):
    def test_all_clear(self):
        issues = campaign_readiness_issues(
            {
                "campaignName": "Q4",
                "account": "me@x.com",
                "folder": "Q4",
                "validCount": 5,
                "blockingCount": 0,
                "unknownPlaceholders": [],
            }
        )
        self.assertEqual(issues, [])

    def test_missing_everything(self):
        issues = campaign_readiness_issues({})
        self.assertIn("Enter a campaign name", issues)
        self.assertIn("Choose an Outlook account", issues)
        self.assertIn("Choose a Drafts destination", issues)
        self.assertIn("Include at least one valid recipient", issues)

    def test_blocking_errors(self):
        issues = campaign_readiness_issues(
            {
                "campaignName": "Q4",
                "account": "me@x.com",
                "folder": "Q4",
                "validCount": 1,
                "blockingCount": 2,
            }
        )
        self.assertIn("Resolve or exclude invalid recipients", issues)

    def test_attachments_required(self):
        issues = campaign_readiness_issues(
            {
                "campaignName": "Q4",
                "account": "me@x.com",
                "folder": "Q4",
                "validCount": 1,
                "blockingCount": 0,
                "attachmentsRequired": True,
                "attachmentCount": 0,
            }
        )
        self.assertIn("Attach the required PDF file", issues)
