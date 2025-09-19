#!/usr/bin/env python3
"""
Terminal AI Assistant Package
A modular AI assistant with separated responsibilities.
"""

from .ai_client import AIClient
from .archive_manager import ArchiveManager
from .command_processor import CommandProcessor
from .conversation_manager import ConversationManager
from .script_executor import ScriptExecutor

__all__ = [
    'AIClient',
    'ArchiveManager', 
    'CommandProcessor',
    'ConversationManager',
    'ScriptExecutor'
]
