"""
Enhanced Signals Route with Real-time Broadcasting
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from backend.database import get_db
from backend.database.models import Signal
from backend.database.repositories.signal_repository import SignalRepository
from backend.api.routes.websocket import broadcast_signal

router = APIRouter(tags=["signals"])
logger = logging.getLogger(__name__)


@router.get("/signals")
async def get_signals(
    tier: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trading signals with optional tier filtering"""
    try:
        signal_repo = SignalRepository(db)
        
        if tier:
            signals = signal_repo.get_by_tier(tier, limit)
        else:
            signals = signal_repo.get_active_signals(limit)
        
        # Convert to dict
        signals_data = []
        for signal in signals:
            signals_data.append({
                'signal_id': signal.signal_id,
                'symbol': signal.symbol,
                'action': signal.action,
                'tier': signal.tier,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'rsi': signal.rsi,
                'volume_ratio': signal.volume_ratio,
                'reasoning': signal.reasoning,
                'created_at': signal.created_at.isoformat() if signal.created_at else None,
                'status': signal.status
            })
        
        # Get tier distribution
        tier_dist = signal_repo.get_tier_distribution()
        
        return {
            'status': 'success',
            'data': {
                'signals': signals_data,
                'total': len(signals_data),
                'tier_distribution': tier_dist
            }
        }
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{signal_id}")
async def get_signal_details(signal_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific signal"""
    try:
        signal_repo = SignalRepository(db)
        signal = signal_repo.get_by_id(signal_id)
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        return {
            'status': 'success',
            'data': {
                'signal_id': signal.signal_id,
                'symbol': signal.symbol,
                'action': signal.action,
                'tier': signal.tier,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'rsi': signal.rsi,
                'volume_ratio': signal.volume_ratio,
                'obv_trend': signal.obv_trend,
                'momentum_score': signal.momentum_score,
                'volume_score': signal.volume_score,
                'technical_score': signal.technical_score,
                'sentiment_score': signal.sentiment_score,
                'risk_score': signal.risk_score,
                'modules_data': signal.modules_data,
                'reasoning': signal.reasoning,
                'created_at': signal.created_at.isoformat() if signal.created_at else None,
                'expires_at': signal.expires_at.isoformat() if signal.expires_at else None,
                'status': signal.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signal details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signals/{signal_id}/execute")
async def execute_signal(signal_id: str, db: Session = Depends(get_db)):
    """Execute a trading signal"""
    try:
        signal_repo = SignalRepository(db)
        signal = signal_repo.get_by_id(signal_id)
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        if signal.status != 'ACTIVE':
            raise HTTPException(status_code=400, detail=f"Signal is {signal.status}, cannot execute")
        
        # Update signal status
        signal = signal_repo.update_status(signal_id, 'EXECUTED')
        
        # Broadcast execution
        await broadcast_signal({
            'signal_id': signal.signal_id,
            'symbol': signal.symbol,
            'action': 'executed',
            'tier': signal.tier
        })
        
        return {
            'status': 'success',
            'data': {
                'signal_id': signal.signal_id,
                'status': signal.status,
                'message': 'Signal executed successfully'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/recent/summary")
async def get_recent_signals_summary(hours: int = 24, db: Session = Depends(get_db)):
    """Get summary of recent signals"""
    try:
        signal_repo = SignalRepository(db)
        signals = signal_repo.get_recent(hours=hours)
        
        # Calculate summary stats
        tier_counts = {}
        total_confidence = 0
        
        for signal in signals:
            tier = signal.tier
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            total_confidence += signal.confidence
        
        avg_confidence = total_confidence / len(signals) if signals else 0
        
        return {
            'status': 'success',
            'data': {
                'total_signals': len(signals),
                'tier_breakdown': tier_counts,
                'average_confidence': round(avg_confidence, 2),
                'timeframe_hours': hours
            }
        }
    except Exception as e:
        logger.error(f"Error fetching signals summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
