from fastapi import APIRouter, Depends
from src.app import database
from src.app.models import AnalyticsSummary, UserResponse
from src.app.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics(current_user: UserResponse = Depends(get_current_user)):
    return database.get_analytics_summary()
