from django.contrib import admin

from .forms import APIKeyForm
from .models import (
    CDT,
    APIKey,
    CalendarEvent,
    CDTRecord,
    Instance,
    Patient,
    Tenant,
    User,
    WebhookMessage,
)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    form = APIKeyForm
    autocomplete_fields = [
        "instance",
    ]


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    autocomplete_fields = [
        "tenant",
    ]
    search_fields = [
        "name",
        "tenant",
    ]


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
    ]


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
