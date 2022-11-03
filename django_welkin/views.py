import json
from enum import Enum

from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import CDT, CalendarEvent, CDTRecord, Instance, Patient, WebhookMessage


class EventEntity(Enum):
    CALENDAR = CalendarEvent
    CDT = CDTRecord
    PATIENT = Patient


@csrf_exempt
@require_POST
@non_atomic_requests
def webhook(request: HttpRequest) -> HttpResponse:
    payload = json.loads(request.body)
    WebhookMessage.objects.create(payload=payload)

    try:
        process_webhook_payload(payload)
    except KeyError as e:
        return HttpResponseBadRequest(f"Payload missing {e}")
    except NotImplementedError as e:
        return HttpResponseBadRequest(e)

    if payload["eventEntity"] == "EVENT_ENTITY":
        # IDEA: Do some actual test interactions when we receive a test payload.
        return HttpResponse("Test payload received")

    return HttpResponse("Message stored.")


@atomic
def process_webhook_payload(payload: dict) -> None:
    entity = payload["eventEntity"]

    if entity == "EVENT_ENTITY":
        return

    try:
        model = EventEntity[entity].value
    except KeyError:
        raise NotImplementedError(f"{entity} is not a supported entity.")

    obj = model.from_webhook(payload)
    obj.sync()


@csrf_exempt
@require_POST
@non_atomic_requests
def chat(request: HttpRequest) -> HttpResponse:
    payload = json.loads(request.body)
    WebhookMessage.objects.create(payload=payload)

    try:
        process_chat_payload(payload)
    except KeyError as e:
        return HttpResponseBadRequest(f"Payload missing {e}")

    return HttpResponse("Message stored.")


@atomic
def process_chat_payload(payload: dict) -> None:
    try:
        patient = Patient.objects.get(
            id=payload["patientId"], instance__name=payload["instanceName"]
        )
    except Patient.DoesNotExist:
        patient = Patient.from_webhook(payload)
        patient.sync()

    patient.sync_chat()
