"""
Utility functions and helpers
"""

from datetime import datetime
from typing import Any, Dict, List
import json


def serialize_json(obj: Any) -> str:
    """
    Serialize object to JSON string.
    
    Handles datetime and other non-standard types.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def calculate_rr_ratio(
    entry: float,
    stop_loss: float,
    take_profit: float,
    direction: str,
) -> float:
    """
    Calculate risk-reward ratio.
    
    Args:
        entry: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        direction: LONG or SHORT
        
    Returns:
        float: RR ratio
    """
    if direction == "LONG":
        risk = entry - stop_loss
        reward = take_profit - entry
    else:  # SHORT
        risk = stop_loss - entry
        reward = entry - take_profit
    
    if risk <= 0:
        return 0.0
    
    return reward / risk


def calculate_pnl(
    entry: float,
    exit_price: float,
    lot_size: float,
    direction: str,
) -> tuple[float, float]:
    """
    Calculate PnL and PnL percentage.
    
    Args:
        entry: Entry price
        exit_price: Exit price
        lot_size: Lot size
        direction: LONG or SHORT
        
    Returns:
        tuple: (pnl, pnl_percentage)
    """
    if direction == "LONG":
        pnl = (exit_price - entry) * lot_size
        pnl_percentage = ((exit_price - entry) / entry) * 100
    else:  # SHORT
        pnl = (entry - exit_price) * lot_size
        pnl_percentage = ((entry - exit_price) / entry) * 100
    
    return pnl, pnl_percentage


def paginate(
    items: List[Any],
    page: int = 1,
    page_size: int = 50,
) -> tuple[List[Any], int]:
    """
    Paginate a list of items.
    
    Args:
        items: List to paginate
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        tuple: (paginated items, total count)
    """
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    
    return items[start:end], total
