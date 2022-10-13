from datetime import datetime, timedelta, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.dateparse import parse_datetime
from welkin.exceptions import WelkinHTTPError
from welkin.models.formation import FormationDataType

from ...models import CDT, CalendarEvent, CDTRecord, Patient, User
from ...models.base import _Welkin


# pylint: disable=no-member
class Command(BaseCommand):
    help = "Refresh Welkin data in the DB"  # noqa: A003

    def handle(self, *args, **options):
        client = _Welkin()

        self.sync_patients(client)
        self.sync_users(client)
        self.sync_calendar_events(client)
        self.sync_chat(client)
        self.sync_cdts(client)
        self.sync_cdt_records(client)

    def sync_patients(self, client):
        self.stdout.write("Refreshing patients")
        for patient in client.Patients().get(paginate=True):
            Patient.objects.update_or_create(
                id=patient.id,
                defaults={
                    "first_name": patient.firstName,
                    "last_name": patient.lastName,
                },
            )

    def sync_users(self, client):
        self.stdout.write("Refreshing users")
        for user in client.Users().get(paginate=True):
            for role in user.roles:
                if role["instanceName"] != client.instance:
                    continue

                if role["permissionName"] in ["health-coach", "physician"]:
                    User.objects.update_or_create(
                        id=user.id,
                        defaults={
                            "first_name": user.firstName,
                            "last_name": user.lastName,
                        },
                    )
                    break

    def sync_calendar_events(self, client):
        start = datetime(2022, 3, 1, tzinfo=timezone.utc)
        end = datetime.now(tz=timezone.utc) + timedelta(days=365)

        self.stdout.write("Refreshing calendar events")

        events = client.CalendarEvents().get(
            from_date=start, to_date=end, include_cancelled=True, paginate=True
        )
        for event in events:
            user = None
            patient = None
            for p in event.participants:
                p_id = p["participantId"]
                first_name = p["firstName"]
                last_name = p["lastName"]
                role = p["participantRole"]

                # Unsure if there are more roles than psm or patient
                if role == "psm":
                    user, _ = User.objects.update_or_create(
                        id=p_id,
                        defaults={"first_name": first_name, "last_name": last_name},
                    )
                elif role == "patient":
                    patient, _ = Patient.objects.update_or_create(
                        id=p_id,
                        defaults={"first_name": first_name, "last_name": last_name},
                    )
            try:
                CalendarEvent.objects.update_or_create(
                    id=event.id,
                    defaults={
                        "title": event.eventTitle,
                        "start_time": parse_datetime(event.startDateTime),
                        "status": event.eventStatus,
                        "patient": patient,
                        "user": user,
                    },
                )
            except IntegrityError:
                self.stdout.write(f"Skip {event}, likely no associated patient.")

    def sync_chat(self, client):
        self.stdout.write("Refreshing chat")
        for patient in Patient.objects.all():
            patient: Patient
            patient.sync_chat()

    def sync_cdts(self, client):
        self.stdout.write("Refreshing CDTs")
        for cdt in client.Formations().get(FormationDataType.CDTS, paginate=True):
            if cdt.pop("internal"):
                self.stdout.write(f"Skip internal CDT {cdt.name}")

            cdt.contains_phi = cdt.pop("_containsPHI")
            cdt.title = cdt.title or ""
            cdt.label = cdt.label or ""

            _, created = CDT.objects.update_or_create(id=cdt.id, defaults=cdt)
            self.stdout.write(
                f'{"Created" if created else "Updated"} CDT {cdt["name"]}'
            )

    def sync_cdt_records(self, client):
        self.stdout.write("Refreshing CDTs")
        for patient in Patient.objects.all():
            for cdt in CDT.objects.all():
                cdt_records = (
                    client.Patient(id=patient.id)
                    .CDTs()
                    .get(cdt_name=cdt.name, paginate=True)
                )

                try:
                    for record in cdt_records:
                        CDTRecord.objects.update_or_create(
                            id=record["id"],
                            defaults={
                                "version": record["version"],
                                "body": record["jsonBody"],
                                "cdt": cdt,
                                "patient": patient,
                            },
                        )
                except WelkinHTTPError as e:
                    messages = ", ".join(i["message"] for i in e.response.json())
                    self.stdout.write(
                        f"Skip CDT records for patient {patient.id}: {messages}"
                    )

                    if "Patient not found" in messages:
                        try:
                            patient.user
                        except ObjectDoesNotExist as e:
                            self.stdout.write(
                                f"Removing patient {patient.id}: {messages}, and {e} "
                            )
                            patient.delete()

                        break
