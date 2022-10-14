from http import HTTPStatus

import pytest
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django_welkin.models import Chat, WebhookMessage
from django_welkin.models.base import _Welkin


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
        _Welkin().auth.token = {"token": "foo"}

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
