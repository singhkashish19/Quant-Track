"""Schemas for ML insights and model operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.trades.schemas import TradeCreate


class PredictionRequest(BaseModel):
    """Prediction request.

    If no trade_id or trade payload is provided, the latest user trade is used.
    """

    trade_id: Optional[int] = Field(None, description="Existing trade to analyze")
    trade: Optional[TradeCreate] = Field(None, description="Unsaved trade scenario")


class PredictionResponse(BaseModel):
    trade_id: Optional[int]
    profitability_probability: float
    risk_score: float
    pattern_cluster: int
    confidence_score: float
    recommendations: List[str]
    feature_snapshot: Dict[str, Any]
    model_version: str


class ModelMetric(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float


class ModelPerformanceResponse(BaseModel):
    model_version: str
    trained_at: datetime
    training_rows: int
    data_source: str
    profitability_model: ModelMetric
    risk_model: ModelMetric
    cluster_distribution: Dict[str, int]


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    model_version: str
    top_features: List[FeatureImportanceItem]


class RetrainResponse(BaseModel):
    message: str
    performance: ModelPerformanceResponse
