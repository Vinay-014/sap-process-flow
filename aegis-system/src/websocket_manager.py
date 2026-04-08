"""
AEGIS WebSocket Manager
Real-time streaming updates to frontend.
"""

import json
import asyncio
import logging
from typing import Dict, Set, Any
from datetime import datetime

logger = logging.getLogger("aegis.websocket")


class WebSocketManager:
    """Manages WebSocket connections and broadcasts real-time updates."""

    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.subscribers: Dict[str, Set[str]] = {
            "cop": set(),
            "missions": set(),
            "agents": set(),
            "intel": set(),
            "threats": set(),
        }

    async def connect(self, websocket, connection_id: str, channels: list = None):
        """Accept a WebSocket connection and subscribe to channels."""
        await websocket.accept()
        self.connections[connection_id] = {
            "websocket": websocket,
            "channels": set(channels or ["cop"]),
            "connected_at": datetime.utcnow().isoformat(),
        }
        for channel in self.connections[connection_id]["channels"]:
            if channel in self.subscribers:
                self.subscribers[channel].add(connection_id)
        logger.info(f"WebSocket connected: {connection_id}, channels: {channels}")

    async def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.connections:
            for channel in self.connections[connection_id]["channels"]:
                if channel in self.subscribers:
                    self.subscribers[channel].discard(connection_id)
            del self.connections[connection_id]
            logger.info(f"WebSocket disconnected: {connection_id}")

    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast a message to all subscribers of a channel."""
        message["channel"] = channel
        message["timestamp"] = datetime.utcnow().isoformat()

        disconnected = []
        for conn_id in self.subscribers.get(channel, set()):
            if conn_id in self.connections:
                try:
                    await self.connections[conn_id]["websocket"].send_json(message)
                except Exception as e:
                    logger.warning(f"WebSocket send failed for {conn_id}: {e}")
                    disconnected.append(conn_id)

        # Clean up disconnected clients
        for conn_id in disconnected:
            await self.disconnect(conn_id)

    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific connection."""
        if connection_id in self.connections:
            try:
                await self.connections[connection_id]["websocket"].send_json(message)
            except Exception as e:
                logger.warning(f"WebSocket send failed for {connection_id}: {e}")
                await self.disconnect(connection_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        return {
            "active_connections": len(self.connections),
            "subscribers_by_channel": {ch: len(subs) for ch, subs in self.subscribers.items()},
        }


# Global instance
websocket_manager = WebSocketManager()
