"""
Bot Control API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory bot state (in production, use database)
BOT_STATE = {
    "auto_trading": False,
    "scanning": False,
    "last_action_at": datetime.now().isoformat(),
    "scan_count": 0,
    "trade_count": 0
}

@router.get("/bot/status")
async def get_bot_status():
    """Get current bot status"""
    try:
        logger.info("Getting bot status")
        return {
            "status": "success",
            "data": {
                "auto_trading": BOT_STATE["auto_trading"],
                "scanning": BOT_STATE["scanning"],
                "last_action_at": BOT_STATE["last_action_at"],
                "scan_count": BOT_STATE["scan_count"],
                "trade_count": BOT_STATE["trade_count"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bot/autotrade/toggle")
async def toggle_auto_trade():
    """Toggle auto trading on/off"""
    try:
        BOT_STATE["auto_trading"] = not BOT_STATE["auto_trading"]
        BOT_STATE["last_action_at"] = datetime.now().isoformat()
        
        action = "enabled" if BOT_STATE["auto_trading"] else "disabled"
        logger.info(f"Auto trading {action}")
        
        # Log to trading log
        trading_logger = logging.getLogger('trading')
        trading_logger.info(f"AUTO_TRADE_{action.upper()}", extra={
            "state": BOT_STATE["auto_trading"],
            "timestamp": BOT_STATE["last_action_at"]
        })
        
        return {
            "status": "success",
            "data": {
                "auto_trading": BOT_STATE["auto_trading"],
                "message": f"Auto trading {action}"
            }
        }
    except Exception as e:
        logger.error(f"Error toggling auto trade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bot/scanning/toggle")
async def toggle_scanning():
    """Toggle market scanning on/off"""
    try:
        BOT_STATE["scanning"] = not BOT_STATE["scanning"]
        BOT_STATE["last_action_at"] = datetime.now().isoformat()
        
        action = "started" if BOT_STATE["scanning"] else "stopped"
        logger.info(f"Market scanning {action}")
        
        # Log to market log
        market_logger = logging.getLogger('market')
        market_logger.info(f"SCANNING_{action.upper()}", extra={
            "state": BOT_STATE["scanning"],
            "timestamp": BOT_STATE["last_action_at"]
        })
        
        return {
            "status": "success",
            "data": {
                "scanning": BOT_STATE["scanning"],
                "message": f"Market scanning {action}"
            }
        }
    except Exception as e:
        logger.error(f"Error toggling scanning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bot/scan-once")
async def scan_once():
    """Run a single market scan"""
    try:
        BOT_STATE["scan_count"] += 1
        BOT_STATE["last_action_at"] = datetime.now().isoformat()
        
        # Mock scan results
        results = [
            {"symbol": "NVDA", "confidence": 0.92, "momentum": 0.85},
            {"symbol": "TSLA", "confidence": 0.88, "momentum": 0.79},
            {"symbol": "AAPL", "confidence": 0.85, "momentum": 0.72}
        ]
        
        logger.info(f"Manual scan completed: {len(results)} opportunities found")
        
        return {
            "status": "success",
            "data": {
                "scan_count": BOT_STATE["scan_count"],
                "results_count": len(results),
                "top_opportunities": results[:3],
                "timestamp": BOT_STATE["last_action_at"]
            }
        }
    except Exception as e:
        logger.error(f"Error running scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bot/reset")
async def reset_bot():
    """Reset bot to initial state"""
    try:
        BOT_STATE.update({
            "auto_trading": False,
            "scanning": False,
            "last_action_at": datetime.now().isoformat(),
            "scan_count": 0,
            "trade_count": 0
        })
        
        logger.info("Bot state reset to defaults")
        
        return {
            "status": "success",
            "data": {
                "message": "Bot reset to initial state",
                "state": BOT_STATE
            }
        }
    except Exception as e:
        logger.error(f"Error resetting bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))