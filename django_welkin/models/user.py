from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import WelkinModel, _Welkin


class User(WelkinModel):
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def sync_from_welkin(self):
        user = _Welkin().User(id=self.id).get()

        self.first_name = user.firstName
        self.last_name = user.lastName

        self.save()
