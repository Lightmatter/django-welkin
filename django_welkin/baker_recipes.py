from django.conf import settings
from environ import Env, Path
from model_bakery.recipe import Recipe

from .models import Configuration

env = Env()
env.read_env(Path(settings.PROJDIR, ".env"))

configuration = Recipe(  # noqa S106
    Configuration,
    tenant=env("WELKIN_TENANT", default="tenant"),
    instance=env("WELKIN_INSTANCE", default="instance"),
    api_client=env("WELKIN_API_CLIENT", default="api_client"),
    secret_key=env("WELKIN_SECRET", default="secret_key"),
)
