"""Feature engineering for trade profitability and behavioral-risk models."""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Any, Iterable, List, Optional

from sqlalchemy.orm import Session

from app.database.models import Trade, TradeDirection


NUMERIC_FEATURES = [
    "entry_price",
    "stop_loss_distance",
    "take_profit_distance",
    "lot_size",
    "rr_ratio",
    "trade_duration",
    "slippage",
    "confidence_level",
    "hour_of_day",
    "day_of_week",
    "average_rr_last_10",
    "rolling_winrate",
    "consecutive_losses",
    "revenge_trade_frequency",
    "overtrading_score",
    "emotional_volatility",
    "strategy_winrate",
    "avg_risk_per_trade",
]

CATEGORICAL_FEATURES = [
    "symbol",
    "asset_type",
    "direction",
    "strategy",
    "timeframe",
    "market_condition",
    "session",
    "emotional_state",
    "execution_quality",
]

TARGET_COLUMNS = ["profitable_trade", "high_risk_trader"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


class FeatureEngineeringService:
    """Builds model-ready rows from SQLAlchemy trades or request payloads."""

    @staticmethod
    def rows_for_user(user_id: int, db: Session) -> List[dict]:
        trades = (
            db.query(Trade)
            .filter(Trade.user_id == user_id, Trade.pnl.isnot(None))
            .order_by(Trade.entry_timestamp.asc())
            .all()
        )
        return FeatureEngineeringService.rows_from_trades(trades)

    @staticmethod
    def rows_from_trades(trades: Iterable[Trade]) -> List[dict]:
        rows = []
        history: List[dict] = []
        consecutive_losses = 0
        for trade in trades:
            row = FeatureEngineeringService.row_from_trade(trade, history, consecutive_losses)
            if trade.pnl is not None and trade.pnl < 0:
                consecutive_losses += 1
            else:
                consecutive_losses = 0
            rows.append(row)
            history.append(row)
        return rows

    @staticmethod
    def row_from_trade(trade: Any, history: Optional[List[dict]] = None, consecutive_losses: int = 0) -> dict:
        history = history or []
        timestamp = FeatureEngineeringService._get(trade, "entry_timestamp") or datetime.utcnow()
        entry_price = float(FeatureEngineeringService._get(trade, "entry_price") or 0.0)
        stop_loss = FeatureEngineeringService._get(trade, "stop_loss")
        take_profit = FeatureEngineeringService._get(trade, "take_profit")
        lot_size = float(FeatureEngineeringService._get(trade, "lot_size") or 0.0)
        pnl = FeatureEngineeringService._get(trade, "pnl")
        direction = FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "direction")) or "BUY"
        rr_ratio = FeatureEngineeringService._get(trade, "risk_reward_ratio")
        if rr_ratio is None:
            rr_ratio = FeatureEngineeringService._get(trade, "rr_ratio")
        if rr_ratio is None:
            rr_ratio = FeatureEngineeringService._rr_ratio(entry_price, stop_loss, take_profit, direction)

        risk_amount = FeatureEngineeringService._risk_amount(entry_price, stop_loss, lot_size)
        window = history[-10:]
        strategy = FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "strategy")) or "unknown"
        strategy_history = [row for row in history if row["strategy"] == strategy]

        row = {
            "entry_price": entry_price,
            "stop_loss_distance": FeatureEngineeringService._distance(entry_price, stop_loss),
            "take_profit_distance": FeatureEngineeringService._distance(entry_price, take_profit),
            "lot_size": lot_size,
            "rr_ratio": float(rr_ratio or 0.0),
            "trade_duration": float(FeatureEngineeringService._get(trade, "trade_duration") or 0.0),
            "slippage": float(FeatureEngineeringService._get(trade, "slippage") or 0.0),
            "confidence_level": float(FeatureEngineeringService._get(trade, "confidence_level") or 5.0),
            "hour_of_day": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "average_rr_last_10": round(mean([row["rr_ratio"] for row in window]), 3) if window else float(rr_ratio or 0.0),
            "rolling_winrate": round(sum(row.get("profitable_trade", 0) for row in window) / len(window), 3) if window else 0.5,
            "consecutive_losses": consecutive_losses,
            "revenge_trade_frequency": FeatureEngineeringService._rate(window, "revenge_trade_flag"),
            "overtrading_score": FeatureEngineeringService._rate(window, "overtrading_flag"),
            "emotional_volatility": round(len({row["emotional_state"] for row in window}) / len(window), 3) if window else 0.0,
            "strategy_winrate": round(sum(row.get("profitable_trade", 0) for row in strategy_history) / len(strategy_history), 3)
            if strategy_history
            else 0.5,
            "avg_risk_per_trade": risk_amount,
            "symbol": FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "symbol")) or "UNKNOWN",
            "asset_type": FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "asset_type")) or "UNKNOWN",
            "direction": "BUY" if direction == TradeDirection.LONG.value else "SELL" if direction == TradeDirection.SHORT.value else direction,
            "strategy": strategy,
            "timeframe": FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "timeframe")) or "unknown",
            "market_condition": FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "market_condition")) or "unknown",
            "session": FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "session")) or "unknown",
            "emotional_state": FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "emotional_state")) or "UNKNOWN",
            "execution_quality": FeatureEngineeringService._value(FeatureEngineeringService._get(trade, "execution_quality")) or "unknown",
            "revenge_trade_flag": bool(FeatureEngineeringService._get(trade, "revenge_trade_flag") or False),
            "overtrading_flag": bool(FeatureEngineeringService._get(trade, "overtrading_flag") or False),
        }

        if pnl is not None:
            row["profitable_trade"] = 1 if float(pnl) > 0 else 0
            row["high_risk_trader"] = 1 if row["revenge_trade_flag"] or row["overtrading_flag"] or consecutive_losses >= 3 else 0
        return row

    @staticmethod
    def _get(source: Any, field: str) -> Any:
        if isinstance(source, dict):
            return source.get(field)
        return getattr(source, field, None)

    @staticmethod
    def _value(value: Any) -> Any:
        return value.value if hasattr(value, "value") else value

    @staticmethod
    def _distance(entry_price: float, price: Optional[float]) -> float:
        if not price or not entry_price:
            return 0.0
        return round(abs(entry_price - float(price)) / entry_price, 5)

    @staticmethod
    def _risk_amount(entry_price: float, stop_loss: Optional[float], lot_size: float) -> float:
        if not stop_loss:
            return 0.0
        return round(abs(entry_price - float(stop_loss)) * lot_size, 3)

    @staticmethod
    def _rr_ratio(entry_price: float, stop_loss: Optional[float], take_profit: Optional[float], direction: str) -> float:
        if not entry_price or not stop_loss or not take_profit:
            return 0.0
        if direction in {"LONG", "BUY"}:
            risk = entry_price - float(stop_loss)
            reward = float(take_profit) - entry_price
        else:
            risk = float(stop_loss) - entry_price
            reward = entry_price - float(take_profit)
        return round(reward / risk, 3) if risk > 0 else 0.0

    @staticmethod
    def _rate(rows: List[dict], key: str) -> float:
        return round(sum(1 for row in rows if row.get(key)) / len(rows), 3) if rows else 0.0
