"""
STEALTH Bot Configuration Loader
Purpose: Loads YAML configuration and provides defaults so the orchestrator 
and modules are tunable without code changes.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os


def load_config(path: str = 'config/config.yml') -> Dict[str, Any]:
    """
    Load configuration from YAML file with sensible defaults.
    
    Args:
        path: Path to configuration YAML file
        
    Returns:
        Configuration dictionary with all settings
    """
    config_path = Path(path)
    
    # Default configuration
    defaults = {
        'trading': {
            'max_positions': 10,
            'max_position_size': 0.1,  # 10% of portfolio
            'risk_per_trade': 0.02,     # 2% risk per trade
            'stop_loss_percent': 0.05,   # 5% stop loss
            'take_profit_percent': 0.15, # 15% take profit
        },
        'scanning': {
            'universe_size': 5000,
            'scan_interval': 60,  # seconds
            'premarket_start': '04:00',
            'market_open': '09:30',
            'market_close': '16:00',
            'afterhours_end': '20:00',
        },
        'modules': {
            'obv_vwap': {
                'enabled': True,
                'lookback_period': 20,
                'slope_threshold': 0.5,
            },
            'float_churn': {
                'enabled': True,
                'volume_multiplier': 2.0,
            },
            'dilution_detector': {
                'enabled': True,
                'shelf_threshold_days': 90,
            },
            'orderbook_imbalance': {
                'enabled': True,
                'imbalance_threshold': 0.65,
            },
            'squeeze_potential': {
                'enabled': True,
                'short_interest_min': 15,  # minimum 15% SI
                'days_to_cover_min': 2,
            },
            'pattern_scorer': {
                'enabled': True,
                'min_pattern_score': 0.7,
            },
            'sentiment_analyzer': {
                'enabled': True,
                'source_weight': {
                    'news': 0.4,
                    'social': 0.3,
                    'filing': 0.3,
                },
            },
        },
        'risk': {
            'max_portfolio_risk': 0.06,  # 6% max portfolio risk
            'max_correlation': 0.7,
            'vix_threshold': 30,
            'position_sizing': 'kelly',  # 'kelly', 'fixed', 'volatility'
        },
        'alerts': {
            'email_enabled': False,
            'webhook_enabled': True,
            'webhook_url': os.getenv('WEBHOOK_URL', ''),
            'alert_levels': ['platinum', 'gold'],
        },
        'api': {
            'host': '0.0.0.0',
            'port': 8000,
            'debug': False,
            'cors_origins': ['*'],
            'rate_limit': 100,  # requests per minute
        },
        'database': {
            'path': 'data/stealth_bot.db',
            'backup_enabled': True,
            'backup_interval': 3600,  # seconds
        },
        'logging': {
            'level': 'INFO',
            'format': 'json',
            'file': 'logs/stealth_bot.log',
            'rotate_size': '100MB',
            'rotate_count': 10,
        },
    }
    
    # Load user configuration if exists
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
            
            # Deep merge user config with defaults
            config = deep_merge(defaults, user_config)
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            print("Using default configuration")
            config = defaults
    else:
        print(f"Config file not found at {path}, using defaults")
        config = defaults
    
    # Validate configuration
    config = validate_config(config)
    
    return config


def deep_merge(base: Dict, updates: Dict) -> Dict:
    """
    Recursively merge two dictionaries.
    
    Args:
        base: Base dictionary
        updates: Dictionary with updates
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_config(config: Dict) -> Dict:
    """
    Validate configuration values and apply constraints.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated configuration
    """
    # Validate trading parameters
    config['trading']['max_positions'] = max(1, min(50, config['trading']['max_positions']))
    config['trading']['max_position_size'] = max(0.01, min(0.25, config['trading']['max_position_size']))
    config['trading']['risk_per_trade'] = max(0.001, min(0.05, config['trading']['risk_per_trade']))
    
    # Validate risk parameters
    config['risk']['max_portfolio_risk'] = max(0.01, min(0.15, config['risk']['max_portfolio_risk']))
    config['risk']['max_correlation'] = max(0.3, min(0.95, config['risk']['max_correlation']))
    
    # Validate API parameters
    config['api']['port'] = max(1024, min(65535, config['api']['port']))
    config['api']['rate_limit'] = max(10, min(1000, config['api']['rate_limit']))
    
    return config


def get_module_config(config: Dict, module_name: str) -> Dict:
    """
    Get configuration for a specific module.
    
    Args:
        config: Full configuration dictionary
        module_name: Name of the module
        
    Returns:
        Module-specific configuration
    """
    return config.get('modules', {}).get(module_name, {})


def is_module_enabled(config: Dict, module_name: str) -> bool:
    """
    Check if a module is enabled.
    
    Args:
        config: Full configuration dictionary
        module_name: Name of the module
        
    Returns:
        True if module is enabled, False otherwise
    """
    module_config = get_module_config(config, module_name)
    return module_config.get('enabled', False)


# Export main function
__all__ = ['load_config', 'get_module_config', 'is_module_enabled']