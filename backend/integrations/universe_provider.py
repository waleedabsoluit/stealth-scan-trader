"""
Universe Provider - Real stock screening and universe building
Uses Yahoo Finance for dynamic stock discovery
"""
import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UniverseProvider:
    """Provides trading universe from Yahoo Finance"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.min_price = self.config.get('min_price', 5.0)
        self.max_price = self.config.get('max_price', 500.0)
        self.min_volume = self.config.get('min_volume', 1_000_000)
        self.min_market_cap = self.config.get('min_market_cap', 1_000_000_000)  # 1B
        
    def get_sp500_symbols(self) -> List[str]:
        """Get S&P 500 constituent symbols"""
        try:
            import pandas as pd
            table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            df = table[0]
            symbols = df['Symbol'].tolist()
            logger.info(f"Fetched {len(symbols)} S&P 500 symbols")
            return symbols[:100]  # Limit to top 100 for performance
        except Exception as e:
            logger.error(f"Error fetching S&P 500 symbols: {e}")
            return self._get_default_universe()
    
    def get_most_active(self, limit: int = 50) -> List[str]:
        """Get most active stocks by volume"""
        # Top tech and popular stocks
        active_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD', 
            'NFLX', 'DIS', 'BABA', 'V', 'MA', 'JPM', 'BAC', 'WMT', 'PFE',
            'INTC', 'CSCO', 'ORCL', 'CRM', 'ADBE', 'PYPL', 'QCOM', 'TXN',
            'AVGO', 'COST', 'CMCSA', 'PEP', 'TMO', 'ABT', 'NKE', 'UNH',
            'HD', 'MCD', 'VZ', 'T', 'MRK', 'LLY', 'KO', 'WFC', 'XOM',
            'CVX', 'BA', 'GE', 'GM', 'F', 'AAL', 'UAL', 'CCL'
        ]
        return active_stocks[:limit]
    
    def get_small_caps(self, limit: int = 30) -> List[str]:
        """Get small cap stocks with potential"""
        small_caps = [
            'PLTR', 'SOFI', 'COIN', 'RIVN', 'LCID', 'HOOD', 'RBLX', 'U',
            'DKNG', 'OPEN', 'AFRM', 'SQ', 'SNAP', 'PINS', 'UBER', 'LYFT',
            'DASH', 'ABNB', 'ZM', 'DOCU', 'CRWD', 'SNOW', 'NET', 'DDOG',
            'MDB', 'TEAM', 'OKTA', 'ZS', 'ESTC', 'SHOP'
        ]
        return small_caps[:limit]
    
    def get_meme_stocks(self) -> List[str]:
        """Get popular meme/retail stocks"""
        return ['GME', 'AMC', 'BBBY', 'NOK', 'BB', 'WISH', 'CLOV', 'SPCE']
    
    def get_etfs(self) -> List[str]:
        """Get major ETFs for market monitoring"""
        return ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'TLT']
    
    def filter_universe(self, symbols: List[str]) -> List[str]:
        """Filter symbols by price, volume, and market cap criteria"""
        filtered = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get current price
                price = info.get('currentPrice') or info.get('regularMarketPrice')
                if not price or price < self.min_price or price > self.max_price:
                    continue
                
                # Check volume
                volume = info.get('volume') or info.get('regularMarketVolume')
                if not volume or volume < self.min_volume:
                    continue
                
                # Check market cap
                market_cap = info.get('marketCap')
                if market_cap and market_cap < self.min_market_cap:
                    continue
                
                filtered.append(symbol)
                
            except Exception as e:
                logger.warning(f"Error filtering {symbol}: {e}")
                continue
        
        logger.info(f"Filtered {len(filtered)} symbols from {len(symbols)}")
        return filtered
    
    def get_full_universe(self, max_size: int = 200) -> List[str]:
        """Get comprehensive trading universe"""
        universe = set()
        
        # Add different categories
        universe.update(self.get_most_active(50))
        universe.update(self.get_small_caps(30))
        universe.update(self.get_meme_stocks())
        universe.update(self.get_etfs())
        
        # Optionally add S&P 500 (expensive API calls)
        # universe.update(self.get_sp500_symbols())
        
        # Convert to list and limit size
        universe_list = list(universe)[:max_size]
        
        logger.info(f"Built universe with {len(universe_list)} symbols")
        return universe_list
    
    def _get_default_universe(self) -> List[str]:
        """Fallback universe if API fails"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD',
            'NFLX', 'DIS', 'SPY', 'QQQ', 'GME', 'AMC', 'PLTR', 'SOFI',
            'BA', 'COIN', 'RIVN', 'F', 'GM', 'AAL', 'BABA', 'V', 'MA'
        ]
    
    def get_symbols(self) -> List[str]:
        """Main method to get trading symbols"""
        universe_size = self.config.get('universe_size', 100)
        return self.get_full_universe(max_size=universe_size)
