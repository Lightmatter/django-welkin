"""Django bootstrap

This file sets up and configures Django. It's used by scripts that need to execute as if
running in a Django server.

https://realpython.com/installable-django-app/#bootstrapping-django-outside-of-a-project
"""
from pathlib import Path

import django
from django.conf import settings

BASE_DIR = Path(__file__).parent.parent / "django_welkin"


def boot_django():
    settings.configure(
        BASE_DIR=BASE_DIR,
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        },
        INSTALLED_APPS=("django_welkin", "solo"),
        TIME_ZONE="UTC",
    )
    django.setup()
