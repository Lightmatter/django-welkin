from functools import cached_property

from django.db import models
from django.utils.translation import gettext_lazy as _
from welkin import Client


class Tenant(models.Model):
    name = models.CharField(max_length=255, help_text="Welkin organization name.")

    def __str__(self):
        return self.name


class Instance(models.Model):
    name = models.CharField(
        max_length=255, help_text="The environment inside a Welkin organization."
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class APIKey(models.Model):
    api_client = models.CharField(
        max_length=255, help_text="Welkin API client name.", verbose_name="API client"
    )
    secret_key = models.CharField(
        max_length=255, help_text="Welkin API client secret key."
    )

    instance = models.OneToOneField(Instance, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tenant}/{self.instance} API key"

    class Meta:
        verbose_name = _("API Key")

    @cached_property
    def _client(self) -> Client:
        """Instantiate a Welkin API client.

        NOTE: Unsure if caching this will cause issues because of:
        https://requests.readthedocs.io/en/latest/user/advanced/?highlight=keep%20alive#keep-alive

        If we start seeing weird connection errors, just change this to a normal property.

        Returns:
            Client: Welkin client.
        """
        return Client(
            tenant=self.instance.tenant.name,
            instance=self.instance.name,
            api_client=self.api_client,
            secret_key=self.secret_key,
        )
