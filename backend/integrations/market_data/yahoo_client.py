"""
Yahoo Finance market data provider
"""
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .base import MarketDataProvider

logger = logging.getLogger(__name__)


class YahooFinanceClient(MarketDataProvider):
    """Yahoo Finance data provider using yfinance library"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Yahoo Finance client
        Note: yfinance doesn't require API key for basic data
        API key can be used for RapidAPI if needed in future
        """
        self.api_key = api_key
        self._cache = {}
        self._cache_ttl = 30  # seconds (increased from 5 to reduce API calls)
        self._last_cache_time = {}
    
    def get_quote(self, symbol: str) -> Dict:
        """Get current quote for a symbol"""
        try:
            # Check cache
            if self._is_cached(symbol):
                logger.debug(f"Returning cached quote for {symbol}")
                return self._cache[symbol]
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price and change
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', 0))
            
            quote = {
                'symbol': symbol,
                'price': current_price,
                'change': current_price - previous_close if previous_close else 0,
                'change_percent': ((current_price - previous_close) / previous_close * 100) if previous_close else 0,
                'volume': info.get('volume', info.get('regularMarketVolume', 0)),
                'high': info.get('dayHigh', info.get('regularMarketDayHigh', 0)),
                'low': info.get('dayLow', info.get('regularMarketDayLow', 0)),
                'open': info.get('open', info.get('regularMarketOpen', 0)),
                'previous_close': previous_close,
                'timestamp': datetime.now().isoformat(),
                'market_cap': info.get('marketCap', 0),
                'name': info.get('shortName', symbol)
            }
            
            # Update cache
            self._cache[symbol] = quote
            self._last_cache_time[symbol] = datetime.now()
            
            return quote
            
        except Exception as e:
            error_msg = str(e)
            
            # If rate limited (429) and we have cached data, return it
            if '429' in error_msg and symbol in self._cache:
                logger.warning(f"Rate limited for {symbol}, returning cached data")
                cached_quote = self._cache[symbol].copy()
                cached_quote['cached'] = True
                return cached_quote
            
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {
                'symbol': symbol,
                'price': 0,
                'change': 0,
                'change_percent': 0,
                'volume': 0,
                'error': str(e)
            }
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols"""
        quotes = {}
        for symbol in symbols:
            quotes[symbol] = self.get_quote(symbol)
        return quotes
    
    def get_historical(self, symbol: str, period: str = "1d") -> Dict:
        """Get historical data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            return {
                'symbol': symbol,
                'data': hist.to_dict('records'),
                'period': period,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e)
            }
    
    def test_connection(self) -> bool:
        """Test if the connection is working"""
        try:
            # Test with a known symbol
            ticker = yf.Ticker("SPY")
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_market_status(self) -> Dict:
        """Get current market status"""
        now = datetime.now()
        hour = now.hour
        
        # Simple market hours check (ET)
        if now.weekday() >= 5:  # Weekend
            status = "CLOSED"
            session = "Weekend"
        elif hour < 4:
            status = "CLOSED"
            session = "After Hours"
        elif 4 <= hour < 9.5:
            status = "OPEN"
            session = "Pre-Market"
        elif 9.5 <= hour < 16:
            status = "OPEN"
            session = "Regular"
        elif 16 <= hour < 20:
            status = "OPEN"
            session = "After Hours"
        else:
            status = "CLOSED"
            session = "Closed"
        
        return {
            'status': status,
            'session': session,
            'timestamp': now.isoformat()
        }
    
    def _is_cached(self, symbol: str) -> bool:
        """Check if symbol data is cached and still valid"""
        if symbol not in self._cache:
            return False
        
        last_time = self._last_cache_time.get(symbol)
        if not last_time:
            return False
        
        return (datetime.now() - last_time).total_seconds() < self._cache_ttl