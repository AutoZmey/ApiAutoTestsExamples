import pytest
from tests.fixtures.data_factories import ProductFactory
from tests.utils.api_client import ApiClient


@pytest.mark.api
class TestProducts:
    def test_list_products_returns_seed_items(self, api_client: ApiClient):
        response = api_client.get_products()
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5
        assert all("sku" in item and "price" in item for item in data)

    def test_filter_products_by_category(self, api_client: ApiClient):
        response = api_client.get_products(params={"category": "Hardware"})
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        assert all(item["category"] == "Hardware" for item in items)

    def test_search_products_by_keyword(self, api_client: ApiClient):
        response = api_client.get_products(params={"search": "Mechanical"})
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert "Mechanical" in items[0]["title"]

    def test_admin_create_product_success(self, admin_client: ApiClient):
        payload = ProductFactory.build()
        response = admin_client.create_product(payload)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["sku"] == payload["sku"]
        assert data["stock"] == payload["stock"]
        assert data["price"] == payload["price"]
        assert data["is_active"] is True

    def test_admin_create_duplicate_sku_fails(self, admin_client: ApiClient):
        payload = ProductFactory.build()
        admin_client.create_product(payload)

        duplicate = admin_client.create_product(payload)
        assert duplicate.status_code == 409
        assert "already exists" in duplicate.json()["detail"]

    def test_regular_user_cannot_create_product(self, auth_user_client: ApiClient):
        payload = ProductFactory.build()
        response = auth_user_client.create_product(payload)
        assert response.status_code == 403

    def test_unauthenticated_cannot_create_product(self, api_client: ApiClient):
        payload = ProductFactory.build()
        response = api_client.create_product(payload)
        assert response.status_code == 401

    def test_admin_update_product_price_and_stock(self, admin_client: ApiClient, sample_product: dict):
        product_id = sample_product["id"]
        updates = {"price": 149.99, "stock": 40}
        response = admin_client.update_product(product_id, updates)

        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 149.99
        assert data["stock"] == 40

    def test_admin_delete_product(self, admin_client: ApiClient, sample_product: dict):
        product_id = sample_product["id"]
        del_resp = admin_client.delete_product(product_id)
        assert del_resp.status_code == 204

        fetch_resp = admin_client.get_products()
        active_ids = [p["id"] for p in fetch_resp.json()]
        assert product_id not in active_ids

    def test_get_nonexistent_product_returns_404(self, api_client: ApiClient):
        response = api_client.get_product(99999)
        assert response.status_code == 404
