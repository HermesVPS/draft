from django.contrib import admin

from .models import (
    AuditEvent,
    Campaign,
    CampaignFile,
    CampaignRecipient,
    CampaignRun,
    EmailTemplate,
    MailboxSyncState,
    MicrosoftAccount,
    SuppressionEntry,
)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "batch_size", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "owner__email", "destination_folder_name")
    ordering = ("-updated_at",)


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "company",
        "primary_email",
        "campaign",
        "validation_status",
        "processing_status",
        "excluded",
    )
    list_filter = ("validation_status", "processing_status", "excluded")
    search_fields = ("full_name", "company", "primary_email")
    raw_id_fields = ("campaign",)


@admin.register(CampaignFile)
class CampaignFileAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "file_role", "size_bytes", "campaign", "created_at")
    list_filter = ("file_role",)
    raw_id_fields = ("campaign", "uploaded_by")


@admin.register(CampaignRun)
class CampaignRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "campaign",
        "status",
        "total_recipients",
        "completed_count",
        "failed_count",
        "reconciliation_count",
        "started_at",
    )
    list_filter = ("status",)
    raw_id_fields = ("campaign", "authorised_by")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "campaign", "recipient", "user", "created_at")
    list_filter = ("event_type",)
    search_fields = ("event_summary",)
    raw_id_fields = ("campaign", "recipient", "run", "user")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "updated_at")
    search_fields = ("name", "owner__email")


@admin.register(SuppressionEntry)
class SuppressionEntryAdmin(admin.ModelAdmin):
    list_display = ("email", "display_name", "source_mailbox", "source_folder", "source_received_at")
    search_fields = ("email", "display_name")


@admin.register(MailboxSyncState)
class MailboxSyncStateAdmin(admin.ModelAdmin):
    list_display = ("mailbox", "folder_path", "last_checked_at", "last_imported_count")


@admin.register(MicrosoftAccount)
class MicrosoftAccountAdmin(admin.ModelAdmin):
    list_display = ("email", "owner", "connected_at")
    search_fields = ("email", "owner__email")
