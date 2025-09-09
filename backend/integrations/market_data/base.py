"""
Base class for market data providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class MarketDataProvider(ABC):
    """Abstract base class for market data providers"""
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Dict:
        """Get current quote for a symbol"""
        pass
    
    @abstractmethod
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols"""
        pass
    
    @abstractmethod
    def get_historical(self, symbol: str, period: str = "1d") -> Dict:
        """Get historical data for a symbol"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the connection is working"""
        pass
    
    @abstractmethod
    def get_market_status(self) -> Dict:
        """Get current market status"""
        pass