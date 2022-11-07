from django.conf import settings
from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel



class Patient(WelkinModel):
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)
    middle_name = models.CharField(_("middle name"), max_length=255, null=True)
    birth_date = models.DateField(null=True)
    gender = models.CharField(_("gender"), max_length=255, null=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name = _("patient")
        verbose_name_plural = _("patients")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def sync(self):
        patient = self.client.Patient(id=self.id).get()

        self.first_name = patient.firstName
        self.last_name = patient.lastName
        self.middle_name = patient.middleName
        self.birth_date = parse_datetime(patient.birthDate)
        self.gender = patient.gender

        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            patient = self.client.Patient(
                firstName=self.first_name, lastName=self.last_name
            )
            patient.create()

            self.id = patient.id

        super().save(*args, **kwargs)
