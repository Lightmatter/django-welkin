from django.conf.urls import include
from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path

admin.autodiscover()


def _blank():
    return HttpResponse()


urlpatterns = [
    path("home/", _blank, name="home"),
    path("admin/", admin.site.urls),
    path("welkin/", include("django_welkin.urls")),
]
