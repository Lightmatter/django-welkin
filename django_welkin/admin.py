from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .forms import ConfigurationForm
from .models import (
    CDT,
    CalendarEvent,
    CDTRecord,
    Configuration,
    Patient,
    User,
    WebhookMessage,
)


@admin.register(Configuration)
class ConfigurationAdmin(SingletonModelAdmin):
    form = ConfigurationForm


@admin.register(WebhookMessage)
class WebhookMessageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "received_at")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(CDT)
class CDTAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "title",
        "label",
        "version",
        "readable",
        "updatable",
        "type",
        "relation",
        "field_count",
    )

    @admin.display(description="Fields")
    def field_count(self, obj):
        return len(obj.fields)


@admin.register(CDTRecord)
class CDTRecordAdmin(admin.ModelAdmin):
    list_display = ("cdt", "version", "patient")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    pass
