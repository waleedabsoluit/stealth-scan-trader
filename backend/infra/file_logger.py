"""
File-based Logging with Rotation
Writes logs to files with automatic rotation
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class JSONFileFormatter(logging.Formatter):
    """Custom JSON formatter for file logging"""
    
    def format(self, record):
        log_obj = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_obj['data'] = record.extra_data
            
        return json.dumps(log_obj)


def setup_file_logging(log_dir: str = 'logs', level=None):
    """
    Setup comprehensive file logging with rotation
    
    Args:
        log_dir: Directory to store log files
        level: Logging level
    """
    log_level = level or logging.INFO
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Console handler (simple format)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Main log file (all logs) with size rotation
    main_handler = RotatingFileHandler(
        log_path / 'stealth_bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    main_handler.setFormatter(JSONFileFormatter())
    main_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(main_handler)
    
    # Error log file (errors only)
    error_handler = RotatingFileHandler(
        log_path / 'errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setFormatter(JSONFileFormatter())
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Trading log file (trading events)
    trading_handler = RotatingFileHandler(
        log_path / 'trading.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    trading_handler.setFormatter(JSONFileFormatter())
    trading_logger = logging.getLogger('trading')
    trading_logger.addHandler(trading_handler)
    
    # Performance log file (daily rotation)
    perf_handler = TimedRotatingFileHandler(
        log_path / 'performance.log',
        when='midnight',
        interval=1,
        backupCount=30  # Keep 30 days
    )
    perf_handler.setFormatter(JSONFileFormatter())
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    
    # Market data log file
    market_handler = RotatingFileHandler(
        log_path / 'market_data.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=3
    )
    market_handler.setFormatter(JSONFileFormatter())
    market_logger = logging.getLogger('market')
    market_logger.addHandler(market_handler)
    
    return root_logger


def get_logger(name: str, extra_data: dict = None):
    """
    Get a logger with optional extra data
    
    Args:
        name: Logger name
        extra_data: Extra data to include in logs
    """
    logger = logging.getLogger(name)
    
    if extra_data:
        # Create adapter to add extra data
        class ExtraAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                kwargs['extra'] = {'extra_data': self.extra}
                return msg, kwargs
        
        return ExtraAdapter(logger, extra_data)
    
    return logger