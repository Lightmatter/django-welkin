from django_welkin.models import Configuration
from environ import Env
from model_bakery.recipe import Recipe

env = Env()

configuration = Recipe(  # noqa S106
    Configuration,
    tenant=env("WELKIN_TENANT", default="tenant"),
    instance=env("WELKIN_INSTANCE", default="instance"),
    api_client=env("WELKIN_API_CLIENT", default="api_client"),
    secret_key=env("WELKIN_SECRET", default="secret_key"),
)
