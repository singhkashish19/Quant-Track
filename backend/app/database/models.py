"""
SQLAlchemy Database Models

Defines the ORM models for all database tables:
- User
- Trade
- Journal
- MLPrediction
- AnalyticsSummary
- NLPAnalysis
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    JSON,
    Enum,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum as PyEnum

# Base class for all models
Base = declarative_base()


# ==================== ENUMS ====================

class TradeDirection(str, PyEnum):
    """Trade direction. BUY/SELL are kept for CSV imports, LONG/SHORT for UI aliases."""
    LONG = "LONG"
    SHORT = "SHORT"
    BUY = "BUY"
    SELL = "SELL"


class AssetType(str, PyEnum):
    """Supported asset classes for the hybrid dataset strategy."""
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    INDICES = "INDICES"
    COMMODITIES = "COMMODITIES"
    EQUITIES = "EQUITIES"


class TradeSession(str, PyEnum):
    """Trading session: NYSE, NSE, CRYPTO"""
    NYSE = "NYSE"
    NSE = "NSE"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"


class EmotionalState(str, PyEnum):
    """Emotional state during trade"""
    CALM = "CALM"
    CONFIDENT = "CONFIDENT"
    ANXIOUS = "ANXIOUS"
    FEARFUL = "FEARFUL"
    GREEDY = "GREEDY"
    FRUSTRATED = "FRUSTRATED"
    FOMO = "FOMO"
    DISCIPLINED = "DISCIPLINED"
    IMPULSIVE = "IMPULSIVE"
    REVENGE = "REVENGE"
    OVERCONFIDENT = "OVERCONFIDENT"
    HESITANT = "HESITANT"


class TradeResult(str, PyEnum):
    """Closed-trade outcome label."""
    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"


class PeriodType(str, PyEnum):
    """Analytics period type"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


# ==================== MODELS ====================

