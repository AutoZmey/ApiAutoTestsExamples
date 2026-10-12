import pytest
from tests.fixtures.data_factories import OrderFactory
from tests.utils.api_client import ApiClient


@pytest.mark.api
class TestAnalytics:
    def test_analytics_metrics_aggregate(
        self, auth_user_client: ApiClient, sample_product: dict
    ):
        initial_metrics = auth_user_client.get_analytics().json()

        order_resp = auth_user_client.place_order(
            OrderFactory.build(product_id=sample_product["id"], quantity=2)
        )
        assert order_resp.status_code == 201
        order = order_resp.json()

        updated_metrics = auth_user_client.get_analytics().json()
        assert updated_metrics["total_orders"] == initial_metrics["total_orders"] + 1
        assert round(updated_metrics["total_revenue"], 2) == round(
            initial_metrics["total_revenue"] + order["total"], 2
        )
        assert updated_metrics["pending_orders"] == initial_metrics["pending_orders"] + 1

    def test_unauthenticated_cannot_access_analytics(self, api_client: ApiClient):
        response = api_client.get_analytics()
        assert response.status_code == 401
