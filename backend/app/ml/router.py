"""ML API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.database.models import User
from app.ml.schemas import (
    FeatureImportanceResponse,
    ModelPerformanceResponse,
    PredictionRequest,
    PredictionResponse,
    RetrainResponse,
)
from app.ml.service import MLService

router = APIRouter(prefix="/api/ml", tags=["ML Insights"])


@router.post("/predictions", response_model=PredictionResponse)
async def predict_trade(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PredictionResponse:
    """Predict profitability, behavioral risk, and pattern cluster for a trade."""
    try:
        return MLService.predict(current_user.id, request, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/risk-detection", response_model=PredictionResponse)
async def detect_risk(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PredictionResponse:
    """Compatibility endpoint focused on behavioral risk scoring."""
    return await predict_trade(request, db, current_user)


@router.post("/pattern-analysis", response_model=PredictionResponse)
async def analyze_pattern(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PredictionResponse:
    """Compatibility endpoint focused on clustering/pattern analysis."""
    return await predict_trade(request, db, current_user)


@router.get("/model-performance", response_model=ModelPerformanceResponse)
async def model_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ModelPerformanceResponse:
    """Return the latest model training metrics."""
    return MLService.model_performance(current_user.id, db)


@router.post("/retrain", response_model=RetrainResponse)
async def retrain_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RetrainResponse:
    """Retrain models on the user's history, falling back to demo data when needed."""
    return MLService.retrain(current_user.id, db)


@router.get("/features", response_model=FeatureImportanceResponse)
async def feature_importance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FeatureImportanceResponse:
    """Return the most important risk-model features."""
    return MLService.feature_importance(current_user.id, db)
