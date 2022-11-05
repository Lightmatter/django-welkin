import json
import os
import uuid
from pathlib import Path
from typing import Generator

import pytest
from environ import Env
from model_bakery import baker
from playwright.sync_api import Playwright
from vcr import VCR

env = Env()
env.read_env(Path(__file__).parent.parent / ".env")


@pytest.fixture(autouse=True)
def api_key():
    api_key = baker.make_recipe("tests.api_key")

    # Ensure token db is created
    api_key._client.auth.token = {"token": "foo"}

    yield api_key


@pytest.fixture
def payload(api_key):
    return {
        "sourceId": "SOURCE_ID",
        "eventSubtype": "EVENT_SUBTYPE",
        "tenantName": api_key.instance.tenant.name,
        "instanceName": api_key.instance.name,
        "patientId": "PATIENT_ID",
        "eventEntity": "EVENT_ENTITY",
        "sourceName": "SOURCE_NAME",
        "url": "URL",
    }


@pytest.fixture(scope="session")
def playwright(playwright: Playwright) -> Generator[Playwright, None, None]:
    """Override of playwright fixture so we can set up for use with Django.

    Background: https://github.com/microsoft/playwright-python/issues/439
    """
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    yield playwright


def redact(field_name, extra=""):
    parts = [field_name, extra, str(uuid.uuid4())]

    return "_".join(i for i in parts if i)


HEADER_BLACKLIST = [("Authorization", redact("API_TOKEN"))]
POST_DATA_BLACKLIST = [("secret", redact("API_TOKEN"))]
REQUEST_BLACKLIST = ["secret"]
RESPONSE_BLACKLIST = [
    "token",
    "createdBy",
    "createdByName",
    "updatedBy",
    "updatedByName",
]
WELKIN_SECRETS = {
    "tenant": env("WELKIN_TENANT", default="tenant"),
    "instance": env("WELKIN_INSTANCE", default="instance"),
    "api_client": env("WELKIN_API_CLIENT", default="api_client"),
    "secret_key": env("WELKIN_SECRET", default="secret_key"),
}


@pytest.fixture(scope="module")
def vcr(vcr: VCR):
    vcr.filter_headers = HEADER_BLACKLIST
    vcr.filter_post_data_parameters = POST_DATA_BLACKLIST
    vcr.before_record_request = scrub_request(WELKIN_SECRETS)
    vcr.before_record_response = scrub_response(RESPONSE_BLACKLIST)

    return vcr


def scrub_request(blacklist, replacement="REDACTED"):
    def before_record_request(request):
        uri_comps = request.uri.split("/")
        for k, v in blacklist.items():
            try:
                ind = uri_comps.index(v)
                uri_comps[ind] = f"{k}_{replacement}"
            except ValueError:
                continue

        request.uri = "/".join(uri_comps)
        return request

    return before_record_request


def scrub_response(blacklist, replacement="REDACTED"):
    def before_record_response(response):
        response["body"]["string"] = filter_body(
            response["body"]["string"], blacklist, replacement
        )

        return response

    return before_record_response


def filter_body(body, blacklist, replacement):
    if not body:
        return body
    object_hook = body_hook(blacklist, replacement)
    body_json = json.loads(body.decode(), object_hook=object_hook)

    return json.dumps(body_json).encode()


def body_hook(blacklist, replacement):
    def hook(dct):
        for k in dct:
            if k in blacklist:
                dct[k] = redact(k, replacement)

        return dct

    return hook
