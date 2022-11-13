from django.db import models

from .api import APIKey, Instance


class WelkinModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)

    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @classmethod
    def from_webhook(cls, payload):
        return cls(
            id=payload["sourceId"],
            instance=Instance.objects.get(name=payload["instanceName"]),
        )

    def sync(self):
        raise NotImplementedError("This method must be implemented in concrete models.")

    @property
    def client(self):
        key = APIKey.objects.get(instance_id=self.instance_id)

        return key._client
