from django.db import models


class SignupAttempt(models.Model):
    fingerprint = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fingerprint} @ {self.created_at}"