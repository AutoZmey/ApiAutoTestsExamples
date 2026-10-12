from playwright.sync_api import Locator, Page
from tests.e2e.pages.base_page import BasePage


class OrdersPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.nav_orders: Locator = page.locator("[data-testid='nav-orders']")
        self.orders_table: Locator = page.locator("[data-testid='orders-table']")

    def open(self) -> None:
        self.nav_orders.click()

    def get_order_status_badge(self, order_id: int) -> Locator:
        return self.page.locator(f"[data-testid='order-row-{order_id}'] [data-testid='order-status-badge']")

    def cancel_order(self, order_id: int) -> None:
        self.page.locator(f"[data-testid='btn-cancel-order-{order_id}']").click()

    def update_order_status(self, order_id: int, new_status: str) -> None:
        select = self.page.locator(f"[data-testid='select-status-update-{order_id}']")
        select.select_option(new_status)
        self.page.locator(f"[data-testid='btn-update-status-{order_id}']").click()
