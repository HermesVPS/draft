import uuid

from django.conf import settings
from django.db import models

from .choices import CampaignStatus


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns"
    )
    name = models.CharField(max_length=160)
    status = models.CharField(
        max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.DRAFT
    )
    outlook_connection_label = models.CharField(max_length=200, blank=True, default="")
    destination_folder_name = models.CharField(max_length=240, blank=True, default="")
    destination_folder_id = models.CharField(max_length=200, blank=True, default="")
    subject_original = models.TextField(blank=True, default="")
    subject_outgoing = models.TextField(blank=True, default="")
    body_original = models.TextField(blank=True, default="")
    body_outgoing = models.TextField(blank=True, default="")
    batch_size = models.PositiveSmallIntegerField(default=8)
    safe_punctuation_enabled = models.BooleanField(default=True)
    date_review_required = models.BooleanField(default=False)
    attachments_required = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
        ]

    def __str__(self):
        return self.name
