import pytest
from tests.fixtures.data_factories import OrderFactory, UserFactory
from tests.utils.api_client import ApiClient


@pytest.mark.api
class TestOrders:
    def test_place_order_success_and_stock_deducted(
        self, auth_user_client: ApiClient, sample_product: dict
    ):
        initial_stock = sample_product["stock"]
        order_payload = OrderFactory.build(product_id=sample_product["id"], quantity=2)

        response = auth_user_client.place_order(order_payload)
        assert response.status_code == 201
        order = response.json()

        assert order["status"] == "PENDING"
        assert order["shipping_address"] == order_payload["shipping_address"]
        assert len(order["items"]) == 1

        expected_subtotal = round(sample_product["price"] * 2, 2)
        expected_tax = round(expected_subtotal * 0.1, 2)
        expected_total = round(expected_subtotal + expected_tax, 2)

        assert order["subtotal"] == expected_subtotal
        assert order["tax"] == expected_tax
        assert order["total"] == expected_total

        updated_prod = auth_user_client.get_product(sample_product["id"]).json()
        assert updated_prod["stock"] == initial_stock - 2

    def test_place_order_insufficient_stock_fails(
        self, auth_user_client: ApiClient, sample_product: dict
    ):
        excessive_qty = sample_product["stock"] + 10
        payload = OrderFactory.build(product_id=sample_product["id"], quantity=excessive_qty)

        response = auth_user_client.place_order(payload)
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]

    def test_place_order_nonexistent_product_fails(self, auth_user_client: ApiClient):
        payload = OrderFactory.build(product_id=99999, quantity=1)
        response = auth_user_client.place_order(payload)
        assert response.status_code == 400

    def test_user_order_isolation(
        self, http_client, auth_user_client: ApiClient, sample_product: dict
    ):
        order_a = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=1)
        ).json()

        user_b_payload = UserFactory.build()
        auth_user_client.register(user_b_payload)
        client_b = ApiClient(client=http_client)
        client_b.login(user_b_payload["email"], user_b_payload["password"])

        order_b = client_b.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=1)
        ).json()

        orders_a = [o["id"] for o in auth_user_client.get_orders().json()]
        orders_b = [o["id"] for o in client_b.get_orders().json()]

        assert order_a["id"] in orders_a
        assert order_b["id"] not in orders_a
        assert order_b["id"] in orders_b
        assert order_a["id"] not in orders_b

    def test_user_cannot_view_other_users_order(
        self, http_client, auth_user_client: ApiClient, sample_product: dict
    ):
        order = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=1)
        ).json()

        other_user = UserFactory.build()
        auth_user_client.register(other_user)
        other_client = ApiClient(client=http_client)
        other_client.login(other_user["email"], other_user["password"])

        response = other_client.get_order(order["id"])
        assert response.status_code == 403

    def test_admin_can_view_all_orders(
        self, auth_user_client: ApiClient, admin_client: ApiClient, sample_product: dict
    ):
        order = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=1)
        ).json()

        all_orders = admin_client.get_orders().json()
        all_order_ids = [o["id"] for o in all_orders]
        assert order["id"] in all_order_ids

    def test_cancel_order_restores_inventory(
        self, auth_user_client: ApiClient, sample_product: dict
    ):
        initial_stock = sample_product["stock"]
        order = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=3)
        ).json()

        cancel_resp = auth_user_client.cancel_order(order["id"])
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "CANCELLED"

        restored_prod = auth_user_client.get_product(sample_product["id"]).json()
        assert restored_prod["stock"] == initial_stock

    def test_admin_update_order_status_lifecycle(
        self, auth_user_client: ApiClient, admin_client: ApiClient, sample_product: dict
    ):
        order = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=1)
        ).json()

        for next_status in ["PROCESSING", "SHIPPED", "DELIVERED"]:
            upd = admin_client.update_order_status(order["id"], next_status)
            assert upd.status_code == 200
            assert upd.json()["status"] == next_status

    def test_cannot_cancel_shipped_order(
        self, auth_user_client: ApiClient, admin_client: ApiClient, sample_product: dict
    ):
        order = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=1)
        ).json()
        admin_client.update_order_status(order["id"], "SHIPPED")

        cancel_resp = auth_user_client.cancel_order(order["id"])
        assert cancel_resp.status_code == 400
        assert "Cannot cancel order in 'SHIPPED' state" in cancel_resp.json()["detail"]

    def test_regular_user_cannot_update_order_status(
        self, auth_user_client: ApiClient, sample_product: dict
    ):
        order = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=1)
        ).json()
        resp = auth_user_client.update_order_status(order["id"], "DELIVERED")
        assert resp.status_code == 403
