from http import HTTPStatus

import pytest
from django.urls import reverse
from django.utils import timezone
from django_welkin.models import Chat, WebhookMessage
from model_bakery import baker


@pytest.mark.django_db
def test_bad_method(client):
    response = client.get(reverse("chat"))

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_missing_data(client):
    payload = {}
    start = timezone.now()
    response = client.post(
        reverse("chat"),
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
        "patientId": "17450e44-c2c8-46c4-9486-0d9bfa16d3aa",
        "tenantName": "lightmatter",
        "instanceName": "sandbox",
        "message": "Give me a message",
    }
    baker.make(
        "django_welkin.Patient", id=payload["patientId"], instance=api_key.instance
    )
    baker.make(
        "django_welkin.User",
        id="d2b3d940-01ec-44f3-a2cd-b5298823ec9f",
        instance=api_key.instance,
    )

    response = client.post(
        reverse("chat"),
        content_type="application/json",
        data=payload,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == "Message stored."

    chat = Chat.objects.get(message=payload["message"])
    assert chat.message == payload["message"]
    assert str(chat.patient_id) == payload["patientId"]
