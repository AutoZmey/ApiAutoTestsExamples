from playwright.sync_api import Locator, Page
from tests.e2e.pages.base_page import BasePage


class CatalogPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.search_input: Locator = page.locator("[data-testid='input-search']")
        self.category_select: Locator = page.locator("[data-testid='select-category']")
        self.product_cards: Locator = page.locator("[data-testid='product-card']")
        self.cart_toggle_btn: Locator = page.locator("[data-testid='cart-toggle-btn']")
        self.cart_badge: Locator = page.locator("[data-testid='cart-badge-count']")

    def search_for(self, query: str) -> None:
        self.search_input.fill(query)
        self.page.wait_for_timeout(350)

    def filter_by_category(self, category_name: str) -> None:
        self.category_select.select_option(category_name)
        self.page.wait_for_timeout(200)

    def add_product_to_cart(self, product_id: int) -> None:
        self.page.locator(f"[data-testid='btn-add-to-cart-{product_id}']").click()

    def open_cart(self) -> None:
        self.cart_toggle_btn.click()
