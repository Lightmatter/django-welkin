from django_welkin.models import APIKey, Instance, Tenant
from environ import Env
from model_bakery.recipe import Recipe, foreign_key

env = Env()

tenant = Recipe(Tenant, name=env("WELKIN_TENANT", default="tenant"))

instance = Recipe(
    Instance,
    name=env("WELKIN_INSTANCE", default="instance"),
    tenant=foreign_key(tenant),
)

api_key = Recipe(  # noqa S106
    APIKey,
    api_client=env("WELKIN_API_CLIENT", default="api_client"),
    secret_key=env("WELKIN_SECRET", default="secret_key"),
    instance=foreign_key(instance),
)
