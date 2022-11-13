from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from django_welkin.models import Chat, WebhookMessage


@pytest.mark.django_db
def test_bad_method(client):
    response = client.get(reverse("welkin"))

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_missing_data(client):
    payload = {}
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
def test_chat(client, api_key):
    payload = {
        "patientId": "fcf051b7-1d8e-4912-b402-e2c436e4c2cc",
        "tenantName": "lightmatter",
        "instanceName": "sandbox",
        "message": "Energy equals mass times the speed of light squared.",
    }
    baker.make(
        "django_welkin.Patient",
        id=payload["patientId"],
        instance_id=api_key.instance_id,
    )
    baker.make(
        "django_welkin.User",
        id="d2b3d940-01ec-44f3-a2cd-b5298823ec9f",
        instance_id=api_key.instance_id,
    )

    response = client.post(
        reverse("welkin"),
        content_type="application/json",
        data=payload,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "Message stored."

    chat = Chat.objects.get(message=payload["message"])
    assert chat.message == payload["message"]
    assert str(chat.patient_id) == payload["patientId"]
