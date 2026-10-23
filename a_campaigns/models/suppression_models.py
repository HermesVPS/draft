import uuid

from django.conf import settings
from django.db import models


class SuppressionEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="suppression_entries"
    )
    email = models.CharField(max_length=320)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    source_mailbox = models.CharField(max_length=320)
    source_folder = models.CharField(max_length=255)
    source_message_id = models.CharField(max_length=500)
    source_received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-source_received_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "email"], name="suppression_owner_email_unique"),
            models.UniqueConstraint(
                fields=["owner", "source_message_id"], name="suppression_owner_message_unique"
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "created_at"]),
        ]

    def __str__(self):
        return self.email


class MailboxSyncState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mailbox_sync_states"
    )
    mailbox = models.CharField(max_length=320)
    folder_path = models.CharField(max_length=255)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_message_count = models.PositiveIntegerField(default=0)
    last_imported_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "mailbox", "folder_path"],
                name="sync_owner_mailbox_folder_unique",
            ),
        ]

    def __str__(self):
        return f"{self.mailbox}/{self.folder_path}"
