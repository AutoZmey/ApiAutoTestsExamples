from typing import Any, Dict, Optional
import httpx


class ApiClient:
    def __init__(self, client: httpx.Client, token: Optional[str] = None):
        self.client = client
        self.token = token

    def _headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def register(self, user_data: dict) -> httpx.Response:
        return self.client.post("/api/auth/register", json=user_data)

    def login(self, email: str, password: str) -> httpx.Response:
        response = self.client.post("/api/auth/login", json={"email": email, "password": password})
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        return response

    def get_me(self) -> httpx.Response:
        return self.client.get("/api/auth/me", headers=self._headers())

    def get_products(self, params: Optional[dict] = None) -> httpx.Response:
        return self.client.get("/api/products", params=params)

    def get_product(self, product_id: int) -> httpx.Response:
        return self.client.get(f"/api/products/{product_id}")

    def create_product(self, product_data: dict) -> httpx.Response:
        return self.client.post("/api/products", json=product_data, headers=self._headers())

    def update_product(self, product_id: int, updates: dict) -> httpx.Response:
        return self.client.put(f"/api/products/{product_id}", json=updates, headers=self._headers())

    def delete_product(self, product_id: int) -> httpx.Response:
        return self.client.delete(f"/api/products/{product_id}", headers=self._headers())

    def place_order(self, order_data: dict) -> httpx.Response:
        return self.client.post("/api/orders", json=order_data, headers=self._headers())

    def get_orders(self) -> httpx.Response:
        return self.client.get("/api/orders", headers=self._headers())

    def get_order(self, order_id: int) -> httpx.Response:
        return self.client.get(f"/api/orders/{order_id}", headers=self._headers())

    def update_order_status(self, order_id: int, status: str) -> httpx.Response:
        return self.client.patch(
            f"/api/orders/{order_id}/status",
            json={"status": status},
            headers=self._headers(),
        )

    def cancel_order(self, order_id: int) -> httpx.Response:
        return self.client.post(f"/api/orders/{order_id}/cancel", headers=self._headers())

    def get_analytics(self) -> httpx.Response:
        return self.client.get("/api/analytics/summary", headers=self._headers())

    def reset_db(self) -> httpx.Response:
        return self.client.post("/api/system/reset")
