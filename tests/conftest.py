import socket
import threading
import time
from typing import Generator
import httpx
import pytest
import uvicorn
from playwright.sync_api import Browser, BrowserContext, Page

from src.app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from src.app.database import reset_db
from src.app.main import app
from tests.fixtures.data_factories import ProductFactory, UserFactory
from tests.utils.api_client import ApiClient


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(autouse=True)
def reset_database_state():
    reset_db()


@pytest.fixture
def http_client(live_server_url: str) -> Generator[httpx.Client, None, None]:
    with httpx.Client(base_url=live_server_url, timeout=10.0) as client:
        yield client


@pytest.fixture
def api_client(http_client: httpx.Client) -> ApiClient:
    return ApiClient(client=http_client)


@pytest.fixture
def admin_client(api_client: ApiClient) -> ApiClient:
    res = api_client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    return api_client


@pytest.fixture
def registered_user(api_client: ApiClient) -> dict:
    user_payload = UserFactory.build(role="user")
    res = api_client.register(user_payload)
    assert res.status_code == 201
    return {**user_payload, "id": res.json()["id"]}


@pytest.fixture
def auth_user_client(http_client: httpx.Client, registered_user: dict) -> ApiClient:
    client = ApiClient(client=http_client)
    res = client.login(registered_user["email"], registered_user["password"])
    assert res.status_code == 200
    return client


@pytest.fixture
def sample_product(admin_client: ApiClient) -> dict:
    payload = ProductFactory.build(stock=15, price=89.99, category="Hardware")
    res = admin_client.create_product(payload)
    assert res.status_code == 201
    return res.json()


@pytest.fixture(scope="session")
def live_server_url() -> Generator[str, None, None]:
    port = get_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    max_wait = 5.0
    start_time = time.time()
    ready = False

    while time.time() - start_time < max_wait:
        try:
            with httpx.Client() as cl:
                r = cl.get(f"{base_url}/api/system/health", timeout=0.5)
                if r.status_code == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.05)

    if not ready:
        raise RuntimeError("Live test server failed to start within timeout")

    yield base_url

    server.should_exit = True
    thread.join(timeout=3)
