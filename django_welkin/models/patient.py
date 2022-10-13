from django.apps import apps
from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel, _Welkin
from .user import User


class Patient(WelkinModel):
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)

    class Meta:
        verbose_name = _("patient")
        verbose_name_plural = _("patients")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def sync_from_welkin(self):
        patient = _Welkin().Patient(id=self.id).get()

        self.first_name = patient.firstName
        self.last_name = patient.lastName

        self.save()

    def sync_chat(self):
        for chat in _Welkin().Patient(id=self.id).Chats().get(paginate=True):
            user = None
            if chat.sender["clientType"] == "USER":
                user, _ = User.objects.get_or_create(id=chat.sender["id"])

            Chat = apps.get_model("django_welkin.Chat")
            _, created = Chat.objects.get_or_create(
                id=Chat.parse_uuid(chat.externalId),
                message=chat.message,
                created_at=parse_datetime(chat.createdAt),
                patient=self,
                user=user,
            )
            if not created:
                break

    def save(self, *args, **kwargs):
        if not self.pk:
            patient = _Welkin().Patient(
                firstName=self.first_name, lastName=self.last_name
            )
            patient.create()

            self.id = patient.id

        super().save(*args, **kwargs)
