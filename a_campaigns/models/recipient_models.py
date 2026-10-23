import uuid

from django.db import models

from .campaign_models import Campaign
from .choices import RecipientProcessingStatus, RecipientValidationStatus


class CampaignRecipient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="recipients"
    )
    source_row_number = models.PositiveIntegerField()
    full_name = models.CharField(max_length=255)
    salutation_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, default="")
    primary_email = models.CharField(max_length=320)
    normalized_address_set = models.TextField(blank=True, default="")
    secondary_emails_json = models.JSONField(default=list, blank=True)
    custom_fields_json = models.JSONField(default=dict, blank=True)
    validation_status = models.CharField(
        max_length=20,
        choices=RecipientValidationStatus.choices,
        default=RecipientValidationStatus.PENDING,
    )
    validation_issues_json = models.JSONField(default=list, blank=True)
    processing_status = models.CharField(
        max_length=30,
        choices=RecipientProcessingStatus.choices,
        default=RecipientProcessingStatus.PENDING,
    )
    excluded = models.BooleanField(default=False)
    exclusion_reason = models.CharField(max_length=500, blank=True, default="")
    subject_hash = models.CharField(max_length=64, null=True, blank=True)
    attachment_set_hash = models.CharField(max_length=64, null=True, blank=True)
    outlook_draft_id = models.CharField(max_length=200, null=True, blank=True)
    destination_folder_id = models.CharField(max_length=200, blank=True, default="")
    attempt_count = models.PositiveIntegerField(default=0)
    retry_after = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["source_row_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "source_row_number"],
                name="recipients_campaign_source_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["campaign", "processing_status"]),
        ]

    @property
    def secondary_emails(self):
        return self.secondary_emails_json or []

    @property
    def custom_fields(self):
        return self.custom_fields_json or {}

    @property
    def validation_issues(self):
        return self.validation_issues_json or []

    def __str__(self):
        return f"{self.full_name} <{self.primary_email}>"
