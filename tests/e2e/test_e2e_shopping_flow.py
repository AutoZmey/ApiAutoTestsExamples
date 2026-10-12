import pytest
from playwright.sync_api import Page, expect
from tests.e2e.pages.auth_page import AuthPage
from tests.e2e.pages.cart_page import CartPage
from tests.e2e.pages.catalog_page import CatalogPage
from tests.fixtures.data_factories import UserFactory


@pytest.mark.e2e
class TestE2EShoppingFlow:
    def test_catalog_search_and_filter(self, page: Page, live_server_url: str):
        catalog = CatalogPage(page, live_server_url)
        catalog.navigate()

        expect(catalog.product_cards).to_have_count(6)

        catalog.filter_by_category("Audio")
        expect(catalog.product_cards).to_have_count(1)
        expect(catalog.product_cards.first).to_contain_text("Headset")

        catalog.filter_by_category("")
        expect(catalog.product_cards).to_have_count(6)

        catalog.search_for("Curved")
        expect(catalog.product_cards).to_have_count(1)
        expect(catalog.product_cards.first).to_contain_text("Ultra-Wide 34' Curved Monitor")

    def test_end_to_end_cart_and_checkout_flow(self, page: Page, live_server_url: str):
        auth_page = AuthPage(page, live_server_url)
        catalog = CatalogPage(page, live_server_url)
        cart = CartPage(page, live_server_url)

        catalog.navigate()

        user = UserFactory.build()
        auth_page.open_modal()
        auth_page.register(user["full_name"], user["email"], user["password"])
        auth_page.login(user["email"], user["password"])
        auth_page.wait_for_toast("Welcome back")

        catalog.add_product_to_cart(1)
        catalog.wait_for_toast("Added")
        expect(catalog.cart_badge).to_have_text("1")

        catalog.open_cart()
        expect(cart.items).to_have_count(1)
        expect(cart.total_price).to_contain_text("$142.99")

        cart.checkout("742 Evergreen Terrace, Springfield")
        cart.wait_for_toast("placed successfully")

        expect(catalog.cart_badge).to_have_text("0")
        expect(page.locator("[data-testid='orders-table']")).to_be_visible()
        expect(page.locator("tr[data-testid^='order-row-']")).to_have_count(1)
