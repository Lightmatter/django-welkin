from django.db import models
from welkin import Client

from .configuration import Configuration


class _Welkin(Client):
    def __init__(self, *args, **kwargs):
        config = Configuration.objects.get()
        kwargs["tenant"] = config.tenant
        kwargs["instance"] = config.instance
        kwargs["api_client"] = config.api_client
        kwargs["secret_key"] = config.secret_key

        super().__init__(*args, **kwargs)


class WelkinModel(models.Model):

    id = models.UUIDField(primary_key=True, editable=False)

    class Meta:
        abstract = True

    def sync_from_welkin(self):
        raise NotImplementedError("This method must be implemented in concrete models.")
