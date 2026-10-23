"""Salutation and placeholder personalisation, ported from ``campaign.mjs``."""

import re

from .text_utils import escape_html


def salutation_name(full_name):
    """Return the salutation token for a full name.

    - Strips trailing punctuation from the first-name token.
    - If the name begins with Dr/Mr/Mrs/Ms/Miss (optionally followed by a
      period), the following token is used instead.
    """
    parts = [p for p in str(full_name).strip().split() if p]
    if parts and re.match(r"^(dr|mr|mrs|ms|miss)\.?$", parts[0], re.IGNORECASE):
        parts.pop(0)
    if not parts:
        return ""
    return re.sub(r"[.,;:!?]+$", "", parts[0])


def find_placeholders(subject, body):
    """Return the unique, de-duplicated, trimmed placeholder keys in [brackets]."""
    keys = re.findall(r"\[([^\]]+)\]", str(subject)) + re.findall(r"\[([^\]]+)\]", str(body))
    return list(dict.fromkeys(k.strip() for k in keys))


def _resolve(contact, key):
    """Resolve a placeholder key against a contact dict (case-sensitive, then
    case-insensitive fallback), returning a sentinel when unknown."""
    if key in contact:
        return contact[key]
    lower = key.lower()
    for k, v in contact.items():
        if isinstance(k, str) and k.lower() == lower:
            return v
    return None


def _build_values(contact):
    values = dict(contact)
    # Custom fields carried on the contact (spreadsheet columns) participate too.
    values.update(contact.get("custom") or {})
    values.update(contact.get("source") or {})
    values["Name"] = contact.get("salutationName") or salutation_name(contact.get("name", ""))
    values["Company"] = contact.get("company", "")
    values["Role"] = contact.get("role") or ""
    values["Email"] = contact.get("primaryEmail") or ""
    return values


def personalise(text, contact):
    """Replace [Placeholder] tokens in text using the contact's values."""
    values = _build_values(contact)

    def repl(match):
        key = match.group(1)
        resolved = _resolve(values, key)
        return str(resolved) if resolved is not None else f"[{key}]"

    return re.sub(r"\[([^\]]+)\]", repl, str(text))


def personalise_html(html, contact):
    """Like personalise but HTML-escapes substituted values."""
    values = _build_values(contact)

    def repl(match):
        key = match.group(1)
        resolved = _resolve(values, key)
        return escape_html(resolved) if resolved is not None else f"[{key}]"

    return re.sub(r"\[([^\]]+)\]", repl, str(html))
