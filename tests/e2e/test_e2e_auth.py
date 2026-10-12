import pytest
from playwright.sync_api import Page, expect
from tests.e2e.pages.auth_page import AuthPage
from tests.fixtures.data_factories import UserFactory


@pytest.mark.e2e
class TestE2EAuth:
    def test_user_registration_and_login_flow(self, page: Page, live_server_url: str):
        auth_page = AuthPage(page, live_server_url)
        auth_page.navigate()

        user = UserFactory.build()

        auth_page.open_modal()
        auth_page.register(user["full_name"], user["email"], user["password"])
        auth_page.wait_for_toast("Account created")

        auth_page.login(user["email"], user["password"])
        auth_page.wait_for_toast(f"Welcome back, {user['full_name']}")

        expect(auth_page.user_profile_badge).to_have_text(user["full_name"])

        auth_page.logout()
        auth_page.wait_for_toast("Signed out successfully")
        expect(auth_page.btn_open_auth).to_be_visible()

    def test_login_invalid_credentials_shows_error(self, page: Page, live_server_url: str):
        auth_page = AuthPage(page, live_server_url)
        auth_page.navigate()

        auth_page.open_modal()
        auth_page.login("unknown_user@domain.com", "WrongPassword123!")

        expect(auth_page.error_msg).to_be_visible()
        expect(auth_page.error_msg).to_contain_text("Invalid email or password")