class User(Base):
    """
    User Model
    
    Attributes:
        id: Unique user identifier
        email: User email (unique)
        name: User full name
        hashed_password: Bcrypt hashed password
        is_active: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    subscription_tier = Column(String(50), default="free")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    journals = relationship("Journal", back_populates="user", cascade="all, delete-orphan")
    ml_predictions = relationship("MLPrediction", back_populates="user", cascade="all, delete-orphan")
    analytics_summaries = relationship("AnalyticsSummary", back_populates="user", cascade="all, delete-orphan")
    nlp_analyses = relationship("NLPAnalysis", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_is_active", "is_active"),
    )


class Trade(Base):
    """
    Trade Model
    
    Represents a single trade with entry/exit prices, strategy, and metadata.
    
    Attributes:
        id: Unique trade identifier
        user_id: Foreign key to user
        symbol: Trading symbol (e.g., AAPL, BTC/USD)
        direction: LONG or SHORT
        entry_price: Price at entry
        exit_price: Price at exit (can be null for open trades)
        stop_loss: Stop loss price
        take_profit: Take profit price
        lot_size: Quantity traded
        pnl: Profit/Loss in currency
        pnl_percentage: Profit/Loss percentage
        risk_reward_ratio: RR ratio of the trade
        strategy: Strategy name used
        timeframe: Timeframe (5M, 15M, 1H, 4H, 1D)
        session: Trading session (NYSE, NSE, CRYPTO)
        emotional_state: Emotional state during trade
        entry_timestamp: Trade entry time
        exit_timestamp: Trade exit time
        notes: Additional notes
        created_at: Record creation time
        updated_at: Last update time
    """
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(Enum(AssetType), nullable=True, index=True)
    direction = Column(Enum(TradeDirection), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    lot_size = Column(Float, nullable=False)
    
    pnl = Column(Float, nullable=True)
    pnl_percentage = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)
    result = Column(Enum(TradeResult), nullable=True, index=True)
    
    strategy = Column(String(100), nullable=True, index=True)
    timeframe = Column(String(10), nullable=True)
    market_condition = Column(String(50), nullable=True, index=True)
    session = Column(Enum(TradeSession), nullable=False, default=TradeSession.NYSE)
    emotional_state = Column(Enum(EmotionalState), nullable=True)
    confidence_level = Column(Integer, nullable=True)
    execution_quality = Column(String(50), nullable=True)
    slippage = Column(Float, nullable=True)
    trade_duration = Column(Float, nullable=True)
    overtrading_flag = Column(Boolean, default=False, index=True)
    revenge_trade_flag = Column(Boolean, default=False, index=True)
    
    entry_timestamp = Column(DateTime, nullable=False, index=True)
    exit_timestamp = Column(DateTime, nullable=True, index=True)
    
    notes = Column(Text, nullable=True)
    is_open = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    journal = relationship("Journal", back_populates="trade", uselist=False, cascade="all, delete-orphan")
    ml_predictions = relationship("MLPrediction", back_populates="trade", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_trade_user_date", "user_id", "entry_timestamp"),
        Index("idx_trade_symbol_date", "symbol", "entry_timestamp"),
        Index("idx_trade_strategy", "strategy"),
        Index("idx_trade_behavior", "emotional_state", "overtrading_flag", "revenge_trade_flag"),
    )


class Journal(Base):
    """
    Trading Journal Model
    
    Stores user notes and emotional state about trades.
    Links to a specific trade or can be standalone.
    
    Attributes:
        id: Unique journal entry identifier
        trade_id: Foreign key to trade (optional)
        user_id: Foreign key to user
        notes: Journal text content
        emotional_state: User's emotional state
        created_at: Entry creation time
        updated_at: Last update time
    """
    __tablename__ = "journals"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    notes = Column(Text, nullable=False)
    emotional_state = Column(Enum(EmotionalState), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="journals")
    trade = relationship("Trade", back_populates="journal")
    nlp_analysis = relationship("NLPAnalysis", back_populates="journal", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_journal_user_date", "user_id", "created_at"),
        Index("idx_journal_trade_id", "trade_id"),
    )


class MLPrediction(Base):
    """
    ML Prediction Model
    
    Stores ML model predictions for trades.
    
    Attributes:
        id: Unique prediction identifier
        trade_id: Foreign key to trade
        user_id: Foreign key to user
        model_name: Name of ML model used
        prediction_type: Type of prediction (profitability, risk, etc.)
        prediction_value: Predicted value
        confidence_score: Model's confidence (0-1)
        features_used: JSON of features used
        created_at: Prediction timestamp
    """
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    model_name = Column(String(100), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # profitability, risk, pattern
    prediction_value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    features_used = Column(JSON, nullable=True)  # Store used features for debugging
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="ml_predictions")
    trade = relationship("Trade", back_populates="ml_predictions")
    
    __table_args__ = (
        Index("idx_prediction_user_trade", "user_id", "trade_id"),
        Index("idx_prediction_model", "model_name"),
    )


class AnalyticsSummary(Base):
    """
    Analytics Summary Model
    
    Pre-calculated analytics metrics for performance optimization.
    
    Attributes:
        id: Unique summary identifier
        user_id: Foreign key to user
        period: Time period (DAILY, WEEKLY, MONTHLY)
        metrics_json: JSON containing all metrics
        generated_at: When metrics were calculated
    """
    __tablename__ = "analytics_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    period = Column(Enum(PeriodType), nullable=False)
    period_date = Column(DateTime, nullable=False, index=True)
    
    # Store all metrics as JSON for flexibility
    metrics_json = Column(JSON, nullable=False)
    
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analytics_summaries")
    
    __table_args__ = (
        Index("idx_analytics_user_period", "user_id", "period", "period_date"),
    )


class NLPAnalysis(Base):
    """
    NLP Analysis Model
    
    Stores results of NLP analysis on journal entries.
    
    Attributes:
        id: Unique analysis identifier
        journal_id: Foreign key to journal
        user_id: Foreign key to user
        sentiment_score: Sentiment polarity (-1 to 1)
        detected_emotions: JSON of detected emotions
        fomo_score: Likelihood of FOMO behavior (0-1)
        revenge_trade_score: Likelihood of revenge trading (0-1)
        impulsive_score: Impulsiveness level (0-1)
        fear_greed_pattern: Detected pattern (fear/greed/neutral)
        extracted_keywords: JSON of important keywords
        behavior_tags: JSON of behavioral flags
        created_at: Analysis timestamp
    """
    __tablename__ = "nlp_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    sentiment_score = Column(Float, nullable=False)  # -1 to 1
    detected_emotions = Column(JSON, nullable=True)
    
    fomo_score = Column(Float, default=0.0)
    revenge_trade_score = Column(Float, default=0.0)
    impulsive_score = Column(Float, default=0.0)
    fear_greed_pattern = Column(String(50), nullable=True)
    
    extracted_keywords = Column(JSON, nullable=True)
    behavior_tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="nlp_analyses")
    journal = relationship("Journal", back_populates="nlp_analysis")
    
    __table_args__ = (
        Index("idx_nlp_user_date", "user_id", "created_at"),
        Index("idx_nlp_journal_id", "journal_id"),
    )
