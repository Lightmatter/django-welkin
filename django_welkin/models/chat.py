import uuid

from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel, _Welkin
from .patient import Patient
from .user import User


class Chat(WelkinModel):
    message = models.TextField()
    created_at = models.DateTimeField(help_text="When the message was created.")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("chat")
        verbose_name_plural = _("chats")

    def __str__(self):
        return self.message

    @property
    def sender(self):
        return self.user if self.user else self.patient

    @staticmethod
    def parse_uuid(external_id):
        return uuid.UUID(external_id[2:])

    def sync_from_welkin(self):
        raise NotImplementedError("Chat is synced through the Patient model.")

    def save(self, *args, **kwargs):
        if not self.pk:
            chat = _Welkin().Patient(id=self.patient.id).Chat(message=self.message)
            chat.create()

            self.id = Chat.parse_uuid(chat.externalId)
            self.message = chat.message
            self.created_at = parse_datetime(chat.createdAt)

        super().save(*args, **kwargs)
