import json
from enum import Enum

from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import CalendarEvent, CDTRecord, Chat, Patient, WebhookMessage


class EventEntity(Enum):
    CALENDAR = CalendarEvent
    CDT = CDTRecord
    PATIENT = Patient
    CHAT = Chat


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
    if "message" in payload:
        payload["eventEntity"] = "CHAT"

    entity = payload["eventEntity"]

    if entity == "EVENT_ENTITY":
        return

    try:
        model = EventEntity[entity].value
    except KeyError:
        raise NotImplementedError(f"{entity} is not a supported entity.")

    obj = model.from_webhook(payload)
    obj.sync()
