"""
Performance Calculator - Real metrics from actual trades
"""
from typing import Dict, List
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
import logging

from backend.database.repositories.trade_repository import TradeRepository

logger = logging.getLogger(__name__)


class PerformanceCalculator:
    """Calculate performance metrics from real trade data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.trade_repo = TradeRepository(db)
    
    def get_performance_metrics(self, days: int = 30) -> Dict:
        """Calculate comprehensive performance metrics"""
        stats = self.trade_repo.get_performance_stats(days)
        daily_pnl = self.trade_repo.get_daily_pnl(days)
        
        # Calculate advanced metrics
        sharpe_ratio = self._calculate_sharpe_ratio(daily_pnl)
        max_drawdown = self._calculate_max_drawdown(daily_pnl)
        sortino_ratio = self._calculate_sortino_ratio(daily_pnl)
        
        return {
            **stats,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'daily_pnl': daily_pnl[-30:],  # Last 30 days
            'avg_daily_pnl': np.mean([d['pnl'] for d in daily_pnl]) if daily_pnl else 0,
            'best_day': max([d['pnl'] for d in daily_pnl]) if daily_pnl else 0,
            'worst_day': min([d['pnl'] for d in daily_pnl]) if daily_pnl else 0
        }
    
    def get_tier_performance(self) -> Dict:
        """Get performance breakdown by signal tier"""
        from backend.database.models import Trade, Signal
        from sqlalchemy import func
        
        results = self.db.query(
            Signal.tier,
            func.count(Trade.id).label('count'),
            func.sum(Trade.pnl).label('total_pnl'),
            func.avg(Trade.pnl).label('avg_pnl')
        ).join(Trade, Signal.id == Trade.signal_id).filter(
            Trade.status.in_(['CLOSED', 'STOPPED'])
        ).group_by(Signal.tier).all()
        
        tier_stats = {}
        for tier, count, total_pnl, avg_pnl in results:
            tier_stats[tier] = {
                'trades': count,
                'total_pnl': float(total_pnl or 0),
                'avg_pnl': float(avg_pnl or 0),
                'win_rate': self._calculate_tier_win_rate(tier)
            }
        
        return tier_stats
    
    def get_monthly_returns(self) -> List[Dict]:
        """Calculate monthly returns"""
        from backend.database.models import Trade
        
        # Get all closed trades
        trades = self.db.query(Trade).filter(
            Trade.status.in_(['CLOSED', 'STOPPED']),
            Trade.exit_time.isnot(None)
        ).all()
        
        # Group by month
        monthly_pnl = {}
        for trade in trades:
            month_key = trade.exit_time.strftime('%Y-%m')
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = {
                    'month': month_key,
                    'pnl': 0.0,
                    'trades': 0
                }
            monthly_pnl[month_key]['pnl'] += trade.pnl
            monthly_pnl[month_key]['trades'] += 1
        
        return list(monthly_pnl.values())
    
    def _calculate_sharpe_ratio(self, daily_pnl: List[Dict], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not daily_pnl or len(daily_pnl) < 2:
            return 0.0
        
        returns = [d['pnl'] for d in daily_pnl]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualize
        daily_rf = risk_free_rate / 252
        sharpe = (avg_return - daily_rf) / std_return * np.sqrt(252)
        
        return round(sharpe, 2)
    
    def _calculate_sortino_ratio(self, daily_pnl: List[Dict], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (only considers downside deviation)"""
        if not daily_pnl or len(daily_pnl) < 2:
            return 0.0
        
        returns = [d['pnl'] for d in daily_pnl]
        avg_return = np.mean(returns)
        
        # Calculate downside deviation
        downside_returns = [r for r in returns if r < 0]
        if not downside_returns:
            return 0.0
        
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0.0
        
        daily_rf = risk_free_rate / 252
        sortino = (avg_return - daily_rf) / downside_std * np.sqrt(252)
        
        return round(sortino, 2)
    
    def _calculate_max_drawdown(self, daily_pnl: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if not daily_pnl:
            return 0.0
        
        cumulative = [sum([d['pnl'] for d in daily_pnl[:i+1]]) for i in range(len(daily_pnl))]
        
        max_dd = 0.0
        peak = cumulative[0]
        
        for value in cumulative:
            if value > peak:
                peak = value
            dd = (peak - value) / abs(peak) * 100 if peak != 0 else 0
            max_dd = max(max_dd, dd)
        
        return round(max_dd, 2)
    
    def _calculate_tier_win_rate(self, tier: str) -> float:
        """Calculate win rate for a specific tier"""
        from backend.database.models import Trade, Signal
        
        trades = self.db.query(Trade).join(Signal, Signal.id == Trade.signal_id).filter(
            Signal.tier == tier,
            Trade.status.in_(['CLOSED', 'STOPPED'])
        ).all()
        
        if not trades:
            return 0.0
        
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        return (winning_trades / len(trades)) * 100
