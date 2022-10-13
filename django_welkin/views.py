import json
from enum import Enum

from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import CDT, CalendarEvent, CDTRecord, Configuration, Patient, WebhookMessage


class EventEntity(Enum):
    CALENDAR = CalendarEvent
    CDT = CDTRecord
    PATIENT = Patient


@csrf_exempt
@require_POST
@non_atomic_requests
def webhook(request: HttpRequest) -> HttpResponse:
    payload = json.loads(request.body)

    if payload == Configuration.get_test_payload():
        return HttpResponse("Test payload received")

    WebhookMessage.objects.create(payload=payload)

    try:
        process_webhook_payload(payload)
    except KeyError as e:
        return HttpResponseBadRequest(f"Payload missing {e}")
    except NotImplementedError as e:
        return HttpResponseBadRequest(e)

    return HttpResponse("Message stored.")


@atomic
def process_webhook_payload(payload: dict) -> None:
    entity = payload["eventEntity"]
    try:
        model = EventEntity[entity].value
    except KeyError:
        raise NotImplementedError(f"{entity} is not a supported entity.")

    obj = model(id=payload["sourceId"])

    if isinstance(obj, CDTRecord):
        # NOTE: I dislike having model-specific logic here. There's likely a better way.
        obj.cdt = CDT.objects.get(name=payload["sourceName"])
        obj.patient = Patient.objects.get(id=payload["patientId"])

    obj.sync_from_welkin()


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
    patient: Patient
    patient, created = Patient.objects.get_or_create(id=payload["patientId"])

    if created:
        patient.sync_from_welkin()

    patient.sync_chat()
