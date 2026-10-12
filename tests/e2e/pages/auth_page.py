from playwright.sync_api import Locator, Page, expect
from tests.e2e.pages.base_page import BasePage


class AuthPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.btn_open_auth: Locator = page.locator("[data-testid='btn-open-auth']")
        self.tab_login: Locator = page.locator("[data-testid='tab-login']")
        self.tab_register: Locator = page.locator("[data-testid='tab-register']")

        self.input_login_email: Locator = page.locator("[data-testid='input-login-email']")
        self.input_login_password: Locator = page.locator("[data-testid='input-login-password']")
        self.btn_login_submit: Locator = page.locator("[data-testid='btn-login-submit']")

        self.input_register_name: Locator = page.locator("[data-testid='input-register-name']")
        self.input_register_email: Locator = page.locator("[data-testid='input-register-email']")
        self.input_register_password: Locator = page.locator("[data-testid='input-register-password']")
        self.btn_register_submit: Locator = page.locator("[data-testid='btn-register-submit']")

        self.error_msg: Locator = page.locator("[data-testid='auth-error-msg']")
        self.user_profile_badge: Locator = page.locator("[data-testid='user-profile-badge']")
        self.btn_logout: Locator = page.locator("[data-testid='btn-logout']")

    def open_modal(self) -> None:
        self.btn_open_auth.click()

    def register(self, full_name: str, email: str, password: str) -> None:
        self.tab_register.click()
        self.input_register_name.fill(full_name)
        self.input_register_email.fill(email)
        self.input_register_password.fill(password)
        self.btn_register_submit.click()

    def login(self, email: str, password: str) -> None:
        self.tab_login.click()
        self.input_login_email.fill(email)
        self.input_login_password.fill(password)
        self.btn_login_submit.click()

    def logout(self) -> None:
        self.btn_logout.click()
