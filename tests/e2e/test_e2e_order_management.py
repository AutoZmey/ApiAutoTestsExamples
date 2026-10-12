import pytest
from playwright.sync_api import Page, expect
from src.app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from tests.e2e.pages.auth_page import AuthPage
from tests.e2e.pages.cart_page import CartPage
from tests.e2e.pages.catalog_page import CatalogPage
from tests.e2e.pages.orders_page import OrdersPage
from tests.fixtures.data_factories import UserFactory


@pytest.mark.e2e
class TestE2EOrderManagement:
    def test_user_can_cancel_pending_order(self, page: Page, live_server_url: str):
        auth_page = AuthPage(page, live_server_url)
        catalog = CatalogPage(page, live_server_url)
        cart = CartPage(page, live_server_url)
        orders_page = OrdersPage(page, live_server_url)

        catalog.navigate()

        user = UserFactory.build()
        auth_page.open_modal()
        auth_page.register(user["full_name"], user["email"], user["password"])
        auth_page.login(user["email"], user["password"])
        auth_page.wait_for_toast("Welcome back")

        catalog.add_product_to_cart(1)
        catalog.open_cart()
        cart.checkout("456 Mission Street, San Francisco")
        cart.wait_for_toast("placed successfully")

        order_row = page.locator("tr[data-testid^='order-row-']").first
        order_id = order_row.get_attribute("data-testid").replace("order-row-", "")

        orders_page.cancel_order(int(order_id))
        orders_page.wait_for_toast("cancelled")

        badge = orders_page.get_order_status_badge(int(order_id))
        expect(badge).to_have_text("CANCELLED")

    def test_admin_can_update_order_status(self, page: Page, live_server_url: str):
        auth_page = AuthPage(page, live_server_url)
        catalog = CatalogPage(page, live_server_url)
        cart = CartPage(page, live_server_url)
        orders_page = OrdersPage(page, live_server_url)

        catalog.navigate()

        auth_page.open_modal()
        auth_page.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        auth_page.wait_for_toast("Welcome back")

        catalog.add_product_to_cart(2)
        catalog.open_cart()
        cart.checkout("999 Market St, Seattle")
        cart.wait_for_toast("placed successfully")

        order_row = page.locator("tr[data-testid^='order-row-']").first
        order_id = int(order_row.get_attribute("data-testid").replace("order-row-", ""))

        orders_page.update_order_status(order_id, "PROCESSING")
        orders_page.wait_for_toast("PROCESSING")

        badge = orders_page.get_order_status_badge(order_id)
        expect(badge).to_have_text("PROCESSING")
