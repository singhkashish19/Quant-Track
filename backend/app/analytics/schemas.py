"""Analytics response schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EquityPoint(BaseModel):
    timestamp: datetime
    cumulative_pnl: float
    trade_pnl: float
    trade_id: int


class DrawdownPoint(BaseModel):
    timestamp: datetime
    equity: float
    peak: float
    drawdown: float
    drawdown_pct: float


class BreakdownItem(BaseModel):
    key: str
    trades: int
    win_rate: float
    total_pnl: float
    average_pnl: float
    profit_factor: float


class AnalyticsSummaryResponse(BaseModel):
    total_trades: int = 0
    closed_trades: int = 0
    win_rate: float = 0.0
    loss_rate: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    average_rr: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: Optional[float] = None
    best_setup: Optional[str] = None
    worst_setup: Optional[str] = None
    behavioral_flags: Dict[str, int] = Field(default_factory=dict)


class AnalyticsDashboardResponse(BaseModel):
    summary: AnalyticsSummaryResponse
    equity_curve: List[EquityPoint]
    drawdown_curve: List[DrawdownPoint]
    strategy_breakdown: List[BreakdownItem]
    session_breakdown: List[BreakdownItem]
    emotional_breakdown: List[BreakdownItem]
