import uuid

from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel
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

    @classmethod
    def from_webhook(cls, payload):
        try:
            patient = Patient.objects.get(
                id=payload["patientId"], instance__name=payload["instanceName"]
            )
        except Patient.DoesNotExist:
            patient = Patient.from_webhook(payload)
            patient.sync()

        return cls(
            patient=patient,
            instance_id=patient.instance_id,
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            chat = self.client.Patient(id=self.patient_id).Chat(message=self.message)
            chat.create()

            self.id = Chat.parse_uuid(chat.externalId)
            self.message = chat.message
            self.created_at = parse_datetime(chat.createdAt)

        super().save(*args, **kwargs)

    def sync(self):
        for chat in self.client.Patient(id=self.patient_id).Chats().get(paginate=True):
            user = None
            if chat.sender["clientType"] == "USER":
                try:
                    user = User.objects.get(
                        id=chat.sender["id"], instance_id=self.instance_id
                    )
                except User.DoesNotExist:
                    user = User(id=chat.sender["id"], instance_id=self.instance_id)
                    user.sync()

            _, created = Chat.objects.get_or_create(
                id=Chat.parse_uuid(chat.externalId),
                message=chat.message,
                created_at=parse_datetime(chat.createdAt),
                instance_id=self.instance_id,
                patient=self.patient,
                user=user,
            )
            if not created:
                break
