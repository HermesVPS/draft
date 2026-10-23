"""Contact parsing, column mapping and validation, ported from ``campaign.mjs``."""

import csv
import io

from .personalisation import salutation_name
from .text_utils import is_email, split_emails

# Canonical fields that are always valid placeholders (plus the built-in
# email/secondary-email placeholders the personaliser supports).
KNOWN_PLACEHOLDERS = {"name", "company", "role", "email", "secondary email"}

CANONICAL_COLUMNS = ["name", "company", "email", "secondary email", "role"]


def parse_csv(text):
    """Parse CSV text into ``{headers, rows}`` using the stdlib csv module.

    Handles BOM, quoted fields, escaped quotes and CRLF. Empty rows are dropped.
    """
    text = str(text)
    if text.startswith("\ufeff"):
        text = text[1:]
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    rows = [row for row in reader if any(str(v).strip() for v in row.values())]
    return {"headers": headers, "rows": rows}


def detect_mapping(headers):
    """Auto-detect canonical columns among headers (case-insensitive)."""
    result = {}
    for key in CANONICAL_COLUMNS:
        match = next((h for h in headers if str(h).strip().lower() == key), None)
        if match:
            result[key] = match
    return result


def validate_contacts(rows, mapping, placeholders=None):
    """Validate parsed rows against a column mapping.

    ``mapping`` is ``{canonical: header_name}``. Returns a dict with
    ``contacts`` (enriched, per-contact issues) and ``unknownPlaceholders``.
    """
    placeholders = placeholders or []
    primary_seen = {}
    all_seen = {}
    available = {str(v).lower() for v in mapping.values() if v}
    unknown_placeholders = [
        p
        for p in placeholders
        if p.lower() not in KNOWN_PLACEHOLDERS and p.lower() not in available
    ]

    contacts = []
    for index, row in enumerate(rows):
        def get(key):
            header = mapping.get(key)
            if not header:
                return ""
            return str(row.get(header, "") or "").strip()

        primary = get("email").lower()
        secondary = [v.lower() for v in split_emails(get("secondary email"))]
        issues = []

        if not get("name"):
            issues.append("Missing name")
        if not get("company"):
            issues.append("Missing company")
        if not primary:
            issues.append("Missing primary email")
        elif not is_email(primary):
            issues.append("Invalid primary email")
        if any(not is_email(v) for v in secondary):
            issues.append("Invalid secondary email")

        if primary in primary_seen:
            issues.append(f"Duplicate primary email (row {primary_seen[primary]})")
        elif primary:
            primary_seen[primary] = index + 2

        for address in [primary] + secondary:
            if not address:
                continue
            if address in all_seen:
                issues.append(f"Address also used on row {all_seen[address]}")
            else:
                all_seen[address] = index + 2

        mapped_headers = set(mapping.values())
        contacts.append(
            {
                "rowNumber": index + 2,
                "name": get("name"),
                "company": get("company"),
                "role": get("role"),
                "primaryEmail": primary,
                "secondaryEmails": secondary,
                "salutationName": salutation_name(get("name")),
                "source": row,
                "custom": {k: v for k, v in row.items() if k not in mapped_headers},
                "issues": list(dict.fromkeys(issues)),
                "excluded": False,
            }
        )

    return {"contacts": contacts, "unknownPlaceholders": unknown_placeholders}


def campaign_readiness_issues(input_):
    """Return the list of blocking issues preventing a campaign from starting."""
    issues = []
    if not str(input_.get("campaignName") or "").strip():
        issues.append("Enter a campaign name")
    if not str(input_.get("account") or "").strip():
        issues.append("Choose an Outlook account")
    if not str(input_.get("folder") or "").strip():
        issues.append("Choose a Drafts destination")
    if not int(input_.get("validCount") or 0):
        issues.append("Include at least one valid recipient")
    if int(input_.get("blockingCount") or 0):
        issues.append("Resolve or exclude invalid recipients")
    if input_.get("unknownPlaceholders"):
        issues.append(f"Map placeholders: {', '.join(input_['unknownPlaceholders'])}")
    if input_.get("attachmentsRequired") and not int(input_.get("attachmentCount") or 0):
        issues.append("Attach the required PDF file")
    if (
        input_.get("dateApprovalRequired")
        and int(input_.get("dateCount") or 0)
        and not input_.get("dateApproved")
    ):
        issues.append("Approve the detected dates below")
    return issues
