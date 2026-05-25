"""
Trade Schemas (Pydantic models)

Request and response schemas for trade management endpoints.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.database.models import (
    AssetType,
    EmotionalState,
    TradeDirection,
    TradeResult,
    TradeSession,
)


# ==================== REQUEST SCHEMAS ====================

class TradeCreate(BaseModel):
    """Create trade request schema"""
    
    symbol: str = Field(..., min_length=1, max_length=20, description="Trading symbol (e.g., AAPL)")
    asset_type: Optional[AssetType] = Field(None, description="Asset class")
    direction: TradeDirection = Field(..., description="LONG or SHORT")
    entry_price: float = Field(..., gt=0, description="Entry price")
    exit_price: Optional[float] = Field(None, gt=0, description="Exit price (null for open trades)")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    lot_size: float = Field(..., gt=0, description="Quantity traded")
    strategy: Optional[str] = Field(None, max_length=100, description="Strategy name")
    timeframe: Optional[str] = Field(None, max_length=10, description="Timeframe (5M, 15M, 1H, etc.)")
    market_condition: Optional[str] = Field(None, max_length=50, description="Trending, ranging, volatile, etc.")
    session: TradeSession = Field(default=TradeSession.NYSE, description="Trading session")
    emotional_state: Optional[EmotionalState] = Field(None, description="Emotional state during trade")
    confidence_level: Optional[int] = Field(None, ge=1, le=10, description="Trader confidence from 1 to 10")
    execution_quality: Optional[str] = Field(None, max_length=50, description="Execution quality label")
    slippage: Optional[float] = Field(None, description="Execution slippage")
    trade_duration: Optional[float] = Field(None, ge=0, description="Trade duration in minutes")
    overtrading_flag: bool = Field(False, description="Whether trade belongs to an overtrading pattern")
    revenge_trade_flag: bool = Field(False, description="Whether trade was a revenge trade")
    entry_timestamp: datetime = Field(..., description="Entry time")
    exit_timestamp: Optional[datetime] = Field(None, description="Exit time")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "asset_type": "EQUITIES",
                "direction": "LONG",
                "entry_price": 150.25,
                "exit_price": 152.75,
                "stop_loss": 149.00,
                "take_profit": 155.00,
                "lot_size": 100,
                "strategy": "Breakout",
                "timeframe": "1H",
                "market_condition": "trending",
                "session": "NYSE",
                "emotional_state": "CONFIDENT",
                "entry_timestamp": "2024-01-15T09:30:00",
                "exit_timestamp": "2024-01-15T11:00:00",
                "notes": "Broke above resistance at 150",
            }
        }


class TradeUpdate(BaseModel):
    """Update trade request schema"""
    
    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    asset_type: Optional[AssetType] = Field(None)
    direction: Optional[TradeDirection] = Field(None)
    entry_price: Optional[float] = Field(None, gt=0)
    exit_price: Optional[float] = Field(None, gt=0)
    stop_loss: Optional[float] = Field(None, gt=0)
    take_profit: Optional[float] = Field(None, gt=0)
    lot_size: Optional[float] = Field(None, gt=0)
    strategy: Optional[str] = Field(None, max_length=100)
    timeframe: Optional[str] = Field(None, max_length=10)
    market_condition: Optional[str] = Field(None, max_length=50)
    session: Optional[TradeSession] = Field(None)
    emotional_state: Optional[EmotionalState] = Field(None)
    confidence_level: Optional[int] = Field(None, ge=1, le=10)
    execution_quality: Optional[str] = Field(None, max_length=50)
    slippage: Optional[float] = Field(None)
    trade_duration: Optional[float] = Field(None, ge=0)
    overtrading_flag: Optional[bool] = Field(None)
    revenge_trade_flag: Optional[bool] = Field(None)
    entry_timestamp: Optional[datetime] = Field(None)
    exit_timestamp: Optional[datetime] = Field(None)
    notes: Optional[str] = Field(None, max_length=1000)


class TradeFilter(BaseModel):
    """Trade filtering parameters"""
    
    symbol: Optional[str] = None
    strategy: Optional[str] = None
    session: Optional[TradeSession] = None
    asset_type: Optional[AssetType] = None
    result: Optional[TradeResult] = None
    direction: Optional[TradeDirection] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_pnl: Optional[float] = None
    max_pnl: Optional[float] = None
    is_open: Optional[bool] = None


# ==================== RESPONSE SCHEMAS ====================

class TradeResponse(BaseModel):
    """Trade response schema"""
    
    id: int = Field(..., description="Trade ID")
    symbol: str = Field(..., description="Trading symbol")
    asset_type: Optional[AssetType] = Field(None, description="Asset class")
    direction: TradeDirection = Field(..., description="LONG or SHORT")
    entry_price: float = Field(..., description="Entry price")
    exit_price: Optional[float] = Field(None, description="Exit price")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    lot_size: float = Field(..., description="Lot size")
    pnl: Optional[float] = Field(None, description="Profit/Loss")
    pnl_percentage: Optional[float] = Field(None, description="P&L percentage")
    risk_reward_ratio: Optional[float] = Field(None, description="RR ratio")
    result: Optional[TradeResult] = Field(None, description="WIN/LOSS/BREAKEVEN")
    strategy: Optional[str] = Field(None, description="Strategy name")
    timeframe: Optional[str] = Field(None, description="Timeframe")
    market_condition: Optional[str] = Field(None, description="Market regime")
    session: TradeSession = Field(..., description="Trading session")
    emotional_state: Optional[EmotionalState] = Field(None, description="Emotional state")
    confidence_level: Optional[int] = Field(None, description="Confidence 1-10")
    execution_quality: Optional[str] = Field(None, description="Execution quality")
    slippage: Optional[float] = Field(None, description="Execution slippage")
    trade_duration: Optional[float] = Field(None, description="Trade duration in minutes")
    overtrading_flag: bool = Field(False, description="Overtrading flag")
    revenge_trade_flag: bool = Field(False, description="Revenge trade flag")
    entry_timestamp: datetime = Field(..., description="Entry time")
    exit_timestamp: Optional[datetime] = Field(None, description="Exit time")
    is_open: bool = Field(..., description="Is trade still open")
    notes: Optional[str] = Field(None, description="Notes")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")
    
    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, obj):
        return cls.model_validate(obj)


class TradeListResponse(BaseModel):
    """Paginated trade list response"""
    
    trades: List[TradeResponse] = Field(..., description="List of trades")
    total: int = Field(..., description="Total number of trades")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")


class TradeStatisticsResponse(BaseModel):
    """Trade statistics response"""
    
    total_trades: int = Field(..., description="Total number of trades")
    winning_trades: int = Field(..., description="Number of winning trades")
    losing_trades: int = Field(..., description="Number of losing trades")
    win_rate: float = Field(..., description="Win rate percentage")
    total_pnl: float = Field(..., description="Total P&L")
    average_pnl: float = Field(..., description="Average P&L per trade")
    largest_win: float = Field(..., description="Largest win")
    largest_loss: float = Field(..., description="Largest loss")
    open_trades: int = Field(..., description="Number of open trades")
    profit_factor: float = Field(0.0, description="Gross profit divided by gross loss")
