from django.apps import AppConfig


class WelkinConfig(AppConfig):
    name = "welkin"
    verbose_name = "Welkin"


class PatientConfig(AppConfig):
    name = "patient"
    verbose_name = "Patient"


class ProviderConfig(AppConfig):
    name = "provider"
    verbose_name = "Provider"
