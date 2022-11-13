from django import forms

from .models import APIKey, Chat


class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ["api_client", "secret_key", "instance"]
        widgets = {"secret_key": forms.PasswordInput(render_value=True)}


class ChatForm(forms.ModelForm):
    message = forms.CharField(
        label="message",
        widget=forms.TextInput(attrs={"placeholder": "Send a message..."}),
    )

    class Meta:
        model = Chat
        fields = ["message"]
