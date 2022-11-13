from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from django_welkin.models import CalendarEvent, CDTRecord, Chat, Patient, WebhookMessage


def response_ok(response):
    assert response.content.decode() == "Message stored."
    assert response.status_code == HTTPStatus.OK

    return True


@pytest.mark.django_db
def test_bad_method(client):
    response = client.get(reverse("welkin"))

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_dummy_payload(client, payload):
    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response.content.decode() == "Test payload received"
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_missing_data(client):
    payloads = [
        {"eventEntity": "CALENDAR"},
        {"sourceId": "notarealid"},
    ]

    for payload in payloads:
        start = timezone.now()
        response = client.post(
            reverse("welkin"),
            content_type="application/json",
            data=payload,
        )

        assert "Payload missing" in response.content.decode()
        assert response.status_code == HTTPStatus.BAD_REQUEST

        wm = WebhookMessage.objects.all().last()
        assert wm.received_at >= start
        assert wm.payload == payload


@pytest.mark.vcr
@pytest.mark.django_db
def test_calendar_event(client, api_key, payload):
    payload.update(
        {
            "sourceId": "2e8d4058-ce62-4b30-8b71-07df4eefbf55",
            "patientId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
            "sourceName": "ENCOUNTER",
            "eventEntity": "CALENDAR",
            "eventSubtype": "CALENDAR_EVENT_UPDATED",
        }
    )
    baker.make(
        "django_welkin.Patient",
        id=payload["patientId"],
        instance_id=api_key.instance_id,
    )
    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response_ok(response)

    event = CalendarEvent.objects.get(id=payload["sourceId"])
    assert str(event.id) == payload["sourceId"]
    assert str(event.patient_id) == payload["patientId"]
    assert str(event.user) == "Sam Morgan"


@pytest.mark.vcr
@pytest.mark.django_db
def test_cdt_record(client, api_key, payload):
    payload.update(
        {
            "sourceId": "31fabd93-2153-4518-b2ce-6fdb1892cf42",
            "eventSubtype": "CDT_UPDATED",
            "patientId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
            "eventEntity": "CDT",
            "sourceName": "_asm-appointment-checkin",
        }
    )
    baker.make(
        "django_welkin.CDT", name=payload["sourceName"], instance_id=api_key.instance_id
    )
    baker.make(
        "django_welkin.Patient",
        id=payload["patientId"],
        instance_id=api_key.instance_id,
    )

    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response_ok(response)

    cdt_record = CDTRecord.objects.get(id=payload["sourceId"])
    assert str(cdt_record.id) == payload["sourceId"]
    assert str(cdt_record.patient_id) == payload["patientId"]
    assert cdt_record.version == 11


@pytest.mark.vcr
@pytest.mark.django_db
def test_patient(client, payload):
    payload.update(
        {
            "sourceId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
            "patientId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
            "sourceName": "Webhook Patient",
            "eventEntity": "PATIENT",
            "eventSubtype": "PATIENT_CREATED",
        }
    )

    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response_ok(response)

    patient = Patient.objects.get(id=payload["sourceId"])
    assert patient.first_name == "Webhook"
    assert patient.last_name == "Patient"


@pytest.mark.vcr
@pytest.mark.django_db
def test_chat(client):
    payload = {
        "patientId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
        "tenantName": "lightmatter",
        "instanceName": "sandbox",
        "message": "Energy equals mass times the speed of light squared.",
    }

    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response_ok(response)

    chat = Chat.objects.get(message=payload["message"])
    assert chat.message == payload["message"]
    assert str(chat.patient_id) == payload["patientId"]
