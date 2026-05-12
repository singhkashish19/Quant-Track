"""Journal and NLP schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.database.models import EmotionalState


class JournalCreate(BaseModel):
    trade_id: Optional[int] = Field(None, description="Optional linked trade")
    notes: str = Field(..., min_length=3, description="Trading journal text")
    emotional_state: Optional[EmotionalState] = Field(None, description="Self-reported emotion")


class JournalResponse(BaseModel):
    id: int
    trade_id: Optional[int]
    notes: str
    emotional_state: Optional[EmotionalState]
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, obj):
        return cls.model_validate(obj)


class NLPAnalysisResponse(BaseModel):
    journal_id: int
    sentiment_score: float
    detected_emotions: Dict[str, float]
    fomo_score: float
    revenge_trade_score: float
    impulsive_score: float
    fear_greed_pattern: Optional[str]
    extracted_keywords: List[str]
    behavior_tags: List[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, obj):
        return cls.model_validate(obj)


class JournalWithAnalysisResponse(BaseModel):
    journal: JournalResponse
    analysis: NLPAnalysisResponse


class JournalSummaryResponse(BaseModel):
    total_journals: int
    average_sentiment: float
    fomo_events: int
    revenge_events: int
    impulsive_events: int
    dominant_behavior: Optional[str]
    risk_warnings: List[str]
