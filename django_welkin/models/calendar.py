from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel
from .patient import Patient
from .user import User


class CalendarEvent(WelkinModel):
    title = models.CharField(_("title"), max_length=255, blank=True)
    start_time = models.DateTimeField(null=True)
    status = models.CharField(_("status"), max_length=255, blank=True)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("calendar event")
        verbose_name_plural = _("calendar events")

    def __str__(self):
        return self.id

    def sync(self):
        event = self.client.CalendarEvent(id=self.id).get()

        self.title = event.eventTitle
        self.start_time = parse_datetime(event.startDateTime)
        self.status = event.eventStatus

        for p in event.participants:
            p_id = p["participantId"]
            role = p["participantRole"]

            # Unsure if there are more roles than psm or patient
            if role == "psm":
                try:
                    self.user = User.objects.get(id=p_id, instance=self.instance)
                except User.DoesNotExist:
                    self.user = User(id=p_id, instance=self.instance)
                    self.user.sync()
            elif role == "patient":
                try:
                    self.patient = Patient.objects.get(id=p_id, instance=self.instance)
                except Patient.DoesNotExist:
                    self.patient = Patient(id=p_id, instance=self.instance)
                    self.patient.sync()

        self.save()
