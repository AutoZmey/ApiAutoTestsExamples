from playwright.sync_api import Locator, Page
from tests.e2e.pages.base_page import BasePage


class InventoryModal(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.btn_open: Locator = page.locator("[data-testid='nav-new-product']")
        self.input_title: Locator = page.locator("[data-testid='input-product-title']")
        self.input_sku: Locator = page.locator("[data-testid='input-product-sku']")
        self.input_category: Locator = page.locator("[data-testid='input-product-category']")
        self.input_price: Locator = page.locator("[data-testid='input-product-price']")
        self.input_stock: Locator = page.locator("[data-testid='input-product-stock']")
        self.btn_submit: Locator = page.locator("[data-testid='btn-submit-product']")

    def open(self) -> None:
        self.btn_open.click()

    def submit_product(
        self, title: str, sku: str, category: str, price: float, stock: int
    ) -> None:
        self.input_title.fill(title)
        self.input_sku.fill(sku)
        self.input_category.fill(category)
        self.input_price.fill(str(price))
        self.input_stock.fill(str(stock))
        self.btn_submit.click()
