from django.urls import path

from .views import chat, webhook

urlpatterns = [
    path("webhook/", webhook, name="welkin"),
    path("chat/", chat, name="chat"),
]
