"""
Market data API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from backend.integrations.market_data import YahooFinanceClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/market", tags=["market"])

# Global market data client
market_client: Optional[YahooFinanceClient] = None


class MarketDataConfig(BaseModel):
    provider: str
    api_key: Optional[str] = None
    universe: List[str] = []


def get_market_client() -> YahooFinanceClient:
    """Get or create market data client"""
    global market_client
    if not market_client:
        logger.info("Creating new YahooFinanceClient instance")
        market_client = YahooFinanceClient()
    return market_client


@router.get("/quotes/{symbol}")
async def get_quote(symbol: str):
    """Get quote for a single symbol"""
    try:
        logger.info(f"Fetching quote for {symbol}")
        client = get_market_client()
        quote = client.get_quote(symbol.upper())
        logger.info(f"Quote fetched: {symbol} @ ${quote.get('price', 0)}")
        return {"status": "success", "data": quote}
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quotes")
async def get_quotes(symbols: List[str]):
    """Get quotes for multiple symbols"""
    try:
        logger.info(f"Fetching quotes for {len(symbols)} symbols: {symbols}")
        client = get_market_client()
        quotes = client.get_quotes([s.upper() for s in symbols])
        logger.info(f"Successfully fetched {len(quotes)} quotes")
        return {"status": "success", "data": quotes}
    except Exception as e:
        logger.error(f"Error fetching quotes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_market_status():
    """Get current market status"""
    try:
        client = get_market_client()
        status = client.get_market_status()
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Error fetching market status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-yahoo")
async def test_yahoo_finance():
    """Test Yahoo Finance connection and get sample data"""
    try:
        logger.info("Testing Yahoo Finance connection...")
        client = get_market_client()
        
        # Test connection
        is_connected = client.test_connection()
        logger.info(f"Connection test result: {is_connected}")
        
        # Try to fetch a sample quote
        sample_quote = None
        if is_connected:
            sample_quote = client.get_quote("AAPL")
            logger.info(f"Sample quote (AAPL): {sample_quote}")
        
        return {
            "status": "success",
            "connected": is_connected,
            "sample_quote": sample_quote,
            "message": "Yahoo Finance is working!" if is_connected else "Connection failed"
        }
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "connected": False,
            "error": str(e),
            "message": "Yahoo Finance connection test failed"
        }


@router.post("/test")
async def test_connection(config: MarketDataConfig):
    """Test market data connection"""
    try:
        # Create a new client with provided config
        if config.provider.lower() == "yahoo":
            test_client = YahooFinanceClient(api_key=config.api_key)
            is_connected = test_client.test_connection()
            
            # Test with first symbol from universe if provided
            test_symbol = None
            test_quote = None
            if config.universe and len(config.universe) > 0:
                test_symbol = config.universe[0]
                test_quote = test_client.get_quote(test_symbol)
            
            return {
                "status": "success",
                "connected": is_connected,
                "provider": config.provider,
                "test_symbol": test_symbol,
                "test_quote": test_quote
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {config.provider}")
            
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }


@router.post("/configure")
async def configure_market_data(config: MarketDataConfig):
    """Configure market data provider"""
    global market_client
    try:
        if config.provider.lower() == "yahoo":
            market_client = YahooFinanceClient(api_key=config.api_key)
            
            # Store universe in config (you might want to persist this)
            # For now, we'll just validate it works
            is_connected = market_client.test_connection()
            
            return {
                "status": "success",
                "provider": config.provider,
                "connected": is_connected,
                "universe_size": len(config.universe)
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {config.provider}")
            
    except Exception as e:
        logger.error(f"Failed to configure market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
