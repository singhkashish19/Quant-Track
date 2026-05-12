"""Generate QuantTrack synthetic datasets.

This script creates the three datasets used by the platform:
trades.csv, journals.csv, and engineered_features.csv.
"""

from __future__ import annotations

import csv
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent
SYMBOLS = {
    "XAUUSD": "COMMODITIES",
    "BTCUSD": "CRYPTO",
    "EURUSD": "FOREX",
    "NAS100": "INDICES",
    "US30": "INDICES",
}
STRATEGIES = ["breakout", "reversal", "scalping", "trend_following", "mean_reversion"]
TIMEFRAMES = ["5M", "15M", "1H", "4H"]
SESSIONS = ["FOREX", "NYSE", "CRYPTO"]
MARKET_CONDITIONS = ["trending", "ranging", "volatile", "news_driven"]
EMOTIONS = ["DISCIPLINED", "FOMO", "FEARFUL", "GREEDY", "IMPULSIVE", "REVENGE", "CONFIDENT"]
JOURNAL_TEMPLATES = {
    "DISCIPLINED": ("Followed my setup rules perfectly.", "discipline", "rule_based_execution"),
    "FOMO": ("Entered too early because price moved aggressively.", "FOMO", "impulsive_entry"),
    "REVENGE": ("Re-entered immediately after previous loss.", "revenge_trading", "emotional_reentry"),
    "IMPULSIVE": ("Ignored confirmation and forced the trade.", "impulsive", "rule_violation"),
    "FEARFUL": ("Closed early because I felt scared of giving back profit.", "fear", "premature_exit"),
    "GREEDY": ("Held too long because I wanted a bigger move.", "greed", "poor_exit_discipline"),
    "CONFIDENT": ("Executed the planned setup with confidence.", "discipline", "planned_execution"),
}


def main(rows: int = 250, seed: int = 42) -> None:
    random.seed(seed)
    trades = build_trades(rows)
    journals = build_journals(trades)
    features = build_engineered_features(trades)

    write_csv(OUTPUT_DIR / "trades.csv", trades)
    write_csv(OUTPUT_DIR / "journals.csv", journals)
    write_csv(OUTPUT_DIR / "engineered_features.csv", features)
    print(f"Generated {len(trades)} trades, {len(journals)} journals, {len(features)} feature rows.")


def build_trades(rows: int) -> list[dict]:
    trades = []
    start = datetime.now(UTC) - timedelta(days=180)
    last_loss = False

    for idx in range(1, rows + 1):
        symbol, asset_type = random.choice(list(SYMBOLS.items()))
        direction = random.choice(["BUY", "SELL"])
        strategy = random.choice(STRATEGIES)
        emotion = random.choices(EMOTIONS, weights=[32, 12, 10, 10, 9, 7, 20])[0]
        entry = base_price(symbol) * random.uniform(0.96, 1.04)
        stop_distance = entry * random.uniform(0.002, 0.015)
        rr_ratio = round(random.uniform(0.7, 3.2), 2)
        is_win = random.random() < win_probability(strategy, emotion)
        pnl_direction = 1 if is_win else -1
        price_delta = stop_distance * (rr_ratio if is_win else random.uniform(0.6, 1.2))
        exit_price = entry + price_delta * pnl_direction if direction == "BUY" else entry - price_delta * pnl_direction
        lot_size = round(random.uniform(0.1, 3.0), 2)
        pnl = (exit_price - entry) * lot_size if direction == "BUY" else (entry - exit_price) * lot_size
        timestamp = start + timedelta(hours=idx * random.uniform(3, 10))
        revenge = last_loss and emotion == "REVENGE"
        overtrading = random.random() < (0.18 if emotion in {"FOMO", "IMPULSIVE", "REVENGE"} else 0.05)
        last_loss = pnl < 0

        trades.append(
            {
                "trade_id": idx,
                "user_id": 1,
                "symbol": symbol,
                "asset_type": asset_type,
                "direction": direction,
                "entry_price": round(entry, 4),
                "exit_price": round(exit_price, 4),
                "stop_loss": round(entry - stop_distance if direction == "BUY" else entry + stop_distance, 4),
                "take_profit": round(entry + stop_distance * rr_ratio if direction == "BUY" else entry - stop_distance * rr_ratio, 4),
                "lot_size": lot_size,
                "pnl": round(pnl, 2),
                "rr_ratio": rr_ratio,
                "strategy": strategy,
                "timeframe": random.choice(TIMEFRAMES),
                "market_condition": random.choice(MARKET_CONDITIONS),
                "session": random.choice(SESSIONS),
                "trade_duration": random.randint(8, 420),
                "execution_quality": random.choice(["excellent", "good", "late", "early", "poor"]),
                "slippage": round(random.uniform(0, 0.8), 3),
                "timestamp": timestamp.isoformat(timespec="seconds"),
                "result": "WIN" if pnl > 0 else "LOSS",
                "emotional_state": emotion,
                "confidence_level": random.randint(3, 10),
                "overtrading_flag": overtrading,
                "revenge_trade_flag": revenge,
            }
        )

    return trades


