from django.test import SimpleTestCase

from a_campaigns.services.state import idempotency_key, recipient_transition


class RecipientTransitionTests(SimpleTestCase):
    def test_start_from_pending(self):
        self.assertEqual(recipient_transition("pending", "start"), "creating_draft")

    def test_start_from_failed(self):
        self.assertEqual(recipient_transition("failed", "start"), "creating_draft")

    def test_start_from_complete_is_ignored(self):
        self.assertEqual(recipient_transition("complete", "start"), "complete")

    def test_rate_limited(self):
        self.assertEqual(
            recipient_transition("creating_draft", "rate_limited"), "waiting_for_retry"
        )

    def test_uncertain(self):
        self.assertEqual(
            recipient_transition("creating_draft", "uncertain"), "reconciliation_required"
        )

    def test_draft_created(self):
        self.assertEqual(recipient_transition("creating_draft", "draft_created"), "attaching")

    def test_attachments_verified(self):
        self.assertEqual(recipient_transition("attaching", "attachments_verified"), "moving")

    def test_move_failed(self):
        self.assertEqual(recipient_transition("moving", "move_failed"), "failed")

    def test_verified(self):
        self.assertEqual(recipient_transition("moving", "verified"), "complete")

    def test_cancel_pending(self):
        self.assertEqual(recipient_transition("pending", "cancel"), "cancelled")

    def test_cancel_does_not_touch_complete(self):
        self.assertEqual(recipient_transition("complete", "cancel"), "complete")

    def test_reconcile_found(self):
        self.assertEqual(
            recipient_transition("reconciliation_required", "reconcile", {"found": True}),
            "verifying",
        )

    def test_reconcile_not_found(self):
        self.assertEqual(
            recipient_transition("reconciliation_required", "reconcile", {"found": False}),
            "failed",
        )

    def test_unknown_event_noop(self):
        self.assertEqual(recipient_transition("pending", "nonsense"), "pending")


class IdempotencyKeyTests(SimpleTestCase):
    def test_order_independent_addresses(self):
        a = idempotency_key("c1", "r1", {"b@x.com", "a@x.com"}, "sh", "ah")
        b = idempotency_key("c1", "r1", {"a@x.com", "b@x.com"}, "sh", "ah")
        self.assertEqual(a, b)

    def test_differs_on_subject_hash(self):
        a = idempotency_key("c1", "r1", {"a@x.com"}, "sh1", "ah")
        b = idempotency_key("c1", "r1", {"a@x.com"}, "sh2", "ah")
        self.assertNotEqual(a, b)
