import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional
from src.app.config import DB_PATH, ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD
from src.app.models import (
    AnalyticsSummary,
    OrderItemResponse,
    OrderResponse,
    OrderStatus,
    ProductResponse,
    Role,
    UserResponse,
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                status TEXT NOT NULL,
                shipping_address TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax REAL NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_title TEXT NOT NULL,
                unit_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
    conn.close()
    seed_default_data()


_CACHED_ADMIN_HASH = None


def seed_default_data() -> None:
    global _CACHED_ADMIN_HASH
    from src.app.security import hash_password

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (ADMIN_EMAIL,))
    if not cursor.fetchone():
        if _CACHED_ADMIN_HASH is None:
            _CACHED_ADMIN_HASH = hash_password(ADMIN_PASSWORD)
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ADMIN_EMAIL, _CACHED_ADMIN_HASH, ADMIN_NAME, Role.ADMIN.value, now),
        )

    cursor.execute("SELECT COUNT(*) as count FROM products")
    if cursor.fetchone()["count"] == 0:
        now = datetime.now(timezone.utc).isoformat()
        initial_products = [
            ("Ergonomic Mechanical Keyboard", "KB-MECH-01", "Hardware", 129.99, 15, "Low-profile tactile switches with RGB"),
            ("Ultra-Wide 34' Curved Monitor", "MON-UW-34", "Hardware", 499.90, 8, "144Hz IPS display with USB-C Hub"),
            ("Noise-Cancelling Wireless Headset", "AU-NC-02", "Audio", 189.50, 20, "Active noise cancelling with dual mic"),
            ("Precision Wireless Mouse", "MS-WL-09", "Accessories", 59.00, 30, "Ergonomic 4000 DPI rechargeable mouse"),
            ("Aluminum Thunderbolt 4 Dock", "DK-TB4-03", "Accessories", 199.00, 5, "Dual 4K output with 100W power delivery"),
            ("Smart Coffee Warming Coaster", "OF-CW-01", "Office", 29.99, 0, "Keeps beverage at perfect temperature (Out of Stock)"),
        ]
        cursor.executemany(
            """
            INSERT INTO products (title, sku, category, price, stock, description, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """,
            [(p[0], p[1], p[2], p[3], p[4], p[5], now) for p in initial_products],
        )

    conn.commit()
    conn.close()


def reset_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute("DROP TABLE IF EXISTS order_items")
        conn.execute("DROP TABLE IF EXISTS orders")
        conn.execute("DROP TABLE IF EXISTS products")
        conn.execute("DROP TABLE IF EXISTS users")
    conn.close()
    init_db()


