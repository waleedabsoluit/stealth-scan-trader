"""
Configuration API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

CONFIG_PATH = Path("backend/config/config.yml")

def load_config():
    """Load configuration from YAML file"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {}

def save_config(config: Dict[str, Any]):
    """Save configuration to YAML file"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        return False

@router.get("/config")
async def get_config():
    """Get current configuration"""
    try:
        config = load_config()
        
        # Ensure all expected fields exist
        if "trading" not in config:
            config["trading"] = {
                "min_confidence": 0.7,
                "max_positions": 10,
                "default_position_size": 1000,
                "max_position_size": 5000,
                "risk_per_trade": 0.02
            }
        
        if "scanning" not in config:
            config["scanning"] = {
                "universe_size": 100,
                "scan_interval": 60,
                "market_sessions": {
                    "premarket": True,
                    "regular": True,
                    "afterhours": False
                }
            }
        
        if "modules" not in config:
            config["modules"] = {}
        
        if "integrations" not in config:
            config["integrations"] = {
                "market_data": {
                    "provider": "yahoo",
                    "universe": ["SPY", "QQQ", "NVDA", "TSLA", "AAPL"]
                }
            }
        
        logger.info("Retrieved configuration")
        
        return {
            "status": "success",
            "data": config
        }
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_config(config: Dict[str, Any]):
    """Update configuration"""
    try:
        # Validate config structure
        if not config:
            raise ValueError("Configuration cannot be empty")
        
        # Save to file
        if save_config(config):
            logger.info("Configuration updated successfully")
            return {
                "status": "success",
                "data": {
                    "message": "Configuration updated successfully",
                    "config": config
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/reset")
async def reset_config():
    """Reset configuration to defaults"""
    try:
        default_config = {
            "trading": {
                "min_confidence": 0.7,
                "max_positions": 10,
                "default_position_size": 1000,
                "max_position_size": 5000,
                "risk_per_trade": 0.02
            },
            "scanning": {
                "universe_size": 100,
                "scan_interval": 60,
                "market_sessions": {
                    "premarket": True,
                    "regular": True,
                    "afterhours": False
                }
            },
            "modules": {
                "market_scanner": {"enabled": True},
                "pattern_scorer": {"enabled": True},
                "sentiment_analyzer": {"enabled": True},
                "risk_engine": {"enabled": True},
                "confidence_scorer": {"enabled": True}
            },
            "integrations": {
                "market_data": {
                    "provider": "yahoo",
                    "universe": ["SPY", "QQQ", "NVDA", "TSLA", "AAPL"]
                }
            }
        }
        
        if save_config(default_config):
            logger.info("Configuration reset to defaults")
            return {
                "status": "success",
                "data": {
                    "message": "Configuration reset to defaults",
                    "config": default_config
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset configuration")
            
    except Exception as e:
        logger.error(f"Error resetting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))