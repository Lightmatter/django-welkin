from django.db import models
from django.utils.translation import gettext_lazy as _


class WebhookMessage(models.Model):
    received_at = models.DateTimeField(
        help_text="When we received the event.", auto_now_add=True
    )
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["received_at"]),
        ]
        verbose_name = _("webhook message")
        verbose_name_plural = _("webhook messages")

    def __str__(self) -> str:
        return self.payload.get("eventEntity", "CHAT")