# User Queries
def create_user(email: str, password_hash: str, full_name: str, role: Role = Role.USER) -> UserResponse:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (email, password_hash, full_name, role, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (email, password_hash, full_name, role.value, now),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return UserResponse(
        id=user_id,
        email=email,
        full_name=full_name,
        role=role,
        created_at=now,
    )


def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return UserResponse(
        id=row["id"],
        email=row["email"],
        full_name=row["full_name"],
        role=Role(row["role"]),
        created_at=row["created_at"],
    )


# Product Queries
def get_products(category: Optional[str] = None, search: Optional[str] = None, active_only: bool = True) -> List[ProductResponse]:
    conn = get_connection()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if active_only:
        query += " AND is_active = 1"
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR sku LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])

    query += " ORDER BY id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        ProductResponse(
            id=r["id"],
            title=r["title"],
            sku=r["sku"],
            category=r["category"],
            price=round(float(r["price"]), 2),
            stock=int(r["stock"]),
            description=r["description"],
            is_active=bool(r["is_active"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


def get_product_by_id(product_id: int) -> Optional[ProductResponse]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return ProductResponse(
        id=row["id"],
        title=row["title"],
        sku=row["sku"],
        category=row["category"],
        price=round(float(row["price"]), 2),
        stock=int(row["stock"]),
        description=row["description"],
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
    )


def create_product(title: str, sku: str, category: str, price: float, stock: int, description: str = "") -> ProductResponse:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO products (title, sku, category, price, stock, description, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (title, sku, category, price, stock, description, now),
    )
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ProductResponse(
        id=product_id,
        title=title,
        sku=sku,
        category=category,
        price=price,
        stock=stock,
        description=description,
        is_active=True,
        created_at=now,
    )


def update_product(product_id: int, updates: dict) -> Optional[ProductResponse]:
    if not updates:
        return get_product_by_id(product_id)

    set_clauses = [f"{k} = ?" for k in updates.keys()]
    values = list(updates.values())
    values.append(product_id)

    conn = get_connection()
    with conn:
        conn.execute(f"UPDATE products SET {', '.join(set_clauses)} WHERE id = ?", values)
    conn.close()
    return get_product_by_id(product_id)


def delete_product(product_id: int) -> bool:
    conn = get_connection()
    with conn:
        cursor = conn.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
    conn.close()
    return cursor.rowcount > 0


# Order Queries
def create_order(user_id: int, user_email: str, items_req: List[dict], shipping_address: str) -> OrderResponse:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    subtotal = 0.0
    processed_items = []

    # Validate stock and lock/update items in transaction
    with conn:
        for item in items_req:
            row = cursor.execute("SELECT * FROM products WHERE id = ? AND is_active = 1", (item["product_id"],)).fetchone()
            if not row:
                raise ValueError(f"Product #{item['product_id']} not found or inactive")

            available_stock = int(row["stock"])
            requested_qty = item["quantity"]
            if available_stock < requested_qty:
                raise ValueError(
                    f"Insufficient stock for '{row['title']}'. Requested: {requested_qty}, available: {available_stock}"
                )

            item_subtotal = round(float(row["price"]) * requested_qty, 2)
            subtotal += item_subtotal

            # Deduct stock
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (requested_qty, row["id"]))

            processed_items.append({
                "product_id": row["id"],
                "product_title": row["title"],
                "unit_price": float(row["price"]),
                "quantity": requested_qty,
                "subtotal": item_subtotal,
            })

        subtotal = round(subtotal, 2)
        tax = round(subtotal * 0.1, 2)
        total = round(subtotal + tax, 2)

        cursor.execute(
            """
            INSERT INTO orders (user_id, user_email, status, shipping_address, subtotal, tax, total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, user_email, OrderStatus.PENDING.value, shipping_address, subtotal, tax, total, now),
        )
        order_id = cursor.lastrowid

        for p_item in processed_items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, product_title, unit_price, quantity, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    p_item["product_id"],
                    p_item["product_title"],
                    p_item["unit_price"],
                    p_item["quantity"],
                    p_item["subtotal"],
                ),
            )

    conn.close()
    return get_order_by_id(order_id)


def get_order_by_id(order_id: int) -> Optional[OrderResponse]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not row:
        conn.close()
        return None

    item_rows = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    conn.close()

    items = [
        OrderItemResponse(
            product_id=ir["product_id"],
            product_title=ir["product_title"],
            unit_price=round(float(ir["unit_price"]), 2),
            quantity=ir["quantity"],
            subtotal=round(float(ir["subtotal"]), 2),
        )
        for ir in item_rows
    ]

    return OrderResponse(
        id=row["id"],
        user_id=row["user_id"],
        user_email=row["user_email"],
        items=items,
        status=OrderStatus(row["status"]),
        shipping_address=row["shipping_address"],
        subtotal=round(float(row["subtotal"]), 2),
        tax=round(float(row["tax"]), 2),
        total=round(float(row["total"]), 2),
        created_at=row["created_at"],
    )


def list_orders(user_id: Optional[int] = None) -> List[OrderResponse]:
    conn = get_connection()
    query = "SELECT id FROM orders"
    params = []
    if user_id is not None:
        query += " WHERE user_id = ?"
        params.append(user_id)
    query += " ORDER BY id DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    orders = []
    for r in rows:
        order = get_order_by_id(r["id"])
        if order:
            orders.append(order)
    return orders


def update_order_status(order_id: int, new_status: OrderStatus) -> Optional[OrderResponse]:
    order = get_order_by_id(order_id)
    if not order:
        return None

    conn = get_connection()
    with conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status.value, order_id))
    conn.close()
    return get_order_by_id(order_id)


def cancel_order(order_id: int) -> Optional[OrderResponse]:
    order = get_order_by_id(order_id)
    if not order:
        return None

    if order.status == OrderStatus.CANCELLED:
        return order

    if order.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
        raise ValueError(f"Cannot cancel order in '{order.status.value}' state")

    conn = get_connection()
    with conn:
        # Restore product stock
        for item in order.items:
            conn.execute(
                "UPDATE products SET stock = stock + ? WHERE id = ?",
                (item.quantity, item.product_id),
            )
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (OrderStatus.CANCELLED.value, order_id))
    conn.close()
    return get_order_by_id(order_id)


# Analytics
def get_analytics_summary() -> AnalyticsSummary:
    conn = get_connection()
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_revenue = conn.execute("SELECT COALESCE(SUM(total), 0.0) FROM orders WHERE status != 'CANCELLED'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'PENDING'").fetchone()[0]
    shipped = conn.execute("SELECT COUNT(*) FROM orders WHERE status IN ('SHIPPED', 'DELIVERED')").fetchone()[0]
    total_products = conn.execute("SELECT COUNT(*) FROM products WHERE is_active = 1").fetchone()[0]
    low_stock = conn.execute("SELECT COUNT(*) FROM products WHERE is_active = 1 AND stock < 10").fetchone()[0]
    conn.close()

    return AnalyticsSummary(
        total_orders=total_orders,
        total_revenue=round(float(total_revenue), 2),
        pending_orders=pending,
        shipped_orders=shipped,
        total_products=total_products,
        low_stock_products=low_stock,
    )


init_db()

