import uuid

from django.conf import settings
from django.db import models


class EmailTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_templates"
    )
    name = models.CharField(max_length=160)
    subject = models.TextField(blank=True, default="")
    body = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="templates_owner_name_unique"),
        ]

    def __str__(self):
        return self.name
