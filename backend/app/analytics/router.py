"""Analytics API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.schemas import AnalyticsDashboardResponse, AnalyticsSummaryResponse
from app.analytics.service import AnalyticsService
from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.database.models import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnalyticsDashboardResponse:
    """Return the full analytics payload used by the dashboard."""
    return AnalyticsService.get_dashboard(current_user.id, db)


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnalyticsSummaryResponse:
    """Return headline trading and behavioral metrics."""
    return AnalyticsService.get_dashboard(current_user.id, db).summary
