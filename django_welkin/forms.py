from django import forms

from .models import Chat, Configuration


class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ["tenant", "instance", "api_client", "secret_key"]
        widgets = {"secret_key": forms.PasswordInput(render_value=True)}


class ChatForm(forms.ModelForm):
    message = forms.CharField(
        label="message", widget=forms.TextInput(attrs={"placeholder": "Send a message..."})
    )

    class Meta:
        model = Chat
        fields = ["message"]
