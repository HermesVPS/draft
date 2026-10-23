import uuid

from django.conf import settings
from django.db import models

from .campaign_models import Campaign
from .recipient_models import CampaignRecipient
from .run_models import CampaignRun


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="audit_events"
    )
    recipient = models.ForeignKey(
        CampaignRecipient, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="audit_events",
    )
    run = models.ForeignKey(
        CampaignRun, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="audit_events",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="audit_events"
    )
    event_type = models.CharField(max_length=100)
    event_summary = models.TextField(blank=True, default="")
    provider_request_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["campaign", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.created_at:%Y-%m-%d %H:%M})"
