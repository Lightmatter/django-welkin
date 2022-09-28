# pylint: disable=no-member
import uuid

from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel
from welkin import Client


class Welkin(Client):
    def __init__(self, *args, **kwargs):
        config = Configuration.objects.get()
        kwargs["tenant"] = config.tenant
        kwargs["instance"] = config.instance
        kwargs["api_client"] = config.api_client
        kwargs["secret_key"] = config.secret_key

        super().__init__(*args, **kwargs)


class Configuration(SingletonModel):
    tenant = models.CharField(max_length=255, help_text="Welkin organization name.")
    instance = models.CharField(
        max_length=255, help_text="The environment inside a Welkin organization."
    )
    api_client = models.CharField(
        max_length=255, help_text="Welkin API client name.", verbose_name="API client"
    )
    secret_key = models.CharField(max_length=255, help_text="Welkin API client secret key.")

    def __str__(self):
        return "Welkin configuration"

    class Meta:
        verbose_name = _("configuration")

    @classmethod
    def get_test_payload(cls):
        config = cls.objects.get()
        return {
            "sourceId": "SOURCE_ID",
            "eventSubtype": "EVENT_SUBTYPE",
            "tenantName": config.tenant,
            "instanceName": config.instance,
            "patientId": "PATIENT_ID",
            "eventEntity": "EVENT_ENTITY",
            "sourceName": "SOURCE_NAME",
            "url": "URL",
        }


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


class WelkinModel(models.Model):

    id = models.UUIDField(primary_key=True, editable=False)  # noqa: A003

    class Meta:
        abstract = True

    def sync_from_welkin(self):
        raise NotImplementedError("This method must be implemented in concrete models.")


class Patient(WelkinModel):
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)

    class Meta:
        verbose_name = _("patient")
        verbose_name_plural = _("patients")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def sync_from_welkin(self):
        patient = Welkin().Patient(id=self.id).get()

        self.first_name = patient.firstName
        self.last_name = patient.lastName

        self.save()

    def sync_chat(self):
        for chat in Welkin().Patient(id=self.id).Chats().get(paginate=True):
            provider = None
            if chat.sender["clientType"] == "USER":
                provider, _ = Provider.objects.get_or_create(id=chat.sender["id"])

            _, created = Chat.objects.get_or_create(
                id=Chat.parse_uuid(chat.externalId),
                message=chat.message,
                created_at=parse_datetime(chat.createdAt),
                patient=self,
                provider=provider,
            )
            if not created:
                break

    def save(self, *args, **kwargs):
        if not self.pk:
            patient = Welkin().Patient(firstName=self.first_name, lastName=self.last_name)
            patient.create()

            self.id = patient.id

        super().save(*args, **kwargs)


class CDT(WelkinModel):
    class CDTType(models.TextChoices):
        SINGLE_RECORD = "SINGLE_RECORD"
        MULTI_RECORD = "MULTI_RECORD"

    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    label = models.CharField(max_length=255, blank=True)
    version = models.IntegerField()
    readable = models.BooleanField()
    updatable = models.BooleanField()
    type = models.CharField(max_length=13, choices=CDTType.choices)  # noqa: A003
    relation = models.CharField(max_length=255)
    fields = models.JSONField()
    contains_phi = models.BooleanField()

    class Meta:
        verbose_name = _("CDT")
        verbose_name_plural = _("CDTs")

    def __str__(self):
        return self.name

    def sync_from_welkin(self):
        raise NotImplementedError(
            "This model is installed using the 'welkin_load_configuration <filename>' "
            "admin command."
        )


class CDTRecord(WelkinModel):
    version = models.IntegerField(null=True)
    body = models.JSONField(null=True)

    cdt = models.ForeignKey(CDT, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("CDT record")
        verbose_name_plural = _("CDT records")

    def __str__(self):
        return f"{self.cdt.name} record"

    def sync_from_welkin(self):
        cdt_record = (
            Welkin().Patient(id=self.patient.id).CDT(cdtName=self.cdt.name, id=self.id)
        ).get()

        self.version = cdt_record["version"]
        self.body = cdt_record["jsonBody"]
        self.cdt = CDT.objects.get(name=cdt_record["cdtName"])
        self.patient = Patient.objects.get(id=cdt_record["patientId"])

        self.save()


class Provider(WelkinModel):
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)

    class Meta:
        verbose_name = _("provider")
        verbose_name_plural = _("providers")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def sync_from_welkin(self):
        user = Welkin().User(id=self.id).get()

        self.first_name = user.firstName
        self.last_name = user.lastName

        self.save()


class CalendarEvent(WelkinModel):
    title = models.CharField(_("title"), max_length=255, blank=True)
    start_time = models.DateTimeField(null=True)
    status = models.CharField(_("status"), max_length=255, blank=True)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("calendar event")
        verbose_name_plural = _("calendar events")

    def __str__(self):
        return self.id

    def sync_from_welkin(self):
        event = Welkin().CalendarEvent(id=self.id).get()

        self.title = event.eventTitle
        self.start_time = parse_datetime(event.startDateTime)
        self.status = event.eventStatus

        for p in event.participants:
            p_id = p["participantId"]
            first_name = p["firstName"]
            last_name = p["lastName"]
            role = p["participantRole"]

            # Unsure if there are more roles than psm or patient
            if role == "psm":
                self.provider, _ = Provider.objects.update_or_create(
                    id=p_id, first_name=first_name, last_name=last_name
                )
            elif role == "patient":
                self.patient, _ = Patient.objects.update_or_create(
                    id=p_id, first_name=first_name, last_name=last_name
                )

        self.save()


class Chat(WelkinModel):
    message = models.TextField()
    created_at = models.DateTimeField(help_text="When the message was created.")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("chat")
        verbose_name_plural = _("chats")

    def __str__(self):
        return self.message

    @property
    def sender(self):
        return self.provider if self.provider else self.patient

    @staticmethod
    def parse_uuid(external_id):
        return uuid.UUID(external_id[2:])

    def sync_from_welkin(self):
        raise NotImplementedError("Chat is synced through the Patient model.")

    def save(self, *args, **kwargs):
        if not self.pk:
            chat = Welkin().Patient(id=self.patient.id).Chat(message=self.message)
            chat.create()

            self.id = Chat.parse_uuid(chat.externalId)
            self.message = chat.message
            self.created_at = parse_datetime(chat.createdAt)

        super().save(*args, **kwargs)
