from django.db import models


class WelkinModel(models.Model):

    id = models.UUIDField(primary_key=True, editable=False)

    class Meta:
        abstract = True

    def sync_from_welkin(self):
        raise NotImplementedError("This method must be implemented in concrete models.")
