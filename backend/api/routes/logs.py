"""
Log Viewing API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)
router = APIRouter()

def read_log_file(log_path: Path, lines: int = 100, level: Optional[str] = None):
    """Read and parse log file"""
    if not log_path.exists():
        return []
    
    logs = []
    with open(log_path, 'r') as f:
        # Read last N lines
        all_lines = f.readlines()
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        for line in recent_lines:
            try:
                # Try to parse as JSON
                log_entry = json.loads(line.strip())
                
                # Filter by level if specified
                if level and log_entry.get("level") != level:
                    continue
                    
                logs.append(log_entry)
            except json.JSONDecodeError:
                # If not JSON, include as plain text
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": line.strip()
                })
    
    return logs

@router.get("/logs")
async def get_logs(
    log_type: str = Query("main", description="Type of log to retrieve"),
    lines: int = Query(100, description="Number of lines to retrieve"),
    level: Optional[str] = Query(None, description="Filter by log level")
):
    """Get system logs"""
    try:
        log_dir = Path("logs")
        
        # Map log types to files
        log_files = {
            "main": "stealth_bot.log",
            "errors": "errors.log",
            "trading": "trading.log",
            "performance": "performance.log",
            "market": "market_data.log"
        }
        
        if log_type not in log_files:
            raise HTTPException(status_code=400, detail=f"Invalid log type: {log_type}")
        
        log_path = log_dir / log_files[log_type]
        logs = read_log_file(log_path, lines, level)
        
        logger.info(f"Retrieved {len(logs)} log entries from {log_type}")
        
        return {
            "status": "success",
            "data": {
                "logs": logs,
                "total": len(logs),
                "log_type": log_type,
                "file": str(log_path)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/stats")
async def get_log_stats():
    """Get log statistics"""
    try:
        log_dir = Path("logs")
        stats = {}
        
        for log_file in log_dir.glob("*.log"):
            if log_file.is_file():
                file_stats = log_file.stat()
                stats[log_file.stem] = {
                    "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    "lines": sum(1 for _ in open(log_file))
                }
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting log stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/logs/clear")
async def clear_logs(log_type: str = Query("all", description="Type of log to clear")):
    """Clear log files"""
    try:
        log_dir = Path("logs")
        
        if log_type == "all":
            # Clear all log files
            cleared = []
            for log_file in log_dir.glob("*.log"):
                log_file.write_text("")
                cleared.append(log_file.name)
            
            logger.info(f"Cleared all log files: {cleared}")
            message = f"Cleared {len(cleared)} log files"
        else:
            # Clear specific log file
            log_files = {
                "main": "stealth_bot.log",
                "errors": "errors.log",
                "trading": "trading.log",
                "performance": "performance.log",
                "market": "market_data.log"
            }
            
            if log_type not in log_files:
                raise HTTPException(status_code=400, detail=f"Invalid log type: {log_type}")
            
            log_path = log_dir / log_files[log_type]
            log_path.write_text("")
            
            logger.info(f"Cleared log file: {log_path}")
            message = f"Cleared {log_type} log file"
        
        return {
            "status": "success",
            "data": {
                "message": message
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))