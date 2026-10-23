import uuid

from django.conf import settings
from django.db import models

from .campaign_models import Campaign
from .choices import RunStatus


class CampaignRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="runs"
    )
    status = models.CharField(max_length=20, choices=RunStatus.choices)
    authorised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="authorised_runs"
    )
    authorised_at = models.DateTimeField()
    total_recipients = models.PositiveIntegerField(default=0)
    completed_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    reconciliation_count = models.PositiveIntegerField(default=0)
    current_batch = models.PositiveIntegerField(default=0)
    last_progress_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["campaign", "status"]),
        ]

    def __str__(self):
        return f"Run {self.id} ({self.status})"
