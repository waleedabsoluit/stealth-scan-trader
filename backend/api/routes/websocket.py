"""
WebSocket Handler for Real-time Updates
Broadcasts signals, trades, and system status to connected clients
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
import json
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time updates
    Sends: signals, trades, bot status, market data
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to STEALTH Bot live feed",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                
                elif message.get("type") == "subscribe":
                    # Client subscribing to specific channels
                    channels = message.get("channels", [])
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "channels": channels,
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
    
    finally:
        manager.disconnect(websocket)


async def broadcast_signal(signal: Dict):
    """Broadcast new signal to all clients"""
    await manager.broadcast({
        "type": "signal",
        "data": signal,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_trade(trade: Dict):
    """Broadcast new trade to all clients"""
    await manager.broadcast({
        "type": "trade",
        "data": trade,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_bot_status(status: Dict):
    """Broadcast bot status update"""
    await manager.broadcast({
        "type": "bot_status",
        "data": status,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_market_update(market_data: Dict):
    """Broadcast market data update"""
    await manager.broadcast({
        "type": "market_update",
        "data": market_data,
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_alert(alert: Dict):
    """Broadcast system alert"""
    await manager.broadcast({
        "type": "alert",
        "data": alert,
        "timestamp": datetime.utcnow().isoformat()
    })