def build_journals(trades: list[dict]) -> list[dict]:
    journals = []
    for trade in trades:
        text, emotion_label, tag = JOURNAL_TEMPLATES[trade["emotional_state"]]
        journals.append(
            {
                "journal_id": trade["trade_id"],
                "trade_id": trade["trade_id"],
                "journal_text": text,
                "emotion_label": emotion_label,
                "sentiment_score": sentiment_for(emotion_label),
                "behavioral_tag": tag,
                "confidence_score": round(random.uniform(0.62, 0.96), 2),
                "created_at": trade["timestamp"],
            }
        )
    return journals


def build_engineered_features(trades: list[dict]) -> list[dict]:
    features = []
    losses = 0
    for index, trade in enumerate(trades):
        window = trades[max(0, index - 9) : index + 1]
        pnls = [row["pnl"] for row in window]
        wins = [row for row in window if row["result"] == "WIN"]
        losses = losses + 1 if trade["result"] == "LOSS" else 0
        features.append(
            {
                "trade_id": trade["trade_id"],
                "average_rr_last_10": round(sum(row["rr_ratio"] for row in window) / len(window), 2),
                "rolling_winrate": round(len(wins) / len(window), 3),
                "pnl_consistency": round(1 / (1 + variance(pnls)), 4),
                "consecutive_losses": losses,
                "revenge_trade_frequency": rolling_rate(window, "revenge_trade_flag"),
                "overtrading_score": rolling_rate(window, "overtrading_flag"),
                "emotional_volatility": emotional_volatility(window),
                "strategy_winrate": strategy_winrate(trades[: index + 1], trade["strategy"]),
                "avg_risk_per_trade": round(abs(trade["entry_price"] - trade["stop_loss"]) * trade["lot_size"], 2),
                "profitable_trade": 1 if trade["result"] == "WIN" else 0,
                "high_risk_trader": 1 if trade["overtrading_flag"] or trade["revenge_trade_flag"] or losses >= 3 else 0,
            }
        )
    return features


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def base_price(symbol: str) -> float:
    return {"XAUUSD": 2350, "BTCUSD": 68000, "EURUSD": 1.08, "NAS100": 18000, "US30": 39000}[symbol]


def win_probability(strategy: str, emotion: str) -> float:
    base = {"breakout": 0.52, "reversal": 0.48, "scalping": 0.46, "trend_following": 0.56, "mean_reversion": 0.5}[strategy]
    adjustment = {"DISCIPLINED": 0.12, "CONFIDENT": 0.06, "FOMO": -0.12, "REVENGE": -0.18, "IMPULSIVE": -0.15}.get(emotion, -0.04)
    return min(max(base + adjustment, 0.18), 0.78)


def sentiment_for(label: str) -> float:
    return {"discipline": 0.55, "FOMO": -0.2, "revenge_trading": -0.65, "impulsive": -0.45, "fear": -0.55, "greed": -0.25}.get(label, 0.2)


def variance(values: list[float]) -> float:
    avg = sum(values) / len(values)
    return sum((value - avg) ** 2 for value in values) / len(values)


def rolling_rate(rows: list[dict], key: str) -> float:
    return round(sum(1 for row in rows if row[key]) / len(rows), 3)


def emotional_volatility(rows: list[dict]) -> float:
    return round(len({row["emotional_state"] for row in rows}) / max(len(rows), 1), 3)


def strategy_winrate(rows: list[dict], strategy: str) -> float:
    strategy_rows = [row for row in rows if row["strategy"] == strategy]
    wins = [row for row in strategy_rows if row["result"] == "WIN"]
    return round(len(wins) / len(strategy_rows), 3) if strategy_rows else 0.0


if __name__ == "__main__":
    main()
