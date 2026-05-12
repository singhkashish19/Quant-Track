"""Portfolio and behavioral analytics calculations."""

from collections import defaultdict
from math import sqrt
from statistics import mean, pstdev
from typing import Iterable, List

from sqlalchemy.orm import Session

from app.analytics.schemas import (
    AnalyticsDashboardResponse,
    AnalyticsSummaryResponse,
    BreakdownItem,
    DrawdownPoint,
    EquityPoint,
)
from app.database.models import Trade


class AnalyticsService:
    """Computes analytics directly from a user's closed trade history."""

    @staticmethod
    def get_dashboard(user_id: int, db: Session) -> AnalyticsDashboardResponse:
        trades = (
            db.query(Trade)
            .filter(Trade.user_id == user_id)
            .order_by(Trade.exit_timestamp.asc().nullslast(), Trade.entry_timestamp.asc())
            .all()
        )
        closed_trades = [trade for trade in trades if trade.pnl is not None]

        equity_curve = AnalyticsService._equity_curve(closed_trades)
        drawdown_curve = AnalyticsService._drawdown_curve(equity_curve)
        strategy_breakdown = AnalyticsService._breakdown(closed_trades, "strategy")
        session_breakdown = AnalyticsService._breakdown(closed_trades, "session")
        emotional_breakdown = AnalyticsService._breakdown(closed_trades, "emotional_state")

        summary = AnalyticsService._summary(
            all_trades=trades,
            closed_trades=closed_trades,
            drawdown_curve=drawdown_curve,
            strategy_breakdown=strategy_breakdown,
        )

        return AnalyticsDashboardResponse(
            summary=summary,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            strategy_breakdown=strategy_breakdown,
            session_breakdown=session_breakdown,
            emotional_breakdown=emotional_breakdown,
        )

    @staticmethod
    def _summary(
        all_trades: List[Trade],
        closed_trades: List[Trade],
        drawdown_curve: List[DrawdownPoint],
        strategy_breakdown: List[BreakdownItem],
    ) -> AnalyticsSummaryResponse:
        if not closed_trades:
            return AnalyticsSummaryResponse(
                total_trades=len(all_trades),
                behavioral_flags=AnalyticsService._behavioral_flags(all_trades),
            )

        wins = [trade for trade in closed_trades if trade.pnl and trade.pnl > 0]
        losses = [trade for trade in closed_trades if trade.pnl and trade.pnl < 0]
        gross_profit = sum(trade.pnl for trade in wins)
        gross_loss = abs(sum(trade.pnl for trade in losses))
        win_rate = len(wins) / len(closed_trades) * 100
        loss_rate = len(losses) / len(closed_trades) * 100
        avg_win = mean([trade.pnl for trade in wins]) if wins else 0.0
        avg_loss = abs(mean([trade.pnl for trade in losses])) if losses else 0.0
        expectancy = (win_rate / 100 * avg_win) - (loss_rate / 100 * avg_loss)
        returns = [trade.pnl_percentage for trade in closed_trades if trade.pnl_percentage is not None]
        sharpe = None
        if len(returns) > 1 and pstdev(returns) > 0:
            sharpe = mean(returns) / pstdev(returns) * sqrt(len(returns))

        sorted_setups = sorted(strategy_breakdown, key=lambda item: item.total_pnl)
        max_drawdown_point = min(drawdown_curve, key=lambda point: point.drawdown, default=None)

        return AnalyticsSummaryResponse(
            total_trades=len(all_trades),
            closed_trades=len(closed_trades),
            win_rate=round(win_rate, 2),
            loss_rate=round(loss_rate, 2),
            profit_factor=round(gross_profit / gross_loss, 2) if gross_loss else round(gross_profit, 2),
            expectancy=round(expectancy, 2),
            average_rr=round(
                mean([trade.risk_reward_ratio for trade in closed_trades if trade.risk_reward_ratio is not None]),
                2,
            )
            if any(trade.risk_reward_ratio is not None for trade in closed_trades)
            else 0.0,
            max_drawdown=round(max_drawdown_point.drawdown, 2) if max_drawdown_point else 0.0,
            max_drawdown_pct=round(max_drawdown_point.drawdown_pct, 2) if max_drawdown_point else 0.0,
            sharpe_ratio=round(sharpe, 2) if sharpe is not None else None,
            best_setup=sorted_setups[-1].key if sorted_setups else None,
            worst_setup=sorted_setups[0].key if sorted_setups else None,
            behavioral_flags=AnalyticsService._behavioral_flags(all_trades),
        )

    @staticmethod
    def _equity_curve(trades: Iterable[Trade]) -> List[EquityPoint]:
        cumulative = 0.0
        points: List[EquityPoint] = []
        for trade in trades:
            cumulative += trade.pnl or 0.0
            points.append(
                EquityPoint(
                    timestamp=trade.exit_timestamp or trade.entry_timestamp,
                    cumulative_pnl=round(cumulative, 2),
                    trade_pnl=round(trade.pnl or 0.0, 2),
                    trade_id=trade.id,
                )
            )
        return points

    @staticmethod
    def _drawdown_curve(equity_curve: List[EquityPoint]) -> List[DrawdownPoint]:
        peak = 0.0
        points: List[DrawdownPoint] = []
        for point in equity_curve:
            peak = max(peak, point.cumulative_pnl)
            drawdown = point.cumulative_pnl - peak
            drawdown_pct = (drawdown / peak * 100) if peak else 0.0
            points.append(
                DrawdownPoint(
                    timestamp=point.timestamp,
                    equity=point.cumulative_pnl,
                    peak=round(peak, 2),
                    drawdown=round(drawdown, 2),
                    drawdown_pct=round(drawdown_pct, 2),
                )
            )
        return points

    @staticmethod
    def _breakdown(trades: Iterable[Trade], attribute: str) -> List[BreakdownItem]:
        buckets = defaultdict(list)
        for trade in trades:
            value = getattr(trade, attribute)
            if hasattr(value, "value"):
                value = value.value
            buckets[value or "Unspecified"].append(trade)

        return sorted(
            [AnalyticsService._breakdown_item(str(key), bucket) for key, bucket in buckets.items()],
            key=lambda item: item.total_pnl,
            reverse=True,
        )

    @staticmethod
    def _breakdown_item(key: str, trades: List[Trade]) -> BreakdownItem:
        wins = [trade for trade in trades if trade.pnl and trade.pnl > 0]
        losses = [trade for trade in trades if trade.pnl and trade.pnl < 0]
        total_pnl = sum(trade.pnl or 0.0 for trade in trades)
        gross_profit = sum(trade.pnl for trade in wins)
        gross_loss = abs(sum(trade.pnl for trade in losses))
        return BreakdownItem(
            key=key,
            trades=len(trades),
            win_rate=round(len(wins) / len(trades) * 100, 2) if trades else 0.0,
            total_pnl=round(total_pnl, 2),
            average_pnl=round(total_pnl / len(trades), 2) if trades else 0.0,
            profit_factor=round(gross_profit / gross_loss, 2) if gross_loss else round(gross_profit, 2),
        )

    @staticmethod
    def _behavioral_flags(trades: Iterable[Trade]) -> dict:
        trades = list(trades)
        return {
            "overtrading": sum(1 for trade in trades if trade.overtrading_flag),
            "revenge_trading": sum(1 for trade in trades if trade.revenge_trade_flag),
            "emotional_trades": sum(1 for trade in trades if trade.emotional_state is not None),
        }
