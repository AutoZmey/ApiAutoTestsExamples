from playwright.sync_api import Locator, Page
from tests.e2e.pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.drawer: Locator = page.locator("[data-testid='cart-drawer']")
        self.items: Locator = page.locator("[data-testid='cart-item']")
        self.total_price: Locator = page.locator("[data-testid='cart-total-price']")
        self.input_shipping_address: Locator = page.locator("[data-testid='input-shipping-address']")
        self.btn_place_order: Locator = page.locator("[data-testid='btn-place-order']")
        self.btn_close_cart: Locator = page.locator("[data-testid='btn-close-cart']")

    def checkout(self, address: str) -> None:
        self.input_shipping_address.fill(address)
        self.btn_place_order.click()

    def close(self) -> None:
        self.btn_close_cart.click()
