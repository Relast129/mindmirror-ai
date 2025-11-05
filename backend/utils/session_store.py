"""
Session Store - In-memory session management with TTL
WARNING: Sessions will be lost on container restart (HF Spaces limitation)
For production, use Redis or encrypted database.
"""

import time
import secrets
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)

class SessionStore:
    """In-memory session storage with TTL and automatic cleanup."""
    
    def __init__(self):
        self._sessions = {}  # {session_token: (data, expiry_timestamp)}
        self._lock = Lock()
        self._cleanup_interval = 300  # Cleanup every 5 minutes
        self._last_cleanup = time.time()
    
    def set_session(self, token: str, data: Dict[str, Any], ttl: int = 3600):
        """
        Store session data.
        
        Args:
            token: Session token
            data: Session data dictionary
            ttl: Time to live in seconds (default 1 hour)
        """
        with self._lock:
            expiry = time.time() + ttl
            self._sessions[token] = (data, expiry)
            logger.info(f"Session created with TTL {ttl}s")
            
            # Periodic cleanup
            if time.time() - self._last_cleanup > self._cleanup_interval:
                self._cleanup_expired()
    
    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data.
        
        Args:
            token: Session token
            
        Returns:
            Session data or None if expired/not found
        """
        with self._lock:
            if token not in self._sessions:
                return None
            
            data, expiry = self._sessions[token]
            
            # Check if expired
            if time.time() > expiry:
                del self._sessions[token]
                logger.info("Session expired and removed")
                return None
            
            return data
    
    def delete_session(self, token: str):
        """Delete a session."""
        with self._lock:
            if token in self._sessions:
                del self._sessions[token]
                logger.info("Session deleted")
    
    def refresh_session(self, token: str, ttl: int = 3600) -> bool:
        """
        Refresh session TTL.
        
        Args:
            token: Session token
            ttl: New TTL in seconds
            
        Returns:
            True if refreshed, False if not found
        """
        with self._lock:
            if token not in self._sessions:
                return False
            
            data, _ = self._sessions[token]
            expiry = time.time() + ttl
            self._sessions[token] = (data, expiry)
            logger.info(f"Session refreshed with TTL {ttl}s")
            return True
    
    def _cleanup_expired(self):
        """Remove expired sessions."""
        current_time = time.time()
        expired_tokens = [
            token for token, (_, expiry) in self._sessions.items()
            if current_time > expiry
        ]
        
        for token in expired_tokens:
            del self._sessions[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
        
        self._last_cleanup = current_time
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        with self._lock:
            return len(self._sessions)
