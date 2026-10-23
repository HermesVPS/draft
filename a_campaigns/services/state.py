"""Recipient state machine and idempotency key, ported from ``campaign.mjs``."""

TERMINAL = {"complete", "excluded"}


def recipient_transition(current, event, detail=None):
    """Return the next processing_status for a recipient given an event.

    ``current`` is the current status; ``event`` is the transition trigger;
    ``detail`` is an optional dict (e.g. ``{"found": bool}`` for ``reconcile``).
    """
    detail = detail or {}
    if current in TERMINAL and event != "reconcile":
        return current
    if event == "start":
        return "creating_draft" if current in ("pending", "failed") else current
    if event == "rate_limited":
        return "waiting_for_retry"
    if event == "uncertain":
        return "reconciliation_required"
    if event == "draft_created":
        return "attaching"
    if event == "attachments_verified":
        return "moving"
    if event == "move_failed":
        return "failed"
    if event == "verified":
        return "complete"
    if event == "cancel":
        return "cancelled" if current in ("pending", "waiting_for_retry", "failed") else current
    if event == "reconcile":
        return "verifying" if detail.get("found") else "failed"
    return current


def idempotency_key(campaign_id, recipient_id, address_set, subject_hash, attachment_hash):
    """Stable key identifying one draft-creation attempt for a recipient."""
    addresses = ";".join(sorted(str(v).lower() for v in address_set))
    return "|".join(
        [str(campaign_id), str(recipient_id), addresses, str(subject_hash), str(attachment_hash)]
    )
