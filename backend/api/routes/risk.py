"""
Risk Management API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)
router = APIRouter()

def generate_risk_data():
    """Generate mock risk metrics"""
    # Risk history
    risk_history = []
    for i in range(24):  # Last 24 hours
        time = (datetime.now() - timedelta(hours=23-i)).strftime("%H:%M")
        risk_history.append({
            "time": time,
            "portfolio": round(random.uniform(0.1, 0.5), 2),
            "market": round(random.uniform(0.2, 0.8), 2),
            "position": round(random.uniform(0.1, 0.4), 2)
        })
    
    # Exposure breakdown
    exposure_breakdown = [
        {"sector": "Technology", "exposure": 35.2, "risk": "MEDIUM"},
        {"sector": "Healthcare", "exposure": 22.1, "risk": "LOW"},
        {"sector": "Finance", "exposure": 18.5, "risk": "HIGH"},
        {"sector": "Energy", "exposure": 12.3, "risk": "MEDIUM"},
        {"sector": "Consumer", "exposure": 11.9, "risk": "LOW"}
    ]
    
    # Risk alerts
    alerts = [
        {
            "severity": "HIGH",
            "message": "Portfolio concentration in NVDA exceeds 15%",
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()
        },
        {
            "severity": "MEDIUM",
            "message": "Market volatility increasing - VIX above 25",
            "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat()
        },
        {
            "severity": "LOW",
            "message": "Correlation risk detected in tech positions",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
        }
    ]
    
    return {
        "portfolio_risk": 0.32,
        "market_volatility": 0.45,
        "max_drawdown": -12.3,
        "risk_alerts": len([a for a in alerts if a["severity"] == "HIGH"]),
        "risk_history": risk_history,
        "exposure_breakdown": exposure_breakdown,
        "alerts": alerts
    }

@router.get("/risk")
async def get_risk_metrics():
    """Get risk metrics"""
    try:
        data = generate_risk_data()
        
        logger.info("Retrieved risk metrics")
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error getting risk metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk/limits")
async def get_risk_limits():
    """Get risk limits and usage"""
    try:
        limits = {
            "max_portfolio_risk": 0.5,
            "current_portfolio_risk": 0.32,
            "max_position_size": 10000,
            "max_daily_loss": 5000,
            "current_daily_loss": 1234,
            "max_positions": 10,
            "current_positions": 6,
            "margin_usage": 45.2,
            "buying_power": 125000
        }
        
        return {
            "status": "success",
            "data": limits
        }
    except Exception as e:
        logger.error(f"Error getting risk limits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/settings")
async def update_risk_settings(settings: Dict[str, Any]):
    """Update risk management settings"""
    try:
        logger.info(f"Updating risk settings: {settings}")
        
        # In production, save to database
        return {
            "status": "success",
            "data": {
                "message": "Risk settings updated successfully",
                "settings": settings
            }
        }
    except Exception as e:
        logger.error(f"Error updating risk settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))