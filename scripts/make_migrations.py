#!/usr/bin/env python
"""Make migrations for django-welkin"""
from django.core.management import call_command

from boot_django import boot_django


def main():
    boot_django()
    call_command("makemigrations", "django_welkin")


if __name__ == "__main__":
    main()
