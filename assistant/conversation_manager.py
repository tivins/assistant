#!/usr/bin/env python3
"""
Conversation Manager
Handles conversation history and message management.
"""

from datetime import datetime
from typing import List, Dict, Any


class ConversationManager:
    """Manages conversation history and message handling."""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str) -> Dict[str, str]:
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        return message
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def set_history(self, history: List[Dict[str, str]]):
        """Set conversation history."""
        self.conversation_history = history.copy()
    
    def get_history_length(self) -> int:
        """Get number of messages in history."""
        return len(self.conversation_history)
