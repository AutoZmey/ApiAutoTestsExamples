import pytest
from src.app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from tests.fixtures.data_factories import UserFactory
from tests.utils.api_client import ApiClient


@pytest.mark.api
@pytest.mark.smoke
class TestAuthentication:
    def test_register_new_user_success(self, api_client: ApiClient):
        payload = UserFactory.build(role="user")
        response = api_client.register(payload)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["full_name"] == payload["full_name"]
        assert data["role"] == "user"
        assert "password" not in data
        assert "id" in data

    def test_register_duplicate_email_fails(self, api_client: ApiClient):
        payload = UserFactory.build()
        first_resp = api_client.register(payload)
        assert first_resp.status_code == 201

        duplicate_resp = api_client.register(payload)
        assert duplicate_resp.status_code == 409
        assert "already exists" in duplicate_resp.json()["detail"]

    @pytest.mark.parametrize(
        "invalid_field, payload_override",
        [
            ("invalid_email", {"email": "not-an-email"}),
            ("short_password", {"password": "123"}),
            ("empty_name", {"full_name": ""}),
        ],
    )
    def test_register_validation_errors(self, api_client: ApiClient, invalid_field, payload_override):
        base_payload = UserFactory.build()
        base_payload.update(payload_override)
        response = api_client.register(base_payload)
        assert response.status_code == 422

    def test_login_success(self, api_client: ApiClient, registered_user: dict):
        response = api_client.login(registered_user["email"], registered_user["password"])

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == registered_user["email"]

    def test_login_invalid_password(self, api_client: ApiClient, registered_user: dict):
        response = api_client.login(registered_user["email"], "WrongPassword999!")

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, api_client: ApiClient):
        response = api_client.login("nobody_exists_404@nowhere.com", "SomePassword123!")

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_get_current_user_profile(self, auth_user_client: ApiClient, registered_user: dict):
        response = auth_user_client.get_me()

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registered_user["email"]
        assert data["full_name"] == registered_user["full_name"]

    def test_unauthorized_profile_request_fails(self, api_client: ApiClient):
        response = api_client.get_me()
        assert response.status_code == 401
