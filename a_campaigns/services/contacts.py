"""Higher-level contact handling: normalisation and persistence to models."""

from ..models import CampaignRecipient, RecipientValidationStatus
from .validation import validate_contacts


def normalize_address_set(primary_email, secondary_emails):
    """Return the sorted, de-duplicated, lowercased address set (semicolon-joined).

    Used for idempotency and for the "one To line" recipients.
    """
    addresses = [primary_email] + list(secondary_emails)
    return ";".join(sorted({str(a).lower() for a in addresses if a}))


def persist_recipients(campaign, rows, mapping, placeholders=None):
    """Validate rows against a mapping and upsert CampaignRecipient rows.

    Returns ``{"contacts": [...], "unknown_placeholders": [...]}``.
    """
    result = validate_contacts(rows, mapping, placeholders)

    existing = {
        r.source_row_number: r
        for r in CampaignRecipient.objects.filter(campaign=campaign)
    }

    for contact in result["contacts"]:
        recipient = existing.get(contact["rowNumber"])
        if recipient is None:
            recipient = CampaignRecipient(
                campaign=campaign, source_row_number=contact["rowNumber"]
            )

        has_issues = bool(contact["issues"])
        recipient.full_name = contact["name"]
        recipient.salutation_name = contact["salutationName"]
        recipient.company = contact["company"]
        recipient.role = contact["role"]
        recipient.primary_email = contact["primaryEmail"]
        recipient.secondary_emails_json = contact["secondaryEmails"]
        recipient.custom_fields_json = contact["custom"]
        recipient.normalized_address_set = normalize_address_set(
            contact["primaryEmail"], contact["secondaryEmails"]
        )
        recipient.validation_status = (
            RecipientValidationStatus.INVALID if has_issues else RecipientValidationStatus.VALID
        )
        recipient.validation_issues_json = contact["issues"]
        # NOTE: `excluded` and `processing_status` are left untouched so an
        # explicit exclusion survives a re-upload/re-validation.
        recipient.save()

    return result


def clear_recipients(campaign):
    """Remove all recipients for a campaign (used on re-upload)."""
    CampaignRecipient.objects.filter(campaign=campaign).delete()
