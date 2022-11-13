from django.conf import settings
from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel


class PatientManager(models.Manager):
    def create(self, **kwargs):
        """
        Create a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True, using=self.db)
        return obj


class Patient(WelkinModel):
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)
    middle_name = models.CharField(
        _("middle name"), max_length=255, default="", blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(_("gender"), max_length=255, default="", blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name = _("patient")
        verbose_name_plural = _("patients")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Sync should all be here I think. Normal ORM actions on CRUD plus:
        # - Create: Create a new patient on Welkin
        # - Read: Do nothing, use local record for reading
        # - Update: Push updates to this model up to Welkin
        # - Delete: Delete patient from Welkin (if possible), otherwise some sort of flag on
        #           Welkin patient?

        if not self.pk:
            patient = self.client.Patient(
                firstName=self.first_name, lastName=self.last_name
            )
            patient.create()

            self.id = patient.id

        super().save(*args, **kwargs)

    def sync(self):
        if not self.pk:
            patient = self.client.Patient(
                firstName=self.first_name, lastName=self.last_name
            )
            patient.create()

            self.id = patient.id
        else:
            patient = self.client.Patient(id=self.id).get()

        self.first_name = patient.firstName
        self.last_name = patient.lastName
        self.middle_name = patient.middleName or ""
        self.gender = patient.gender

        if patient.birthDate:
            self.birth_date = parse_datetime(patient.birthDate)

        self.save()
