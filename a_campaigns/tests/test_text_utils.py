from django.test import SimpleTestCase

from a_campaigns.services.text_utils import (
    escape_html,
    html_to_text,
    is_email,
    parse_text_template,
    safe_punctuation,
    safe_punctuation_html,
    split_emails,
)


class ParseTextTemplateTests(SimpleTestCase):
    def test_leading_blank_lines_before_subject(self):
        result = parse_text_template("\n\n\nSUBJECT: Hello there\n\nBody line one\nBody line two")
        self.assertEqual(result["subject"], "Hello there")
        self.assertEqual(result["body"], "\nBody line one\nBody line two")

    def test_no_subject_line(self):
        result = parse_text_template("\n\nJust a body\nSecond line")
        self.assertEqual(result["subject"], "")
        self.assertEqual(result["body"], "Just a body\nSecond line")

    def test_crlf_line_endings(self):
        result = parse_text_template("SUBJECT: Hi\r\nBody one\r\nBody two")
        self.assertEqual(result["subject"], "Hi")
        self.assertEqual(result["body"], "Body one\nBody two")

    def test_subject_prefix_removed_case_insensitive(self):
        result = parse_text_template("subject: Lowercase subject\nBody")
        self.assertEqual(result["subject"], "Lowercase subject")


class SafePunctuationTests(SimpleTestCase):
    def test_curly_apostrophes_and_quotes(self):
        self.assertEqual(safe_punctuation("It\u2019s \u2018okay\u2019 \u201cnow\u201d"), "It's 'okay' \"now\"")

    def test_en_and_em_dashes(self):
        self.assertEqual(safe_punctuation("a\u2013b c\u2014d"), "a - b c - d")

    def test_bullet_characters(self):
        self.assertEqual(safe_punctuation("\u2022 First\n\u2022 Second"), "- First\n- Second")

    def test_nonbreaking_space(self):
        self.assertEqual(safe_punctuation("a\u00a0b"), "a b")

    def test_no_rewording(self):
        text = "Please confirm the October allocation is ready."
        self.assertEqual(safe_punctuation(text), text)

    def test_html_skips_tags(self):
        html = "<strong>it\u2019s</strong>"
        self.assertEqual(safe_punctuation_html(html), "<strong>it's</strong>")


class EscapeHtmlTests(SimpleTestCase):
    def test_escapes_all_five(self):
        self.assertEqual(
            escape_html('<a href="x">& \'</a>'),
            "&lt;a href=&quot;x&quot;&gt;&amp; &#39;&lt;/a&gt;",
        )

    def test_none_becomes_empty(self):
        self.assertEqual(escape_html(None), "")


class HtmlToTextTests(SimpleTestCase):
    def test_converts_breaks_and_paragraphs(self):
        # Faithful to the MVP: inline tags become spaces, br/block closers become newlines.
        self.assertEqual(html_to_text("<p>One</p><br><p>Two</p>"), " One\n\n Two\n")
        self.assertEqual(html_to_text("A<br>B"), "A\nB")

    def test_decodes_entities(self):
        self.assertEqual(html_to_text("A &amp; B &lt; C"), "A & B < C")


class EmailHelpersTests(SimpleTestCase):
    def test_is_email_valid(self):
        self.assertTrue(is_email("user@example.com"))

    def test_is_email_invalid(self):
        self.assertFalse(is_email("not-an-email"))
        self.assertFalse(is_email("user@"))
        self.assertFalse(is_email(""))

    def test_split_emails(self):
        self.assertEqual(
            split_emails("a@x.com; b@x.com, c@x.com"),
            ["a@x.com", "b@x.com", "c@x.com"],
        )

    def test_split_emails_empty(self):
        self.assertEqual(split_emails(""), [])
