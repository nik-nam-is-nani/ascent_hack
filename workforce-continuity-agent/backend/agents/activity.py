from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import asyncio

class AgentActivity:
    """Track agent activity for real-time feed"""
    def __init__(self):
        self.activities: List[Dict[str, Any]] = []

    def add(self, phase: str, message: str, details: Dict = None):
        activity = {
            "id": len(self.activities) + 1,
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "message": message,
            "details": details or {}
        }
        self.activities.append(activity)
        return activity

    def get_all(self) -> List[Dict[str, Any]]:
        return self.activities

    def clear(self):
        self.activities = []

# Global activity tracker
activity_tracker = AgentActivity()

def get_activity_feed() -> List[Dict[str, Any]]:
    """Get all activities"""
    return activity_tracker.get_all()

# WebSocket broadcast callback
broadcast_callback: Optional[Callable] = None

def set_broadcast_callback(callback: Callable):
    """Set the WebSocket broadcast callback"""
    global broadcast_callback
    broadcast_callback = callback

def broadcast_activity(phase: str, message: str, details: Dict = None):
    """Broadcast activity to WebSocket clients"""
    activity = activity_tracker.add(phase, message, details)
    if broadcast_callback:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(broadcast_callback(activity))
            else:
                loop.run_until_complete(broadcast_callback(activity))
        except Exception:
            pass  # Silently fail if broadcast fails
    return activity
