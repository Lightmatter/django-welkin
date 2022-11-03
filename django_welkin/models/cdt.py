from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel
from .patient import Patient


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

    def sync(self):
        raise NotImplementedError(
            "This model is installed using the 'welkin_sync_models' admin command."
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

    @classmethod
    def from_webhook(cls, payload):
        cls = super().from_webhook(payload)
        cls.cdt = CDT.objects.get(name=payload["sourceName"], instance=cls.instance)
        cls.patient = Patient.objects.get(
            id=payload["patientId"], instance=cls.instance
        )

        return cls

    def sync(self):
        patient = self.client.Patient(id=self.patient.id)
        cdt_record = patient.CDT(cdtName=self.cdt.name, id=self.id).get()

        self.version = cdt_record["version"]
        self.body = cdt_record["jsonBody"]
        self.cdt = CDT.objects.get(name=cdt_record["cdtName"])
        self.patient = Patient.objects.get(id=cdt_record["patientId"])

        self.save()
