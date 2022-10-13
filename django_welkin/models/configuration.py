from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


class Configuration(SingletonModel):
    tenant = models.CharField(max_length=255, help_text="Welkin organization name.")
    instance = models.CharField(
        max_length=255, help_text="The environment inside a Welkin organization."
    )
    api_client = models.CharField(
        max_length=255, help_text="Welkin API client name.", verbose_name="API client"
    )
    secret_key = models.CharField(
        max_length=255, help_text="Welkin API client secret key."
    )

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
