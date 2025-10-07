"""
Signal Repository - Data access layer for signals
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from backend.database.models import Signal


class SignalRepository:
    """Repository for Signal operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, signal_data: Dict) -> Signal:
        """Create a new signal"""
        signal = Signal(**signal_data)
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)
        return signal
    
    def get_by_id(self, signal_id: str) -> Optional[Signal]:
        """Get signal by ID"""
        return self.db.query(Signal).filter(Signal.signal_id == signal_id).first()
    
    def get_active_signals(self, limit: int = 100) -> List[Signal]:
        """Get all active signals"""
        return self.db.query(Signal).filter(
            Signal.status == 'ACTIVE',
            Signal.expires_at > datetime.utcnow()
        ).order_by(desc(Signal.created_at)).limit(limit).all()
    
    def get_by_symbol(self, symbol: str, limit: int = 50) -> List[Signal]:
        """Get signals for a specific symbol"""
        return self.db.query(Signal).filter(
            Signal.symbol == symbol
        ).order_by(desc(Signal.created_at)).limit(limit).all()
    
    def get_by_tier(self, tier: str, limit: int = 100) -> List[Signal]:
        """Get signals by tier"""
        return self.db.query(Signal).filter(
            Signal.tier == tier,
            Signal.status == 'ACTIVE'
        ).order_by(desc(Signal.created_at)).limit(limit).all()
    
    def get_recent(self, hours: int = 24, limit: int = 200) -> List[Signal]:
        """Get recent signals within timeframe"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(Signal).filter(
            Signal.created_at >= cutoff
        ).order_by(desc(Signal.created_at)).limit(limit).all()
    
    def update_status(self, signal_id: str, status: str) -> Optional[Signal]:
        """Update signal status"""
        signal = self.get_by_id(signal_id)
        if signal:
            signal.status = status
            self.db.commit()
            self.db.refresh(signal)
        return signal
    
    def expire_old_signals(self) -> int:
        """Expire signals past their expiry time"""
        count = self.db.query(Signal).filter(
            Signal.status == 'ACTIVE',
            Signal.expires_at <= datetime.utcnow()
        ).update({'status': 'EXPIRED'})
        self.db.commit()
        return count
    
    def get_tier_distribution(self) -> Dict[str, int]:
        """Get count of signals by tier"""
        from sqlalchemy import func
        results = self.db.query(
            Signal.tier, func.count(Signal.id)
        ).filter(Signal.status == 'ACTIVE').group_by(Signal.tier).all()
        return {tier: count for tier, count in results}
    
    def delete_old_signals(self, days: int = 30) -> int:
        """Delete signals older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        count = self.db.query(Signal).filter(
            Signal.created_at < cutoff
        ).delete()
        self.db.commit()
        return count
