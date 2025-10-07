"""
Trade Repository - Data access layer for trades
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.database.models import Trade


class TradeRepository:
    """Repository for Trade operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, trade_data: Dict) -> Trade:
        """Create a new trade"""
        trade = Trade(**trade_data)
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        return trade
    
    def get_by_id(self, trade_id: str) -> Optional[Trade]:
        """Get trade by ID"""
        return self.db.query(Trade).filter(Trade.trade_id == trade_id).first()
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades"""
        return self.db.query(Trade).filter(Trade.status == 'OPEN').all()
    
    def get_closed_trades(self, limit: int = 100) -> List[Trade]:
        """Get closed trades"""
        return self.db.query(Trade).filter(
            Trade.status.in_(['CLOSED', 'STOPPED'])
        ).order_by(desc(Trade.exit_time)).limit(limit).all()
    
    def get_by_symbol(self, symbol: str) -> List[Trade]:
        """Get trades for a specific symbol"""
        return self.db.query(Trade).filter(
            Trade.symbol == symbol
        ).order_by(desc(Trade.entry_time)).all()
    
    def update_trade(self, trade_id: str, updates: Dict) -> Optional[Trade]:
        """Update trade fields"""
        trade = self.get_by_id(trade_id)
        if trade:
            for key, value in updates.items():
                setattr(trade, key, value)
            trade.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(trade)
        return trade
    
    def close_trade(self, trade_id: str, exit_price: float, reason: str) -> Optional[Trade]:
        """Close a trade"""
        trade = self.get_by_id(trade_id)
        if trade and trade.status == 'OPEN':
            trade.exit_price = exit_price
            trade.exit_time = datetime.utcnow()
            trade.status = 'CLOSED'
            trade.close_reason = reason
            
            # Calculate P&L
            if trade.side == 'BUY':
                trade.pnl = (exit_price - trade.entry_price) * trade.quantity
            else:
                trade.pnl = (trade.entry_price - exit_price) * trade.quantity
            
            trade.pnl_percent = (trade.pnl / trade.position_size) * 100
            
            self.db.commit()
            self.db.refresh(trade)
        return trade
    
    def get_performance_stats(self, days: int = 30) -> Dict:
        """Get performance statistics"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        trades = self.db.query(Trade).filter(
            Trade.entry_time >= cutoff,
            Trade.status.in_(['CLOSED', 'STOPPED'])
        ).all()
        
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0
            }
        
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in trades)
        total_wins = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_pnl': total_pnl,
            'win_rate': (len(winning_trades) / len(trades)) * 100 if trades else 0,
            'avg_win': total_wins / len(winning_trades) if winning_trades else 0,
            'avg_loss': total_losses / len(losing_trades) if losing_trades else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else 0
        }
    
    def get_daily_pnl(self, days: int = 30) -> List[Dict]:
        """Get daily P&L breakdown"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        trades = self.db.query(Trade).filter(
            Trade.exit_time >= cutoff,
            Trade.status.in_(['CLOSED', 'STOPPED'])
        ).all()
        
        # Group by date
        daily_pnl = {}
        for trade in trades:
            date = trade.exit_time.date()
            if date not in daily_pnl:
                daily_pnl[date] = 0.0
            daily_pnl[date] += trade.pnl
        
        return [{'date': str(date), 'pnl': pnl} for date, pnl in sorted(daily_pnl.items())]
