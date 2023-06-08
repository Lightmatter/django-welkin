from django.apps import AppConfig


class DjangoWelkinConfig(AppConfig):
    name = "django_welkin"
    verbose_name = "Django Welkin"

    def ready(self):
        try:
            import solo
        except ImportError:
            raise ValueError("Missing 'solo' from 'INSTALLED_APPS'")
