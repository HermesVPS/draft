from django.db import models


class CampaignStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    READY = "ready", "Ready"
    RUNNING = "running", "Running"
    WAITING = "waiting", "Waiting"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class RecipientProcessingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CREATING_DRAFT = "creating_draft", "Creating draft"
    ATTACHING = "attaching", "Attaching"
    MOVING = "moving", "Moving"
    VERIFYING = "verifying", "Verifying"
    COMPLETE = "complete", "Complete"
    FAILED = "failed", "Failed"
    WAITING_FOR_RETRY = "waiting_for_retry", "Waiting for retry"
    RECONCILIATION_REQUIRED = "reconciliation_required", "Reconciliation required"
    CANCELLED = "cancelled", "Cancelled"
    EXCLUDED = "excluded", "Excluded"


class RecipientValidationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    VALID = "valid", "Valid"
    INVALID = "invalid", "Invalid"


class FileRole(models.TextChoices):
    CONTACTS = "contacts", "Contact list"
    TEMPLATE = "template", "Template"
    ATTACHMENT = "attachment", "Attachment"


class RunStatus(models.TextChoices):
    RUNNING = "running", "Running"
    PAUSED = "paused", "Paused"
    WAITING = "waiting", "Waiting"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
