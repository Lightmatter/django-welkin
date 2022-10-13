from http import HTTPStatus

import pytest
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django_welkin.models import (
    CalendarEvent,
    CDTRecord,
    Chat,
    Configuration,
    Patient,
    WebhookMessage,
    Welkin,
)


def check_model():
    pass


# Create your tests here.
class PatientTest(TestCase):
    pass


class WebhookTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.url = self.url = reverse("welkin")

        # baker.make_recipe("django_welkin.configuration")

        # Ensure token db is created
        Welkin().auth.token = {"token": "foo"}

    def test_bad_method(self):
        response = self.client.get(self.url)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_welkin_test(self):
        response = self.client.post(
            self.url,
            content_type="application/json",
            data=Configuration.get_test_payload(),
        )

        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Test payload received"

    def test_missing_data(self):
        payloads = [
            {"eventEntity": "CALENDAR"},
            {"sourceId": "notarealid"},
        ]

        for payload in payloads:
            start = timezone.now()
            response = self.client.post(
                self.url,
                content_type="application/json",
                data=payload,
            )

            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.content.decode().startswith("Payload missing")

            wm = WebhookMessage.objects.all().last()
            assert wm.received_at >= start
            assert wm.payload == payload

    @pytest.mark.vcr()
    def test_calendar_event(self):
        payload = {
            "sourceId": "834e4ab3-3e82-4a74-807c-bf0bb2b1308a",
            "patientId": "17450e44-c2c8-46c4-9486-0d9bfa16d3aa",
            "sourceName": "ENCOUNTER",
            "tenantName": "lightmatter",
            "eventEntity": "CALENDAR",
            "eventSubtype": "CALENDAR_EVENT_UPDATED",
            "instanceName": "sandbox",
        }
        response = self.client.post(
            self.url,
            content_type="application/json",
            data=payload,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Message stored."

        event = CalendarEvent.objects.get(id=payload["sourceId"])
        assert str(event.id) == payload["sourceId"]
        assert str(event.patient.id) == payload["patientId"]
        assert str(event.user) == "Sam Morgan"

    @pytest.mark.vcr()
    def test_cdt_record(self):
        payload = {
            "sourceId": "9be39258-9a81-4dc4-953a-630e4e5fc77b",
            "patientId": "89ec0634-50f3-40b1-981d-22ab39dd3037",
            "sourceName": "insurance",
            "tenantName": "lightmatter",
            "eventEntity": "CDT",
            "eventSubtype": "CDT_CREATED",
            "instanceName": "sandbox",
        }
        # baker.make("welkin.CDT", name=payload["sourceName"])
        # baker.make("welkin.Patient", id=payload["patientId"])

        response = self.client.post(
            self.url,
            content_type="application/json",
            data=payload,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Message stored."

        cdt_record = CDTRecord.objects.get(id=payload["sourceId"])
        assert str(cdt_record.id) == payload["sourceId"]
        assert str(cdt_record.patient.id) == payload["patientId"]
        assert cdt_record.version == 27

    @pytest.mark.vcr()
    def test_patient(self):
        payload = {
            "sourceId": "49ec74c2-7368-4932-a98f-e5298622c191",
            "patientId": "49ec74c2-7368-4932-a98f-e5298622c191",
            "sourceName": "Webhook Patient",
            "tenantName": "lightmatter",
            "eventEntity": "PATIENT",
            "eventSubtype": "PATIENT_CREATED",
            "instanceName": "sandbox",
        }

        response = self.client.post(
            self.url,
            content_type="application/json",
            data=payload,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Message stored."

        patient = Patient.objects.get(id=payload["sourceId"])
        assert patient.first_name == "Webhook"
        assert patient.last_name == "Patient"


class ChatWebhookTests(TestCase):
    def setUp(self):
        self.client = Client(  # noqa: S106
            enforce_csrf_checks=True,
            X_WEBHOOK_API_KEY="test_key",
            X_WEBHOOK_API_secret="test_secret",
        )
        self.url = self.url = reverse("chat")

        # baker.make_recipe("django_welkin.configuration")

        # Ensure token db is created
        Welkin().auth.token = {"token": "foo"}

    def test_bad_method(self):
        response = self.client.get(self.url)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_missing_data(self):
        payload = {}
        start = timezone.now()
        response = self.client.post(
            self.url,
            content_type="application/json",
            data=payload,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode().startswith("Payload missing")

        wm = WebhookMessage.objects.all().last()
        assert wm.received_at >= start
        assert wm.payload == payload

    @pytest.mark.vcr()
    def test_chat(self):
        payload = {
            "patientId": "17450e44-c2c8-46c4-9486-0d9bfa16d3aa",
            "tenantName": "lightmatter",
            "instanceName": "sandbox",
            "message": "Give me a message",
        }
        # baker.make("welkin.Patient", id=payload["patientId"])

        response = self.client.post(
            self.url,
            content_type="application/json",
            data=payload,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "Message stored."

        chat = Chat.objects.get(message=payload["message"])
        assert chat.message == payload["message"]
        assert str(chat.patient.id) == payload["patientId"]
