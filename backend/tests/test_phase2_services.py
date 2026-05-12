from datetime import datetime
from types import SimpleNamespace

from app.database.models import AssetType, EmotionalState, TradeDirection, TradeSession
from app.ml.feature_engineering import FEATURE_COLUMNS, FeatureEngineeringService
from app.ml.service import MLService
from app.nlp.service import NLPService


def test_feature_engineering_creates_model_ready_row():
    trade = SimpleNamespace(
        symbol="XAUUSD",
        asset_type=AssetType.COMMODITIES,
        direction=TradeDirection.BUY,
        entry_price=2350,
        exit_price=2365,
        stop_loss=2340,
        take_profit=2370,
        lot_size=1.2,
        pnl=18,
        risk_reward_ratio=None,
        strategy="breakout",
        timeframe="15M",
        market_condition="trending",
        session=TradeSession.FOREX,
        emotional_state=EmotionalState.DISCIPLINED,
        confidence_level=8,
        execution_quality="good",
        slippage=0.1,
        trade_duration=35,
        revenge_trade_flag=False,
        overtrading_flag=False,
        entry_timestamp=datetime(2026, 1, 1, 10, 30),
    )

    row = FeatureEngineeringService.row_from_trade(trade)

    assert set(FEATURE_COLUMNS).issubset(row.keys())
    assert row["profitable_trade"] == 1
    assert row["rr_ratio"] == 2.0
    assert row["asset_type"] == "COMMODITIES"


def test_nlp_detects_revenge_trading():
    result = NLPService.analyze_text("Re-entered immediately after previous loss to win it back.")

    assert result["revenge_trade_score"] >= 0.34
    assert "revenge_trading" in result["behavior_tags"]
    assert result["sentiment_score"] <= 0


def test_demo_dataset_supports_ml_training_contract():
    rows = MLService._load_demo_rows()

    assert len(rows) >= 30
    assert set(FEATURE_COLUMNS).issubset(rows[0].keys())
    assert {row["profitable_trade"] for row in rows} == {0, 1}
