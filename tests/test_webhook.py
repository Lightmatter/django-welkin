from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone
from django_welkin.models import (
    APIKey,
    CalendarEvent,
    CDTRecord,
    Patient,
    WebhookMessage,
)
from model_bakery import baker


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

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "Test payload received"


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

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.content.decode().startswith("Payload missing")

        wm = WebhookMessage.objects.all().last()
        assert wm.received_at >= start
        assert wm.payload == payload


@pytest.mark.vcr
@pytest.mark.django_db
def test_calendar_event(client):
    payload = {
        "sourceId": "2e8d4058-ce62-4b30-8b71-07df4eefbf55",
        "patientId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
        "sourceName": "ENCOUNTER",
        "tenantName": "lightmatter",
        "eventEntity": "CALENDAR",
        "eventSubtype": "CALENDAR_EVENT_UPDATED",
        "instanceName": "sandbox",
    }
    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "Message stored."

    event = CalendarEvent.objects.get(id=payload["sourceId"])
    assert str(event.id) == payload["sourceId"]
    assert str(event.patient.id) == payload["patientId"]
    assert str(event.user) == "Sam Morgan"


@pytest.mark.vcr
@pytest.mark.django_db
def test_cdt_record(client, api_key):
    payload = {
        "sourceId": "9be39258-9a81-4dc4-953a-630e4e5fc77b",
        "patientId": "89ec0634-50f3-40b1-981d-22ab39dd3037",
        "sourceName": "insurance",
        "tenantName": "lightmatter",
        "eventEntity": "CDT",
        "eventSubtype": "CDT_CREATED",
        "instanceName": "sandbox",
    }
    baker.make(
        "django_welkin.CDT", name=payload["sourceName"], instance=api_key.instance
    )
    baker.make(
        "django_welkin.Patient", id=payload["patientId"], instance=api_key.instance
    )

    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "Message stored."

    cdt_record = CDTRecord.objects.get(id=payload["sourceId"])
    assert str(cdt_record.id) == payload["sourceId"]
    assert str(cdt_record.patient.id) == payload["patientId"]
    assert cdt_record.version == 27


@pytest.mark.vcr
@pytest.mark.django_db
def test_patient(client):
    payload = {
        "sourceId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
        "patientId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
        "sourceName": "Webhook Patient",
        "tenantName": "lightmatter",
        "eventEntity": "PATIENT",
        "eventSubtype": "PATIENT_CREATED",
        "instanceName": "sandbox",
    }

    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "Message stored."

    patient = Patient.objects.get(id=payload["sourceId"])
    assert patient.first_name == "Webhook"
    assert patient.last_name == "Patient"
