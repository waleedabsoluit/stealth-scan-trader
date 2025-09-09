"""
Performance Metrics API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)
router = APIRouter()

def generate_performance_data():
    """Generate mock performance metrics"""
    # Daily P&L for last 30 days
    daily_pnl = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
        pnl = round(random.uniform(-5000, 10000), 2)
        daily_pnl.append({"date": date, "pnl": pnl})
    
    # Tier performance
    tier_performance = [
        {
            "tier": "PLATINUM",
            "win_rate": 78.5,
            "avg_return": 4.2,
            "trades": 45
        },
        {
            "tier": "GOLD",
            "win_rate": 65.3,
            "avg_return": 2.8,
            "trades": 89
        },
        {
            "tier": "SILVER",
            "win_rate": 52.1,
            "avg_return": 1.5,
            "trades": 156
        },
        {
            "tier": "BRONZE",
            "win_rate": 41.2,
            "avg_return": 0.8,
            "trades": 234
        }
    ]
    
    # Monthly returns
    monthly_returns = []
    for i in range(12):
        month = (datetime.now() - timedelta(days=30*i)).strftime("%b %Y")
        ret = round(random.uniform(-10, 25), 2)
        monthly_returns.append({"month": month, "return": ret})
    
    return {
        "total_pnl": sum(d["pnl"] for d in daily_pnl),
        "win_rate": 62.5,
        "sharpe_ratio": 1.85,
        "max_drawdown": -12.3,
        "total_trades": 524,
        "daily_pnl": daily_pnl,
        "tier_performance": tier_performance,
        "monthly_returns": monthly_returns
    }

@router.get("/performance")
async def get_performance():
    """Get performance metrics"""
    try:
        data = generate_performance_data()
        
        logger.info("Retrieved performance metrics")
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error getting performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/summary")
async def get_performance_summary():
    """Get performance summary"""
    try:
        data = generate_performance_data()
        
        summary = {
            "total_pnl": data["total_pnl"],
            "win_rate": data["win_rate"],
            "sharpe_ratio": data["sharpe_ratio"],
            "max_drawdown": data["max_drawdown"],
            "total_trades": data["total_trades"],
            "best_day": max(data["daily_pnl"], key=lambda x: x["pnl"]),
            "worst_day": min(data["daily_pnl"], key=lambda x: x["pnl"]),
            "avg_daily_pnl": round(sum(d["pnl"] for d in data["daily_pnl"]) / len(data["daily_pnl"]), 2)
        }
        
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/trades")
async def get_recent_trades():
    """Get recent trades"""
    try:
        trades = []
        for i in range(20):
            trades.append({
                "id": f"trade_{i+1}",
                "symbol": random.choice(["NVDA", "TSLA", "AAPL", "AMD", "META"]),
                "side": random.choice(["BUY", "SELL"]),
                "quantity": random.choice([100, 200, 300, 500]),
                "entry_price": round(random.uniform(100, 500), 2),
                "exit_price": round(random.uniform(100, 500), 2) if i < 10 else None,
                "pnl": round(random.uniform(-1000, 3000), 2) if i < 10 else None,
                "status": "CLOSED" if i < 10 else "OPEN",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat()
            })
        
        return {
            "status": "success",
            "data": sorted(trades, key=lambda x: x["timestamp"], reverse=True)
        }
    except Exception as e:
        logger.error(f"Error getting recent trades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))