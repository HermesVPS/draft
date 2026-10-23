from django.test import SimpleTestCase

from a_campaigns.services.dates import find_numbered_dates


class FindNumberedDatesTests(SimpleTestCase):
    def test_long_form_date(self):
        self.assertIn("22 October 2026", find_numbered_dates("Meet on 22 October 2026 please."))

    def test_slash_date(self):
        self.assertIn("22/10/2026", find_numbered_dates("Due by 22/10/2026."))

    def test_iso_date(self):
        self.assertIn("2026-10-22", find_numbered_dates("Deadline 2026-10-22."))

    def test_general_wording_not_flagged(self):
        text = (
            "October allocation, Mid-November, six monthly sessions, "
            "twelve months to complete."
        )
        self.assertEqual(find_numbered_dates(text), [])

    def test_deduplicates(self):
        text = "On 22 October 2026 and again 22 October 2026."
        self.assertEqual(find_numbered_dates(text), ["22 October 2026"])
