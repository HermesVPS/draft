"""Pure text utilities ported from the MVP's ``lib/campaign.mjs``.

These functions have no Django or network dependencies so they can be tested
in isolation and reused by the provider layer and the campaign workflow.
"""

import re

# Match the MVP's EMAIL regex exactly.
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def parse_text_template(text):
    """Split a text template into subject + body.

    Ignores leading blank lines, then treats the first nonblank line beginning
    with ``SUBJECT:`` as the subject. The remaining lines form the body with
    paragraph breaks preserved.
    """
    lines = str(text).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    subject = ""
    if lines and re.match(r"^SUBJECT:", lines[0], re.IGNORECASE):
        subject = re.sub(r"^SUBJECT:\s*", "", lines.pop(0), flags=re.IGNORECASE)
    return {"subject": subject, "body": "\n".join(lines)}


def safe_punctuation(value):
    """Apply the "Outlook-safe punctuation" substitutions to plain text.

    Only controlled character substitutions — never rewording.
    """
    s = str(value)
    s = re.sub(r"[‘’]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[–—]", " - ", s)
    s = re.sub(r"^[\t ]*[•●▪]\s*", "- ", s, flags=re.MULTILINE)
    s = s.replace("\u00a0", " ")
    return s


def safe_punctuation_html(value):
    """safe_punctuation that skips over HTML tags so markup is untouched."""
    parts = re.split(r"(<[^>]+>)", str(value))
    return "".join(part if part.startswith("<") else safe_punctuation(part) for part in parts)


def escape_html(value):
    """Escape the five HTML-significant characters."""
    s = str(value) if value is not None else ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def html_to_text(html):
    """Lossy HTML -> plain text conversion for previews."""
    s = str(html)
    s = re.sub(r"<\s*br\s*/?\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</(p|div|h[1-6]|li|tr)>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"&nbsp;", " ", s, flags=re.IGNORECASE)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return s


def is_email(value):
    """Return True when the value is a syntactically valid email address."""
    return bool(EMAIL_RE.match(str(value or "").strip()))


def split_emails(value):
    """Split a value on commas/semicolons into trimmed, non-empty addresses."""
    return [v.strip() for v in re.split(r"[;,]", str(value or "")) if v.strip()]
