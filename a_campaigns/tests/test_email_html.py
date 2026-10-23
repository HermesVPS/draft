from django.test import SimpleTestCase

from a_campaigns.services.email_html import (
    extract_subject_from_html,
    plain_text,
    sanitize_email_html,
)


class SanitizeEmailHtmlTests(SimpleTestCase):
    def test_allows_safe_tags(self):
        html = "<p>Hello <strong>world</strong> <a href='https://x.com'>link</a></p>"
        out = sanitize_email_html(html)
        self.assertIn("<p>Hello <strong>world</strong>", out)
        self.assertIn("href=\"https://x.com\"", out)

    def test_strips_script_and_content(self):
        html = "<p>safe</p><script>alert(1)</script>"
        out = sanitize_email_html(html)
        self.assertNotIn("alert", out)
        self.assertNotIn("<script", out)

    def test_strips_iframe(self):
        html = "<p>safe</p><iframe src='https://evil.com'></iframe>"
        out = sanitize_email_html(html)
        self.assertNotIn("iframe", out)
        self.assertNotIn("evil.com", out)

    def test_drops_img_tag(self):
        html = "<p>text</p><img src='x.png' onerror='alert(1)'>"
        out = sanitize_email_html(html)
        self.assertNotIn("<img", out)

    def test_allows_style_subset(self):
        html = "<p style='color:red;font-weight:bold'>styled</p>"
        out = sanitize_email_html(html)
        self.assertIn("color:red", out)

    def test_rejects_javascript_href(self):
        html = "<a href='javascript:alert(1)'>bad</a>"
        out = sanitize_email_html(html)
        self.assertNotIn("javascript:", out)


class PlainTextTests(SimpleTestCase):
    def test_decodes_entities_and_strips_tags(self):
        self.assertEqual(plain_text("<p>A &amp; B</p>"), "A & B")


class ExtractSubjectTests(SimpleTestCase):
    def test_extracts_subject(self):
        html = "<p>SUBJECT: Hello</p><p>Body text</p>"
        result = extract_subject_from_html(html)
        self.assertEqual(result["subject"], "Hello")
        self.assertEqual(result["body"], "<p>Body text</p>")

    def test_no_subject_keeps_body(self):
        html = "<p>Just a body</p>"
        result = extract_subject_from_html(html)
        self.assertEqual(result["subject"], "")
        self.assertEqual(result["body"], html)
