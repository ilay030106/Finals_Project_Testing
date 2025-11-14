"""User session management for maintaining per-user state"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserSession:
    """Manages session state for a single user"""
    
    def __init__(self, user_id: int, username: Optional[str] = None):
        """Initialize user session
        
        Args:
            user_id: Telegram user ID
            username: Optional username
        """
        self.user_id = user_id
        self.username = username
        self.current_menu: Optional[str] = None
        self.conversation_state: Optional[str] = None
        self.data: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        logger.debug(f"Created session for user {user_id}")
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def set_menu(self, menu_name: str) -> None:
        """Set current menu
        
        Args:
            menu_name: Name of the current menu
        """
        self.current_menu = menu_name
        self.update_activity()
        logger.debug(f"User {self.user_id} menu set to: {menu_name}")
    
    def set_state(self, state: str) -> None:
        """Set conversation state
        
        Args:
            state: The conversation state identifier
        """
        self.conversation_state = state
        self.update_activity()
        logger.debug(f"User {self.user_id} state set to: {state}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get data from session
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            The value or default
        """
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set data in session
        
        Args:
            key: Data key
            value: Value to store
        """
        self.data[key] = value
        self.update_activity()
        logger.debug(f"User {self.user_id} data set: {key} = {value}")
    
    def clear_data(self) -> None:
        """Clear all session data"""
        self.data.clear()
        logger.debug(f"Cleared data for user {self.user_id}")
    
    def reset(self) -> None:
        """Reset session to initial state"""
        self.current_menu = None
        self.conversation_state = None
        self.clear_data()
        logger.info(f"Reset session for user {self.user_id}")
    
    def __repr__(self) -> str:
        return f"UserSession(user_id={self.user_id}, menu={self.current_menu}, state={self.conversation_state})"


class SessionManager:
    """Manages sessions for all users"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sessions= {}
        return cls._instance
    
    def get_session(self, user_id: int, username: Optional[str] = None) -> UserSession:
        """Get or create session for user
        
        Args:
            user_id: Telegram user ID
            username: Optional username
            
        Returns:
            UserSession instance
        """
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id, username)
            logger.info(f"Created new session for user {user_id}")
        
        session = self._sessions[user_id]
        session.update_activity()
        return session
    
    def remove_session(self, user_id: int) -> None:
        """Remove session for user
        
        Args:
            user_id: Telegram user ID
        """
        if user_id in self._sessions:
            del self._sessions[user_id]
            logger.info(f"Removed session for user {user_id}")
    
    def get_all_sessions(self) -> Dict[int, UserSession]:
        """Get all active sessions
        
        Returns:
            Dictionary of user_id -> UserSession
        """
        return self._sessions.copy()
    
    def cleanup_inactive(self, max_idle_hours: int = 24) -> int:
        """Remove sessions inactive for specified hours
        
        Args:
            max_idle_hours: Maximum hours of inactivity
            
        Returns:
            Number of sessions removed
        """
        from datetime import timedelta
        
        now = datetime.now()
        to_remove = []
        
        for user_id, session in self._sessions.items():
            if (now - session.last_activity).total_seconds() > max_idle_hours * 3600:
                to_remove.append(user_id)
        
        for user_id in to_remove:
            self.remove_session(user_id)
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive sessions")
        
        return len(to_remove)


# Global session manager instance
session_manager = SessionManager()
