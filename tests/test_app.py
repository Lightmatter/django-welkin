import pytest
from django.core import management
from django.urls import reverse
from django_welkin.models import APIKey
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_no_migrations(capsys):
    management.call_command("makemigrations")

    captured = capsys.readouterr()
    assert "No changes detected" in captured.out


def test_add_api_key(page: Page, live_server, admin_user):
    page.goto(f'{live_server.url}{reverse("admin:django_welkin_apikey_add")}')
    expect(page.locator("#site-name")).to_have_text("Django administration")

    page.fill('input[name="username"]', admin_user.username)
    page.fill('input[name="password"]', "password")
    page.click("text=Log in")
    expect(page).to_have_title("Add API Key | Django site admin")

    page.fill("#id_api_client", "api_client")
    page.fill("#id_secret_key", "secret_key")

    with page.expect_popup() as popup_info:
        page.click("#add_id_instance")

    instance_page = popup_info.value
    instance_page.wait_for_load_state()
    instance_page.fill("#id_name", "instance")

    with instance_page.expect_popup() as popup_info:
        instance_page.click("#add_id_tenant")

    tenant_page = popup_info.value
    tenant_page.wait_for_load_state()
    tenant_page.fill("#id_name", "tenant")
    tenant_page.click("text=Save")
    expect(instance_page.locator("#id_tenant")).to_contain_text("tenant")

    instance_page.click("text=Save")
    expect(page.locator("#id_instance")).to_contain_text("instance")

    page.click("text=Save")
    expect(page.locator("#result_list")).to_contain_text("tenant/instance API key")

    api_key = APIKey.objects.get(api_client="api_client", secret_key="secret_key")

    assert api_key.api_client == "api_client"
    assert api_key.secret_key == "secret_key"
    assert api_key.instance.name == "instance"
    assert api_key.instance.tenant.name == "tenant"
