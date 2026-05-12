"""
Trade Service

Business logic for trade management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional, Tuple
from app.database.models import Trade, TradeDirection, TradeResult
from app.trades.schemas import TradeCreate, TradeUpdate, TradeStatisticsResponse


class TradeService:
    """Service for trade management operations"""
    
    @staticmethod
    def create_trade(trade_data: TradeCreate, user_id: int, db: Session) -> Trade:
        """
        Create a new trade.
        
        Args:
            trade_data: Trade creation data
            user_id: User ID
            db: Database session
            
        Returns:
            Trade: Created trade object
        """
        # Calculate PnL if trade is closed
        pnl = None
        pnl_percentage = None
        risk_reward_ratio = None
        
        if trade_data.exit_price is not None:
            if trade_data.direction in (TradeDirection.LONG, TradeDirection.BUY):
                pnl = (trade_data.exit_price - trade_data.entry_price) * trade_data.lot_size
                pnl_percentage = ((trade_data.exit_price - trade_data.entry_price) / trade_data.entry_price) * 100
            else:  # SHORT
                pnl = (trade_data.entry_price - trade_data.exit_price) * trade_data.lot_size
                pnl_percentage = ((trade_data.entry_price - trade_data.exit_price) / trade_data.entry_price) * 100
            
            # Calculate RR ratio
            if trade_data.stop_loss and trade_data.take_profit:
                if trade_data.direction in (TradeDirection.LONG, TradeDirection.BUY):
                    risk = trade_data.entry_price - trade_data.stop_loss
                    reward = trade_data.take_profit - trade_data.entry_price
                else:  # SHORT
                    risk = trade_data.stop_loss - trade_data.entry_price
                    reward = trade_data.entry_price - trade_data.take_profit
                
                if risk > 0:
                    risk_reward_ratio = reward / risk
        
        trade = Trade(
            user_id=user_id,
            symbol=trade_data.symbol,
            asset_type=trade_data.asset_type,
            direction=trade_data.direction,
            entry_price=trade_data.entry_price,
            exit_price=trade_data.exit_price,
            stop_loss=trade_data.stop_loss,
            take_profit=trade_data.take_profit,
            lot_size=trade_data.lot_size,
            pnl=pnl,
            pnl_percentage=pnl_percentage,
            risk_reward_ratio=risk_reward_ratio,
            result=TradeService._result_from_pnl(pnl),
            strategy=trade_data.strategy,
            timeframe=trade_data.timeframe,
            market_condition=trade_data.market_condition,
            session=trade_data.session,
            emotional_state=trade_data.emotional_state,
            confidence_level=trade_data.confidence_level,
            execution_quality=trade_data.execution_quality,
            slippage=trade_data.slippage,
            trade_duration=trade_data.trade_duration,
            overtrading_flag=trade_data.overtrading_flag,
            revenge_trade_flag=trade_data.revenge_trade_flag,
            entry_timestamp=trade_data.entry_timestamp,
            exit_timestamp=trade_data.exit_timestamp,
            notes=trade_data.notes,
            is_open=trade_data.exit_price is None,
        )
        
        db.add(trade)
        db.commit()
        db.refresh(trade)
        
        return trade
    
    @staticmethod
    def get_trade(trade_id: int, user_id: int, db: Session) -> Trade:
        """
        Get trade by ID (only if user owns it).
        
        Args:
            trade_id: Trade ID
            user_id: User ID
            db: Database session
            
        Returns:
            Trade: Trade object
            
        Raises:
            ValueError: If trade not found or user doesn't own it
        """
        trade = db.query(Trade).filter(
            and_(Trade.id == trade_id, Trade.user_id == user_id)
        ).first()
        
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        return trade
    
    @staticmethod
    def list_trades(
        user_id: int,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None,
        session: Optional[str] = None,
    ) -> Tuple[List[Trade], int]:
        """
        List user's trades with optional filtering.
        
        Args:
            user_id: User ID
            db: Database session
            skip: Number of trades to skip
            limit: Number of trades to return
            symbol: Filter by symbol
            strategy: Filter by strategy
            session: Filter by session
            
        Returns:
            tuple: (trades list, total count)
        """
        query = db.query(Trade).filter(Trade.user_id == user_id)
        
        if symbol:
            query = query.filter(Trade.symbol == symbol)
        if strategy:
            query = query.filter(Trade.strategy == strategy)
        if session:
            query = query.filter(Trade.session == session)
        
        total = query.count()
        
        trades = query.order_by(Trade.entry_timestamp.desc()).offset(skip).limit(limit).all()
        
        return trades, total
    
    @staticmethod
    def update_trade(
        trade_id: int,
        user_id: int,
        trade_data: TradeUpdate,
        db: Session,
    ) -> Trade:
        """
        Update a trade.
        
        Args:
            trade_id: Trade ID
            user_id: User ID
            trade_data: Update data
            db: Database session
            
        Returns:
            Trade: Updated trade object
        """
        trade = TradeService.get_trade(trade_id, user_id, db)
        
        # Update fields if provided
        update_data = trade_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(trade, field, value)
        
        # Recalculate PnL if needed
        if trade.exit_price:
            if trade.direction in (TradeDirection.LONG, TradeDirection.BUY):
                trade.pnl = (trade.exit_price - trade.entry_price) * trade.lot_size
                trade.pnl_percentage = ((trade.exit_price - trade.entry_price) / trade.entry_price) * 100
            else:
                trade.pnl = (trade.entry_price - trade.exit_price) * trade.lot_size
                trade.pnl_percentage = ((trade.entry_price - trade.exit_price) / trade.entry_price) * 100
            
            trade.is_open = False
            trade.result = TradeService._result_from_pnl(trade.pnl)
        
        db.commit()
        db.refresh(trade)
        
        return trade
    
    @staticmethod
    def delete_trade(trade_id: int, user_id: int, db: Session) -> None:
        """
        Delete a trade.
        
        Args:
            trade_id: Trade ID
            user_id: User ID
            db: Database session
        """
        trade = TradeService.get_trade(trade_id, user_id, db)
        db.delete(trade)
        db.commit()
    
    @staticmethod
    def get_trade_statistics(user_id: int, db: Session) -> TradeStatisticsResponse:
        """
        Calculate trade statistics for a user.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            TradeStatisticsResponse: Statistics
        """
        trades = db.query(Trade).filter(Trade.user_id == user_id).all()
        
        if not trades:
            return TradeStatisticsResponse(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                average_pnl=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                open_trades=0,
                profit_factor=0.0,
            )
        
        closed_trades = [t for t in trades if t.pnl is not None]
        open_trades = [t for t in trades if t.is_open]
        
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl < 0]
        
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0.0
        total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
        average_pnl = total_pnl / len(closed_trades) if closed_trades else 0.0
        
        largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0.0
        largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0.0
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss else (gross_profit if gross_profit else 0.0)
        
        return TradeStatisticsResponse(
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            total_pnl=total_pnl,
            average_pnl=average_pnl,
            largest_win=largest_win,
            largest_loss=largest_loss,
            open_trades=len(open_trades),
            profit_factor=profit_factor,
        )

    @staticmethod
    def _result_from_pnl(pnl: Optional[float]) -> Optional[TradeResult]:
        if pnl is None:
            return None
        if pnl > 0:
            return TradeResult.WIN
        if pnl < 0:
            return TradeResult.LOSS
        return TradeResult.BREAKEVEN
