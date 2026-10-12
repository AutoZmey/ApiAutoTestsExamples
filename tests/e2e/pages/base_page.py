from typing import Optional
from playwright.sync_api import Locator, Page, expect


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "/") -> None:
        self.page.goto(f"{self.base_url}{path}")
        self.page.wait_for_load_state("domcontentloaded")

    def wait_for_toast(self, text_contains: Optional[str] = None) -> Locator:
        if text_contains:
            toast = self.page.locator(f"[data-testid='toast']:has-text('{text_contains}')")
        else:
            toast = self.page.locator("[data-testid='toast']")
        toast.last.wait_for(state="visible", timeout=5000)
        return toast.last
