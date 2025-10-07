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
        market_client = YahooFinanceClient()
    return market_client


@router.get("/quotes/{symbol}")
async def get_quote(symbol: str):
    """Get quote for a single symbol"""
    try:
        client = get_market_client()
        quote = client.get_quote(symbol.upper())
        return {"status": "success", "data": quote}
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quotes")
async def get_quotes(symbols: List[str]):
    """Get quotes for multiple symbols"""
    try:
        client = get_market_client()
        quotes = client.get_quotes([s.upper() for s in symbols])
        return {"status": "success", "data": quotes}
    except Exception as e:
        logger.error(f"Error fetching quotes: {e}")
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