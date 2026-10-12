from fastapi import APIRouter
from src.app import database

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "PulseOps Hub", "version": "1.0.0"}


@router.post("/reset")
def reset_database():
    database.reset_db()
    return {"status": "ok", "message": "Database reset to initial seed state"}
