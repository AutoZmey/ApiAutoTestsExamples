import pytest
from playwright.sync_api import Page, expect
from src.app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from tests.e2e.pages.auth_page import AuthPage
from tests.e2e.pages.catalog_page import CatalogPage
from tests.e2e.pages.inventory_modal import InventoryModal
from tests.fixtures.data_factories import ProductFactory, UserFactory


@pytest.mark.e2e
class TestE2EInventory:
    def test_admin_can_create_new_catalog_product(self, page: Page, live_server_url: str):
        auth_page = AuthPage(page, live_server_url)
        catalog = CatalogPage(page, live_server_url)
        inventory_modal = InventoryModal(page, live_server_url)

        catalog.navigate()

        auth_page.open_modal()
        auth_page.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        auth_page.wait_for_toast("Welcome back")

        prod_data = ProductFactory.build(stock=12, price=320.00, category="Hardware")

        inventory_modal.open()
        inventory_modal.submit_product(
            title=prod_data["title"],
            sku=prod_data["sku"],
            category=prod_data["category"],
            price=prod_data["price"],
            stock=prod_data["stock"],
        )
        inventory_modal.wait_for_toast("added to catalog")

        catalog.search_for(prod_data["title"])
        new_card = catalog.product_cards.first
        expect(new_card).to_be_visible()
        expect(new_card).to_contain_text(prod_data["title"])
        expect(new_card).to_contain_text("$320.00")

    def test_standard_user_cannot_access_new_product_button(self, page: Page, live_server_url: str):
        auth_page = AuthPage(page, live_server_url)
        catalog = CatalogPage(page, live_server_url)
        inventory_modal = InventoryModal(page, live_server_url)

        catalog.navigate()

        user = UserFactory.build(role="user")
        auth_page.open_modal()
        auth_page.register(user["full_name"], user["email"], user["password"])
        auth_page.login(user["email"], user["password"])
        auth_page.wait_for_toast("Welcome back")

        expect(inventory_modal.btn_open).to_be_hidden()
