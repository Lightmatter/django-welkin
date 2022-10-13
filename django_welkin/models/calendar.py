from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel, _Welkin
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

    def sync_from_welkin(self):
        event = _Welkin().CalendarEvent(id=self.id).get()

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
                self.user, _ = User.objects.update_or_create(
                    id=p_id, first_name=first_name, last_name=last_name
                )
            elif role == "patient":
                self.patient, _ = Patient.objects.update_or_create(
                    id=p_id, first_name=first_name, last_name=last_name
                )

        self.save()
