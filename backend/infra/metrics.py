"""
Metrics collection for STEALTH Bot
Simple metrics implementation without Prometheus dependency
"""
from typing import Dict, Any, Callable
from functools import wraps
import time


class Counter:
    """Simple counter metric"""
    
    def __init__(self):
        self.value = 0
        self.labels_data = {}
    
    def inc(self, amount=1):
        """Increment counter"""
        self.value += amount
    
    def labels(self, **kwargs):
        """Return labeled counter"""
        key = tuple(sorted(kwargs.items()))
        if key not in self.labels_data:
            self.labels_data[key] = Counter()
        return self.labels_data[key]


class Histogram:
    """Simple histogram metric"""
    
    def __init__(self):
        self.values = []
    
    def observe(self, value):
        """Record an observation"""
        self.values.append(value)


# Global metrics
REQUEST_COUNT = Counter()
REQUEST_LATENCY = Histogram()
SIGNALS_BY_TIER = Counter()
REJECT_COUNT = Counter()


def orchestrator_metrics(func: Callable) -> Callable:
    """
    Decorator to track orchestrator metrics
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            REQUEST_LATENCY.observe(time.time() - start)
    
    return wrapper