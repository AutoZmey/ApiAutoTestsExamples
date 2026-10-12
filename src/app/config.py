import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "pulseops.db"))
SECRET_KEY = os.getenv("SECRET_KEY", "pulseops-super-secure-jwt-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@pulseops.io")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminPass123!")
ADMIN_NAME = "System Administrator"
