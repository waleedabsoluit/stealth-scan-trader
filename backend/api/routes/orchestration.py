"""
Orchestration API Routes
Real signal generation using the orchestrator
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
import logging

from backend.database import get_db
from backend.database.repositories.signal_repository import SignalRepository
from backend.orchestrator import StealthBotOrchestrator
from backend.integrations.universe_provider import UniverseProvider

router = APIRouter()
logger = logging.getLogger(__name__)

# Global orchestrator instance (initialized once)
_orchestrator = None
_universe_provider = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = StealthBotOrchestrator(config_path='backend/config/config.yml')
        logger.info("Orchestrator initialized")
    return _orchestrator


def get_universe():
    """Get or create universe provider"""
    global _universe_provider
    if _universe_provider is None:
        _universe_provider = UniverseProvider()
        logger.info("Universe provider initialized")
    return _universe_provider


@router.post("/orchestrate/scan")
async def run_scan(db: Session = Depends(get_db)):
    """
    Run a full market scan using the orchestrator
    Generates real signals and stores them in the database
    """
    try:
        orchestrator = get_orchestrator()
        universe_provider = get_universe()
        
        # Execute scan
        context = {
            'session': 'regular',
            'timestamp': datetime.now().isoformat()
        }
        
        result = orchestrator.run_autowired_tick(context, universe_provider)
        
        # Store signals in database
        signal_repo = SignalRepository(db)
        stored_signals = []
        
        for signal_data in result.get('signals', []):
            try:
                # Extract signal data
                db_signal_data = {
                    'signal_id': f"SIG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{signal_data.get('symbol')}",
                    'symbol': signal_data.get('symbol'),
                    'action': 'BUY',  # Default action
                    'tier': signal_data.get('tier', 'BRONZE'),
                    'confidence': signal_data.get('confidence', 0),
                    'entry_price': signal_data.get('modules', {}).get('market_scanner', {}).get('price', 0),
                    'modules_data': signal_data.get('modules', {}),
                    'reasoning': f"Aggregate score: {signal_data.get('aggregate_score')}",
                    'created_at': datetime.utcnow()
                }
                
                # Only store high-quality signals
                if db_signal_data['confidence'] >= 60:
                    signal = signal_repo.create(db_signal_data)
                    stored_signals.append({
                        'signal_id': signal.signal_id,
                        'symbol': signal.symbol,
                        'tier': signal.tier,
                        'confidence': signal.confidence
                    })
                    
            except Exception as e:
                logger.error(f"Error storing signal: {e}")
                continue
        
        return {
            'status': 'success',
            'data': {
                'total_scanned': len(result.get('signals', [])),
                'signals_stored': len(stored_signals),
                'signals': stored_signals,
                'latency': result.get('latency'),
                'errors': result.get('errors', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orchestrate/status")
async def get_orchestrator_status():
    """Get orchestrator status"""
    try:
        orchestrator = get_orchestrator()
        
        return {
            'status': 'success',
            'data': {
                'active': True,
                'modules_loaded': len(orchestrator.modules),
                'modules': list(orchestrator.modules.keys())
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': {
                'active': False,
                'error': str(e)
            }
        }
