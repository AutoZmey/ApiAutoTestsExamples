# PulseOps Hub — Test Automation Showcase

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![pytest](https://img.shields.io/badge/pytest-9.1+-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.63+-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](.github/workflows/tests.yml)
[![Tests](https://img.shields.io/badge/Tests-40%20Passed-brightgreen)](https://github.com/AutoZmey/ApiAutoTestsExamples)
[![Architecture](https://img.shields.io/badge/Design-Page_Object_Model-8A2BE2)](#test-framework-architecture)

> A modern Order Fulfillment & Inventory Management platform paired with an enterprise-grade automated testing suite (REST API & Playwright E2E with Page Object Model) built in Python.

---

## Overview

**PulseOps Hub** is a full-stack operational hub featuring:
- **Role-Based Authentication**: Secure JWT-based access with Admin and Standard User tiers.
- **Dynamic Inventory Catalog**: Product search, real-time category filtering, stock depletion, and price tracking.
- **Cart & Order Processing**: Transactional checkout, tax calculations, stock reservation, and stateful fulfillment (`PENDING` → `PROCESSING` → `SHIPPED` → `DELIVERED` / `CANCELLED`).
- **Inventory Restoration**: Automatic stock recovery upon order cancellation.
- **Operations Analytics**: Real-time business metrics dashboard.
- **Modern Interactive Dashboard**: Tailwind-styled single-page frontend with dedicated `data-testid` hooks for reliable end-to-end automation.

---

## System & Test Architecture

```
                                    +-----------------------+
                                    |     PulseOps App      |
                                    |   (FastAPI + SQLite)  |
                                    +-----------+-----------+
                                                ^
                        REST API Calls          |          UI Interactivity
                   (httpx / ApiClient)          |       (Playwright Chromium)
                                                |
               +--------------------------------+--------------------------------+
               |                                                                 |
    +----------+----------+                                           +----------+----------+
    |   API Test Suite    |                                           |     E2E Test Suite  |
    |  (pytest / fixtures)|                                           |   (POM Architecture)|
    +----------+----------+                                           +----------+----------+
               |                                                                 |
     +---------+---------+                                             +---------+---------+
     | - Auth & Tokens   |                                             | - Auth Page       |
     | - Catalog CRUD    |                                             | - Catalog Page    |
     | - Order Lifecycle |                                             | - Cart Drawer     |
     | - Access Control  |                                             | - Orders Table    |
     | - Stock Sync      |                                             | - Inventory Modal |
     +-------------------+                                             +-------------------+
```

---

## Repository Structure

```
├── .github/
│   └── workflows/
│       └── tests.yml             # GitHub Actions CI workflow
├── src/
│   ├── app/
│   │   ├── main.py               # FastAPI application entrypoint
│   │   ├── config.py             # Application settings & credentials
│   │   ├── database.py           # SQLite repository & seed management
│   │   ├── security.py           # JWT generation, password hashing & dependencies
│   │   ├── models.py             # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── auth.py           # Registration & login endpoints
│   │   │   ├── products.py       # Catalog CRUD endpoints
│   │   │   ├── orders.py         # Order creation & fulfillment lifecycle
│   │   │   ├── analytics.py      # Operations metrics summary
│   │   │   └── system.py         # Health checks & database reset
│   │   └── static/
│   │       ├── index.html        # Modern dashboard UI
│   │       ├── app.js            # Frontend application logic
│   │       └── styles.css        # Custom styles & animations
├── tests/
│   ├── conftest.py               # Pytest fixtures & live test server lifecycle
│   ├── fixtures/
│   │   └── data_factories.py     # Faker-powered test data generators
│   ├── utils/
│   │   └── api_client.py         # Fluent API client abstraction
│   ├── api/                      # 32 Integration & API Test Cases
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   ├── test_orders.py
│   │   └── test_analytics.py
│   └── e2e/                      # 8 End-to-End Browser Test Cases
│       ├── pages/                # Page Object Model (POM)
│       │   ├── base_page.py
│       │   ├── auth_page.py
│       │   ├── catalog_page.py
│       │   ├── cart_page.py
│       │   ├── orders_page.py
│       │   └── inventory_modal.py
│       ├── test_e2e_auth.py
│       ├── test_e2e_shopping_flow.py
│       ├── test_e2e_order_management.py
│       └── test_e2e_inventory.py
├── Makefile                      # CLI shortcuts for local execution
├── pyproject.toml                # Project metadata & dependencies
└── pytest.ini                    # Pytest markers and configuration
```

---

## Test Design Highlights

1. **Page Object Model (POM)**:
   All page interactions and element locators are encapsulated in reusable classes under `tests/e2e/pages/`. Tests remain declarative, resilient to layout alterations, and readable.
2. **Dedicated Test Selectors**:
   Elements are referenced using resilient `data-testid` attributes (e.g. `data-testid="btn-add-to-cart-1"`, `data-testid="input-shipping-address"`), preventing fragile XPath or CSS-class-dependent bindings.
3. **Database State Isolation**:
   Every test runs with an automatic database reset fixture (`reset_database_state`), preventing test pollution and ensuring idempotent execution.
4. **Dynamic Data Factories**:
   Test inputs are synthesized using `Faker` and UUIDs (`UserFactory`, `ProductFactory`, `OrderFactory`), ensuring tests do not fail on duplicate collision edge cases.
5. **Background Live Server**:
   E2E tests boot an ephemeral Uvicorn server on a dynamically allocated free port, enabling true end-to-end network validation against the compiled frontend.

---

## Test Coverage Matrix

| Area | Suite | Scenarios Covered |
| :--- | :--- | :--- |
| **Authentication** | `tests/api/test_auth.py` | New user registration, duplicate email rejection (409), input validation (422), valid JWT issuance, invalid password handling (401), non-existent user handling, profile inspection (`/me`), unauthorized request handling. |
| **Catalog** | `tests/api/test_products.py` | Seed listing, category filtering, keyword search, admin product creation (201), duplicate SKU rejection (409), role enforcement (403 for non-admins, 401 for guests), price/stock updates, soft deletion, 404 responses. |
| **Orders** | `tests/api/test_orders.py` | Order creation with stock deduction, tax calculation (10%), out-of-stock validation (400), user data isolation, admin cross-tenant visibility, unauthorized order access (403), inventory restoration upon cancellation, fulfillment state transitions (`PENDING` → `PROCESSING` → `SHIPPED` → `DELIVERED`), non-cancellable shipped orders. |
| **Analytics** | `tests/api/test_analytics.py` | Metrics calculation, order placement revenue synchronization, low stock detection, unauthenticated rejection. |
| **E2E Auth** | `tests/e2e/test_e2e_auth.py` | Browser-based user registration, login modal handling, profile header badge display, invalid credentials feedback, logout flow. |
| **E2E Shopping** | `tests/e2e/test_e2e_shopping_flow.py` | Product search and filter UI, cart badge counter increments, cart drawer opening, subtotal/total calculation, checkout and transition to orders view. |
| **E2E Orders** | `tests/e2e/test_e2e_order_management.py` | Placing order, customer cancellation from orders table, status badge color updates, admin status transition controls. |
| **E2E Inventory** | `tests/e2e/test_e2e_inventory.py` | Admin modal product creation, immediate appearance in catalog search, restriction verification for standard users. |

---

## Getting Started

### Prerequisites

- **Python 3.12+**
- **uv** (recommended) or standard `pip`

### 1. Installation

Using `uv`:
```bash
# Clone the repository
git clone <repo-url>
cd autoTests_example

# Install dependencies
uv sync

# Install Playwright browser binaries
uv run playwright install chromium
```

Or using `Makefile`:
```bash
make install
```

---

## Running the Application

To launch the web service locally:

```bash
make run
# or
uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at `http://127.0.0.1:8000`.

Default administrator credentials:
- **Email:** `admin@pulseops.io`
- **Password:** `AdminPass123!`

---

## Executing Tests

### Run All Tests (API + E2E)
```bash
make test
# or
uv run pytest
```

### Run API Tests Only
```bash
make test-api
# or
uv run pytest tests/api -m api
```

### Run Playwright E2E Tests
```bash
make test-e2e
# or
uv run pytest tests/e2e -m e2e
```

### Run in Headed Browser Mode (Watching UI Execution)
```bash
uv run pytest tests/e2e --headed
```

### Run in Parallel (Multi-threaded with pytest-xdist)
```bash
uv run pytest -n auto
```

### Run Quick Smoke Tests
```bash
make test-smoke
# or
uv run pytest -m smoke
```

---

## Continuous Integration (CI)

The repository includes a GitHub Actions configuration at `.github/workflows/tests.yml`:
- Sets up Python 3.12 and `uv` caching.
- Installs dependencies and headless Chromium binaries.
- Executes the API and Playwright E2E suites on every pull request and push to `main`.
- Uploads test traces and reports as artifacts if any failure occurs.
