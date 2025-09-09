"""
Configuration loader and management for STEALTH Bot
"""
import os
import yaml
from typing import Dict, Any
from pathlib import Path


def load_config(path: str = 'config/config.yml') -> Dict[str, Any]:
    """
    Load configuration from YAML file and merge with defaults.
    
    Args:
        path: Path to configuration file
        
    Returns:
        Merged configuration dictionary
    """
    # Default configuration
    defaults = {
        'trading': {
            'universe_size': 500,
            'max_positions': 10,
            'min_confidence': 60,
            'risk_per_trade': 0.02,
            'max_daily_loss': 0.05,
        },
        'scanning': {
            'interval_seconds': 60,
            'parallel_workers': 10,
            'timeout_seconds': 30,
        },
        'modules': {
            'obv_vwap': {
                'enabled': True,
                'lookback_period': 20,
                'volume_threshold': 1000000,
            },
            'float_churn': {
                'enabled': True,
                'min_churn': 0.5,
                'lookback_days': 5,
            },
            'dilution_detector': {
                'enabled': True,
                'sensitivity': 'medium',
            },
            'orderbook_imbalance': {
                'enabled': False,
                'depth_levels': 10,
            },
            'squeeze_potential': {
                'enabled': True,
                'min_short_interest': 15,
            },
            'pattern_scorer': {
                'enabled': False,
                'patterns': ['breakout', 'reversal'],
            },
            'sentiment_analyzer': {
                'enabled': False,
                'sources': ['reddit', 'twitter'],
            },
            'confidence_scorer': {
                'enabled': True,
                'weights': {
                    'technical': 0.4,
                    'fundamental': 0.3,
                    'sentiment': 0.3,
                }
            },
            'stealth_builder': {
                'enabled': False,
                'threshold': 0.7,
            },
            'platinum_gatekeeper': {
                'enabled': True,
                'min_confidence': 85,
            },
            'market_scanner': {
                'enabled': True,
                'universe_size': 500,
            },
        },
        'risk': {
            'max_position_size': 0.1,
            'stop_loss_percent': 0.05,
            'take_profit_percent': 0.15,
            'max_drawdown': 0.2,
        },
        'alerts': {
            'enabled': True,
            'channels': ['console', 'webhook'],
            'min_tier': 'GOLD',
        },
        'api': {
            'host': '0.0.0.0',
            'port': 8000,
            'cors_origins': ['http://localhost:5173', 'http://localhost:3000'],
        },
        'database': {
            'connection': 'sqlite:///stealth_bot.db',
            'pool_size': 10,
        },
        'logging': {
            'level': 'INFO',
            'format': 'json',
            'file': 'logs/stealth_bot.log',
        }
    }
    
    # Load configuration file if it exists
    config_path = Path(path)
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
            user_config = {}
    else:
        user_config = {}
    
    # Merge configurations
    config = deep_merge(defaults, user_config)
    
    # Validate configuration
    config = validate_config(config)
    
    return config


def deep_merge(base: Dict, updates: Dict) -> Dict:
    """
    Recursively merge two dictionaries.
    
    Args:
        base: Base dictionary
        updates: Updates to apply
        
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
    Validate and constrain configuration values.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated configuration
    """
    # Validate trading parameters
    config['trading']['universe_size'] = max(1, min(5000, config['trading']['universe_size']))
    config['trading']['max_positions'] = max(1, min(50, config['trading']['max_positions']))
    config['trading']['min_confidence'] = max(0, min(100, config['trading']['min_confidence']))
    
    # Validate risk parameters
    config['risk']['max_position_size'] = max(0.01, min(1.0, config['risk']['max_position_size']))
    config['risk']['stop_loss_percent'] = max(0.01, min(0.5, config['risk']['stop_loss_percent']))
    config['risk']['take_profit_percent'] = max(0.01, min(1.0, config['risk']['take_profit_percent']))
    
    # Validate API parameters
    config['api']['port'] = max(1024, min(65535, config['api']['port']))
    
    return config


def get_module_config(config: Dict, module_name: str) -> Dict:
    """
    Get configuration for a specific module.
    
    Args:
        config: Full configuration dictionary
        module_name: Name of the module
        
    Returns:
        Module configuration dictionary
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