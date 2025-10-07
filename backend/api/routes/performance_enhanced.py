"""
Enhanced Performance Route with Real Data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import logging

from backend.database import get_db
from backend.analytics.performance_calculator import PerformanceCalculator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/performance")
async def get_performance(days: int = 30, db: Session = Depends(get_db)):
    """Get comprehensive performance metrics"""
    try:
        calc = PerformanceCalculator(db)
        metrics = calc.get_performance_metrics(days)
        
        return {
            'status': 'success',
            'data': metrics
        }
    except Exception as e:
        logger.error(f"Error fetching performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/summary")
async def get_performance_summary(db: Session = Depends(get_db)):
    """Get performance summary"""
    try:
        calc = PerformanceCalculator(db)
        metrics = calc.get_performance_metrics(days=30)
        
        summary = {
            'total_pnl': metrics.get('total_pnl', 0),
            'win_rate': metrics.get('win_rate', 0),
            'sharpe_ratio': metrics.get('sharpe_ratio', 0),
            'max_drawdown': metrics.get('max_drawdown', 0),
            'total_trades': metrics.get('total_trades', 0),
            'winning_trades': metrics.get('winning_trades', 0),
            'losing_trades': metrics.get('losing_trades', 0),
            'avg_win': metrics.get('avg_win', 0),
            'avg_loss': metrics.get('avg_loss', 0),
            'best_day': metrics.get('best_day', 0),
            'worst_day': metrics.get('worst_day', 0),
            'avg_daily_pnl': metrics.get('avg_daily_pnl', 0)
        }
        
        return {
            'status': 'success',
            'data': summary
        }
    except Exception as e:
        logger.error(f"Error fetching performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/tier")
async def get_tier_performance(db: Session = Depends(get_db)):
    """Get performance breakdown by signal tier"""
    try:
        calc = PerformanceCalculator(db)
        tier_stats = calc.get_tier_performance()
        
        return {
            'status': 'success',
            'data': tier_stats
        }
    except Exception as e:
        logger.error(f"Error fetching tier performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/monthly")
async def get_monthly_performance(db: Session = Depends(get_db)):
    """Get monthly returns"""
    try:
        calc = PerformanceCalculator(db)
        monthly = calc.get_monthly_returns()
        
        return {
            'status': 'success',
            'data': monthly
        }
    except Exception as e:
        logger.error(f"Error fetching monthly performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/trades")
async def get_recent_trades(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent trades"""
    try:
        from backend.database.repositories.trade_repository import TradeRepository
        
        trade_repo = TradeRepository(db)
        trades = trade_repo.get_closed_trades(limit)
        
        trades_data = []
        for trade in trades:
            trades_data.append({
                'trade_id': trade.trade_id,
                'symbol': trade.symbol,
                'side': trade.side,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'quantity': trade.quantity,
                'pnl': trade.pnl,
                'pnl_percent': trade.pnl_percent,
                'status': trade.status,
                'close_reason': trade.close_reason,
                'entry_time': trade.entry_time.isoformat() if trade.entry_time else None,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None
            })
        
        return {
            'status': 'success',
            'data': trades_data
        }
    except Exception as e:
        logger.error(f"Error fetching recent trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))
