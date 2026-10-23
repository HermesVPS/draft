"""Email HTML sanitisation, ported from the MVP's ``server-email-html.ts``.

The MVP used sanitize-html (Node); we use bleach, which provides the closest
match: tag/attribute/protocol allowlists plus a CSS-property allowlist.
"""

import re

import bleach
from bleach.css_sanitizer import CSSSanitizer

ALLOWED_TAGS = [
    "a", "b", "blockquote", "br", "div", "em", "h1", "h2", "h3", "i", "li",
    "ol", "p", "s", "span", "strong", "table", "tbody", "td", "th", "thead",
    "tr", "u", "ul",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "target", "rel"],
    "*": ["style"],
    "td": ["colspan", "rowspan", "align"],
    "th": ["colspan", "rowspan", "align"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto", "tel"]

ALLOWED_CSS_PROPERTIES = [
    "color", "background-color", "text-align", "font-weight", "font-style",
    "text-decoration", "font-size", "font-family", "line-height",
]

# Tags whose content must be dropped entirely (script, embedded objects, etc.).
DROP_CONTENT_TAGS = [
    "script", "style", "object", "embed", "iframe", "form", "input", "button",
    "svg", "math", "img",
]

_css_sanitizer = CSSSanitizer(allowed_css_properties=ALLOWED_CSS_PROPERTIES)

_ENTITY_MAP = {
    "&nbsp;": " ",
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
}


def _strip_drop_tags(html):
    """Remove DROP_CONTENT_TAGS and their contents before allowlist sanitisation."""
    for tag in DROP_CONTENT_TAGS:
        html = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}\s*>", "", html, flags=re.IGNORECASE | re.DOTALL
        )
        html = re.sub(rf"<{tag}\b[^>]*/>", "", html, flags=re.IGNORECASE)
    return html


def sanitize_email_html(value):
    """Sanitize untrusted HTML to the safe email subset."""
    html = _strip_drop_tags(str(value))
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        css_sanitizer=_css_sanitizer,
    ).strip()


def plain_text(html):
    """Convert sanitized HTML to plain text, decoding entities."""
    text = re.sub(r"<[^>]*>", "", str(html))
    for entity, char in _ENTITY_MAP.items():
        text = text.replace(entity, char)
    return text.strip()


def extract_subject_from_html(html):
    """If the first block starts with SUBJECT:, split it out of the body."""
    match = re.match(r"^\s*<p(?:\s[^>]*)?>([\s\S]*?)</p>", str(html), re.IGNORECASE)
    if match:
        text = plain_text(match.group(1))
        if re.match(r"^SUBJECT:", text, re.IGNORECASE):
            subject = re.sub(r"^SUBJECT:\s*", "", text, flags=re.IGNORECASE)
            body = str(html)[match.end():].strip()
            return {"subject": subject, "body": body}
    return {"subject": "", "body": str(html)}
