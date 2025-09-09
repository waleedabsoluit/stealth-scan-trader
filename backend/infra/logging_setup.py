"""
Logging Setup
JSON logging for easier ingestion
"""
import logging
import json
from datetime import datetime


def setup_json_logging(level=None):
    """Setup JSON formatted logging"""
    log_level = level or logging.INFO
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_obj = {
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'module': record.module,
                'message': record.getMessage()
            }
            return json.dumps(log_obj)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)
    
    return logger