import asyncio
import logging
import uuid
from typing import Dict, Any, Optional

class ClassroomManager:
    """Manages classroom translation sessions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_session(self, config: Dict[str, Any]) -> str:
        """Create a new classroom session
        
        Args:
            config: Session configuration including teacher_id, class_name, and target_languages
            
        Returns:
            str: Session identifier
        """
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            **config,
            'active': True,
            'created_at': asyncio.get_event_loop().time()
        }
        return session_id
    
    async def end_session(self, session_id: str) -> None:
        """End an active classroom session
        
        Args:
            session_id: Session identifier to end
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def get_active_sessions(self) -> list:
        """Get list of active classroom sessions
        
        Returns:
            list: List of active session identifiers
        """
        return list(self.active_sessions.keys())