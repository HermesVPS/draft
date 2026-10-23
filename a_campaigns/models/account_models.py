import uuid

from django.conf import settings
from django.db import models


class MicrosoftAccount(models.Model):
    """A user's connected Microsoft 365 account (server-side OAuth state).

    The refresh token is stored encrypted at rest; see
    ``a_campaigns.services.provider.crypto`` for encrypt/decrypt helpers.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="microsoft_accounts"
    )
    msal_account_id = models.CharField(max_length=200)
    email = models.CharField(max_length=320)
    display_name = models.CharField(max_length=255, blank=True, default="")
    refresh_token_encrypted = models.TextField(blank=True, default="")
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "msal_account_id"], name="microsoft_owner_account_unique"
            ),
        ]

    def __str__(self):
        return f"{self.email} ({self.msal_account_id})"
