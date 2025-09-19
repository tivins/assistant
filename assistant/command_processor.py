#!/usr/bin/env python3
"""
Command Processor
Handles special command parsing and routing.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json


class CommandProcessor:
    """Processes special commands and routes them to appropriate handlers."""
    
    def __init__(self, ai_client, script_executor, archive_manager):
        self.ai_client = ai_client
        self.script_executor = script_executor
        self.archive_manager = archive_manager
    
    def process_command(self, user_input: str, conversation_history: List[Dict[str, str]]) -> Optional[str]:
        """Process special commands and return result or None if not a command."""
        command = user_input.strip().lower()
        
        if command in ['/help', '/h']:
            return self._show_help()
        elif command in ['/scripts', '/s']:
            return self.script_executor.get_scripts_info()
        elif command.startswith('/execute '):
            script_name = user_input[9:].strip()
            return self.script_executor.execute_script(script_name)
        elif command.startswith('/save'):
            filename = user_input[6:].strip() or None
            return self._save_conversation(conversation_history, filename)
        elif command.startswith('/load '):
            filename = user_input[6:].strip()
            return self._load_conversation(filename)
        elif command in ['/clear', '/c']:
            return "Conversation history cleared"
        elif command in ['/history', '/hist']:
            return self._show_history(conversation_history)
        elif command.startswith('/model '):
            new_model = user_input[7:].strip()
            return self.ai_client.change_model(new_model)
        elif command in ['/info', '/i']:
            return self._show_info(conversation_history)
        elif command in ['/archive', '/a']:
            return self.archive_manager.get_archive_status()
        elif command == '/archive-list':
            return self.archive_manager.list_archived_conversations()
        elif command.startswith('/archive-view '):
            session_id = user_input[14:].strip()
            return self.archive_manager.view_archived_conversation(session_id)
        elif command == '/archive-toggle':
            return self.archive_manager.toggle_auto_archive(conversation_history, self.ai_client.model)
        elif command == '/archive-save':
            return self.archive_manager.manual_archive_save(conversation_history, self.ai_client.model)
        elif command == '/archive-clear':
            return self.archive_manager.clear_current_session()
        elif command.startswith('/archive-resume '):
            session_id = user_input[16:].strip()
            message, messages = self.archive_manager.resume_archived_conversation(session_id)
            if messages:
                # Set the conversation history to the resumed messages
                conversation_history.clear()
                conversation_history.extend(messages)
            return message
        elif command in ['/quit', '/q']:
            return "quit"
        else:
            return None  # Not a special command
    
    def _show_help(self) -> str:
        """Show available commands."""
        return """
Available commands:
- /help or /h          - Show this help message
- /scripts or /s       - List available scripts
- /execute <script>    - Execute a script
- /save [filename]     - Save conversation to file
- /load <filename>     - Load conversation from file
- /clear or /c         - Clear conversation history
- /history or /hist    - Show conversation history
- /quit or /q          - Exit the assistant
- /model <name>        - Change AI model
- /info or /i          - Show assistant info

Archive commands:
- /archive or /a       - Show archive status and commands
- /archive-list        - List archived conversations
- /archive-view <id>   - View specific archived conversation
- /archive-toggle      - Toggle auto-archiving on/off
- /archive-save        - Manually save current conversation

Just type your message to chat with the AI assistant.
"""
    
    def _show_history(self, conversation_history: List[Dict[str, str]]) -> str:
        """Show conversation history."""
        if not conversation_history:
            return "No conversation history"
        
        history_text = "Conversation History:\n"
        for i, msg in enumerate(conversation_history, 1):
            role = msg['role'].upper()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            history_text += f"{i}. [{role}] {content}\n"
        return history_text
    
    def _show_info(self, conversation_history: List[Dict[str, str]]) -> str:
        """Show assistant information."""
        return f"""
Terminal AI Assistant
Model: {self.ai_client.model}
Scripts Directory: {self.script_executor.scripts_dir}
Archive Directory: {self.archive_manager.archive_dir}
Conversation Length: {len(conversation_history)} messages
Available Scripts: {len(self.script_executor.list_scripts())}
Auto-Archive: {'Enabled' if self.archive_manager.auto_archive else 'Disabled'}
Current Session: {self.archive_manager.current_session_file.name if self.archive_manager.current_session_file else 'None'}
"""
    
    def _save_conversation(self, conversation_history: List[Dict[str, str]], filename: str = None) -> str:
        """Save conversation history to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_history, f, indent=2, ensure_ascii=False)
        
        return f"Conversation saved to {filepath}"
    
    def _load_conversation(self, filename: str) -> tuple[str, List[Dict[str, str]]]:
        """Load conversation history from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                conversation_history = json.load(f)
            return f"Loaded conversation from {filename}", conversation_history
        except Exception as e:
            return f"Error loading conversation: {e}", []
