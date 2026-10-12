import random
import uuid
from faker import Faker

fake = Faker()


class UserFactory:
    @staticmethod
    def build(role: str = "user") -> dict:
        unique_suffix = uuid.uuid4().hex[:6]
        return {
            "email": f"test_{unique_suffix}_{fake.email()}",
            "password": "SecurePassword123!",
            "full_name": fake.name(),
            "role": role,
        }


class ProductFactory:
    @staticmethod
    def build(stock: int = 25, price: float = 79.99, category: str = "Hardware") -> dict:
        unique_sku = f"SKU-{uuid.uuid4().hex[:6].upper()}"
        return {
            "title": f"{fake.word().capitalize()} Pro Edition",
            "sku": unique_sku,
            "category": category,
            "price": round(price, 2),
            "stock": stock,
            "description": fake.sentence(nb_words=10),
        }


class OrderFactory:
    @staticmethod
    def build(product_id: int, quantity: int = 1) -> dict:
        return {
            "shipping_address": fake.address().replace("\n", ", "),
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ],
        }
