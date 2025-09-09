"""
STEALTH Bot API
FastAPI application for the trading bot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn
import yaml
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.config_loader import load_config
from orchestrator import Orchestrator

# Initialize FastAPI app
app = FastAPI(
    title="STEALTH Bot API",
    description="Trading bot with advanced signal detection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
config = load_config()

# Initialize orchestrator
orchestrator = Orchestrator(config_path='config/config.yml')


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "STEALTH Bot API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": orchestrator._collect_metrics()
    }


@app.get("/api/signals")
async def get_signals():
    """Get current trading signals"""
    try:
        # Run a scan tick
        context = {
            'timestamp': datetime.now().isoformat(),
            'session': 'regular'  # Could be determined dynamically
        }
        
        # Mock universe provider for now
        class MockUniverseProvider:
            def get_symbols(self):
                return ['AAPL', 'TSLA', 'NVDA', 'AMD', 'MSFT', 'GME', 'AMC', 'SPY']
        
        universe_provider = MockUniverseProvider()
        
        # Run orchestrator
        results = orchestrator.run_autowired_tick(context, universe_provider)
        
        return {
            "success": True,
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/modules")
async def get_modules_status():
    """Get status of all modules"""
    try:
        modules_status = []
        
        for name, module in orchestrator.modules.items():
            modules_status.append({
                "name": name,
                "enabled": True,
                "status": "running",
                "config": orchestrator.config.get('modules', {}).get(name, {})
            })
            
        return {
            "success": True,
            "modules": modules_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/modules/{module_name}/toggle")
async def toggle_module(module_name: str):
    """Enable or disable a module"""
    try:
        if module_name not in orchestrator.modules:
            raise HTTPException(status_code=404, detail=f"Module {module_name} not found")
            
        # Toggle module in config
        current_state = orchestrator.config['modules'][module_name].get('enabled', True)
        orchestrator.config['modules'][module_name]['enabled'] = not current_state
        
        # Reinitialize modules
        orchestrator._initialize_modules()
        
        return {
            "success": True,
            "module": module_name,
            "enabled": not current_state,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return {
        "success": True,
        "config": orchestrator.config,
        "timestamp": datetime.now().isoformat()
    }


@app.put("/api/config")
async def update_config(config_update: dict):
    """Update configuration"""
    try:
        # Merge config updates
        from core.config_loader import deep_merge
        orchestrator.config = deep_merge(orchestrator.config, config_update)
        
        # Reinitialize modules with new config
        orchestrator._initialize_modules()
        
        return {
            "success": True,
            "message": "Configuration updated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance")
async def get_performance():
    """Get performance metrics"""
    # Mock performance data for now
    return {
        "success": True,
        "data": {
            "total_signals": 156,
            "win_rate": 68.5,
            "avg_return": 12.3,
            "sharpe_ratio": 1.85,
            "max_drawdown": -8.2,
            "total_pnl": 45678.90,
            "by_tier": {
                "PLATINUM": {"count": 12, "win_rate": 85.0, "avg_return": 18.5},
                "GOLD": {"count": 34, "win_rate": 75.0, "avg_return": 14.2},
                "SILVER": {"count": 56, "win_rate": 65.0, "avg_return": 10.8},
                "BRONZE": {"count": 54, "win_rate": 55.0, "avg_return": 7.2}
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/risk")
async def get_risk_metrics():
    """Get current risk metrics"""
    return {
        "success": True,
        "data": {
            "portfolio_risk": 0.042,
            "position_count": 5,
            "total_exposure": 0.23,
            "max_position_size": 0.05,
            "sector_concentration": {
                "Technology": 0.45,
                "Healthcare": 0.25,
                "Finance": 0.15,
                "Energy": 0.15
            },
            "risk_alerts": [
                {"level": "warning", "message": "High concentration in Technology sector"},
                {"level": "info", "message": "Portfolio within risk limits"}
            ]
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)