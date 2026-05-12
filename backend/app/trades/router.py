"""
Trade Routes (API Endpoints)

Endpoints for trade management:
- Create trade
- Get trades (list, single)
- Update trade
- Delete trade
- Get statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.models import User
from app.auth.dependencies import get_current_active_user
from app.trades.schemas import (
    TradeCreate,
    TradeUpdate,
    TradeResponse,
    TradeListResponse,
    TradeStatisticsResponse,
)
from app.trades.service import TradeService

router = APIRouter(prefix="/api/trades", tags=["Trades"])


@router.post(
    "",
    response_model=TradeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new trade",
)
async def create_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TradeResponse:
    """
    Create a new trade record.
    
    Parameters:
    - **symbol**: Trading symbol (e.g., AAPL, BTC/USD)
    - **direction**: LONG or SHORT
    - **entry_price**: Entry price
    - **exit_price**: Exit price (optional for open trades)
    - **lot_size**: Quantity traded
    - **strategy**: Strategy name (optional)
    - **emotional_state**: Emotional state during trade (optional)
    """
    try:
        trade = TradeService.create_trade(trade_data, current_user.id, db)
        return TradeResponse.from_attributes(trade)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=TradeListResponse,
    summary="List user trades",
)
async def list_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="Skip N trades"),
    limit: int = Query(50, ge=1, le=100, description="Limit results"),
    symbol: str = Query(None, description="Filter by symbol"),
    strategy: str = Query(None, description="Filter by strategy"),
    session: str = Query(None, description="Filter by session"),
) -> TradeListResponse:
    """
    Get user's trades with pagination and optional filtering.
    
    Query Parameters:
    - **skip**: Number of trades to skip (default: 0)
    - **limit**: Number of trades to return (default: 50, max: 100)
    - **symbol**: Filter by symbol (optional)
    - **strategy**: Filter by strategy (optional)
    - **session**: Filter by session (optional)
    """
    trades, total = TradeService.list_trades(
        user_id=current_user.id,
        db=db,
        skip=skip,
        limit=limit,
        symbol=symbol,
        strategy=strategy,
        session=session,
    )
    
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return TradeListResponse(
        trades=[TradeResponse.from_attributes(t) for t in trades],
        total=total,
        page=current_page,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get(
    "/statistics/summary",
    response_model=TradeStatisticsResponse,
    summary="Get trade statistics",
)
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TradeStatisticsResponse:
    """
    Get trading statistics summary for the user.
    
    Returns:
    - Total trades
    - Winning/losing trades
    - Win rate
    - Total P&L
    - Largest win/loss
    - Open trades count
    """
    return TradeService.get_trade_statistics(current_user.id, db)


@router.get(
    "/{trade_id}",
    response_model=TradeResponse,
    summary="Get trade details",
)
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TradeResponse:
    """Get details of a specific trade."""
    try:
        trade = TradeService.get_trade(trade_id, current_user.id, db)
        return TradeResponse.from_attributes(trade)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/{trade_id}",
    response_model=TradeResponse,
    summary="Update trade",
)
async def update_trade(
    trade_id: int,
    trade_data: TradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TradeResponse:
    """Update a trade record."""
    try:
        trade = TradeService.update_trade(trade_id, current_user.id, trade_data, db)
        return TradeResponse.from_attributes(trade)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{trade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete trade",
)
async def delete_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete a trade record."""
    try:
        TradeService.delete_trade(trade_id, current_user.id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
