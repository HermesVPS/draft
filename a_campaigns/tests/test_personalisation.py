from django.test import SimpleTestCase

from a_campaigns.services.personalisation import (
    find_placeholders,
    personalise,
    personalise_html,
    salutation_name,
)


class SalutationNameTests(SimpleTestCase):
    def test_dr_prefix_drops_title(self):
        self.assertEqual(salutation_name("Dr Rowena B."), "Rowena")

    def test_mr_prefix_drops_title(self):
        self.assertEqual(salutation_name("Mr John Smith"), "John")

    def test_miss_prefix_with_period(self):
        self.assertEqual(salutation_name("Miss. Jane Doe"), "Jane")

    def test_plain_name(self):
        self.assertEqual(salutation_name("Mary Johnson"), "Mary")

    def test_trailing_punctuation_stripped(self):
        self.assertEqual(salutation_name("Rowena."), "Rowena")

    def test_empty_name(self):
        self.assertEqual(salutation_name(""), "")


class FindPlaceholdersTests(SimpleTestCase):
    def test_deduplicates_and_trims(self):
        self.assertEqual(
            find_placeholders("Hi [Name]", "[Name], [ Company ] from [Name]"),
            ["Name", "Company"],
        )


class PersonaliseTests(SimpleTestCase):
    def _contact(self, **overrides):
        contact = {
            "name": "Rowena B",
            "company": "Acme",
            "role": "Manager",
            "primaryEmail": "rowena@acme.com",
            "salutationName": "Rowena",
            "custom": {"Region": "NSW"},
            "source": {"Region": "NSW"},
        }
        contact.update(overrides)
        return contact

    def test_builtin_placeholders(self):
        text = "Hi [Name], thanks for your work at [Company] as [Role]."
        out = personalise(text, self._contact())
        self.assertEqual(out, "Hi Rowena, thanks for your work at Acme as Manager.")

    def test_email_placeholder(self):
        self.assertEqual(personalise("[Email]", self._contact()), "rowena@acme.com")

    def test_custom_placeholder(self):
        self.assertEqual(personalise("[Region]", self._contact()), "NSW")

    def test_unknown_placeholder_left_untouched(self):
        self.assertEqual(personalise("[Missing]", self._contact()), "[Missing]")

    def test_salutation_falls_back_to_name(self):
        contact = self._contact(salutationName="")
        self.assertEqual(personalise("Hi [Name]", contact), "Hi Rowena")

    def test_html_escapes_values(self):
        contact = self._contact(company="A & B <Co>")
        self.assertEqual(
            personalise_html("[Company]", contact),
            "A &amp; B &lt;Co&gt;",
        )
