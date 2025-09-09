"""
Module Management API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory module state (in production, use database)
MODULE_STATE = {
    "market_scanner": {
        "name": "Market Scanner",
        "status": "running",
        "enabled": True,
        "performance": 92.5,
        "errors": 0,
        "last_run": datetime.now().isoformat()
    },
    "pattern_scorer": {
        "name": "Pattern Scorer",
        "status": "running",
        "enabled": True,
        "performance": 88.3,
        "errors": 0,
        "last_run": datetime.now().isoformat()
    },
    "sentiment_analyzer": {
        "name": "Sentiment Analyzer",
        "status": "running",
        "enabled": True,
        "performance": 85.7,
        "errors": 1,
        "last_run": datetime.now().isoformat()
    },
    "risk_engine": {
        "name": "Risk Engine",
        "status": "running",
        "enabled": True,
        "performance": 95.0,
        "errors": 0,
        "last_run": datetime.now().isoformat()
    },
    "confidence_scorer": {
        "name": "Confidence Scorer",
        "status": "running",
        "enabled": True,
        "performance": 91.2,
        "errors": 0,
        "last_run": datetime.now().isoformat()
    },
    "dilution_detector": {
        "name": "Dilution Detector",
        "status": "idle",
        "enabled": False,
        "performance": 78.5,
        "errors": 2,
        "last_run": datetime.now().isoformat()
    }
}

@router.get("/modules")
async def get_modules():
    """Get all module statuses"""
    try:
        modules_list = [
            {
                "name": module_data["name"],
                "status": module_data["status"],
                "enabled": module_data["enabled"],
                "performance": module_data["performance"],
                "errors": module_data["errors"]
            }
            for module_data in MODULE_STATE.values()
        ]
        
        logger.info(f"Retrieved {len(modules_list)} modules")
        return {
            "status": "success",
            "data": modules_list
        }
    except Exception as e:
        logger.error(f"Error getting modules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modules/{module_name}/toggle")
async def toggle_module(module_name: str):
    """Toggle a module on/off"""
    try:
        if module_name not in MODULE_STATE:
            raise HTTPException(status_code=404, detail=f"Module {module_name} not found")
        
        module = MODULE_STATE[module_name]
        module["enabled"] = not module["enabled"]
        module["status"] = "running" if module["enabled"] else "idle"
        
        logger.info(f"Toggled module {module_name}: enabled={module['enabled']}")
        
        return {
            "status": "success",
            "data": {
                "module": module_name,
                "enabled": module["enabled"],
                "status": module["status"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling module {module_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/modules/{module_name}")
async def get_module_details(module_name: str):
    """Get detailed info about a specific module"""
    try:
        if module_name not in MODULE_STATE:
            raise HTTPException(status_code=404, detail=f"Module {module_name} not found")
        
        module = MODULE_STATE[module_name]
        
        # Add some mock detailed data
        detailed_info = {
            **module,
            "configuration": {
                "threshold": 0.75,
                "timeout": 30,
                "max_retries": 3
            },
            "statistics": {
                "total_runs": 1250,
                "successful_runs": 1156,
                "failed_runs": 94,
                "avg_execution_time": 0.234
            }
        }
        
        return {
            "status": "success",
            "data": detailed_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting module details for {module_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))