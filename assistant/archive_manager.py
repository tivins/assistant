#!/usr/bin/env python3
"""
Archive Manager
Handles conversation archiving, session management, and conversation persistence.
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class ArchiveManager:
    """Manages conversation archiving and session persistence."""
    
    def __init__(self, archive_dir: str = "./conversations"):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(exist_ok=True)
        
        # Real-time archiving settings
        self.auto_archive = True
        self.archive_interval = 5  # seconds
        self.current_session_file: Optional[Path] = None
        self.archive_thread: Optional[threading.Thread] = None
        self.stop_archive = False
    
    def _get_session_filename(self) -> str:
        """Generate a unique session filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}.json"
    
    def _archive_message(self, message: Dict[str, str], model: str):
        """Archive a single message to the current session file."""
        if not self.current_session_file:
            self.current_session_file = self.archive_dir / self._get_session_filename()
        
        try:
            # Load existing session data or create new
            if self.current_session_file.exists():
                with open(self.current_session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
            else:
                session_data = {
                    "session_id": self.current_session_file.stem,
                    "model": model,
                    "start_time": datetime.now().isoformat(),
                    "messages": []
                }
            
            # Add the new message
            session_data["messages"].append(message)
            session_data["last_updated"] = datetime.now().isoformat()
            
            # Save to file
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to archive message: {e}")
    
    def _archive_full_conversation(self, conversation_history: List[Dict[str, str]], model: str):
        """Archive the complete conversation to a session file."""
        if not self.current_session_file:
            self.current_session_file = self.archive_dir / self._get_session_filename()
        
        try:
            session_data = {
                "session_id": self.current_session_file.stem,
                "model": model,
                "start_time": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "message_count": len(conversation_history),
                "messages": conversation_history.copy()
            }
            
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to archive conversation: {e}")
    
    def _archive_worker(self, conversation_history: List[Dict[str, str]], model: str):
        """Background worker for periodic archiving."""
        while not self.stop_archive:
            try:
                if conversation_history and self.auto_archive:
                    self._archive_full_conversation(conversation_history, model)
                time.sleep(self.archive_interval)
            except Exception as e:
                print(f"Archive worker error: {e}")
                time.sleep(self.archive_interval)
    
    def start_auto_archive(self, conversation_history: List[Dict[str, str]], model: str):
        """Start the automatic archiving thread."""
        if self.archive_thread and self.archive_thread.is_alive():
            return
        
        self.stop_archive = False
        self.archive_thread = threading.Thread(
            target=self._archive_worker, 
            args=(conversation_history, model),
            daemon=True
        )
        self.archive_thread.start()
    
    def stop_auto_archive(self):
        """Stop the automatic archiving thread."""
        self.stop_archive = True
        if self.archive_thread:
            self.archive_thread.join(timeout=1)
    
    def archive_message(self, message: Dict[str, str], model: str):
        """Archive a single message if auto-archiving is enabled."""
        if self.auto_archive:
            self._archive_message(message, model)
    
    def manual_archive_save(self, conversation_history: List[Dict[str, str]], model: str) -> str:
        """Manually save the current conversation."""
        if not conversation_history:
            return "No conversation to save."
        
        try:
            self._archive_full_conversation(conversation_history, model)
            return f"Conversation saved to: {self.current_session_file.name}"
        except Exception as e:
            return f"Error saving conversation: {e}"
    
    def clear_current_session(self):
        """Clear current session and start a new one."""
        self.current_session_file = None
        return "Current session cleared. New conversation will start fresh."
    
    def toggle_auto_archive(self, conversation_history: List[Dict[str, str]], model: str) -> str:
        """Toggle auto-archiving on/off."""
        self.auto_archive = not self.auto_archive
        
        if self.auto_archive:
            self.start_auto_archive(conversation_history, model)
            return "Auto-archiving enabled. Conversations will be saved automatically."
        else:
            self.stop_auto_archive()
            return "Auto-archiving disabled. Conversations will not be saved automatically."
    
    def list_archived_conversations(self) -> str:
        """List all archived conversations."""
        if not self.archive_dir.exists():
            return "No archive directory found"
        
        archive_files = list(self.archive_dir.glob("session_*.json"))
        if not archive_files:
            return "No archived conversations found"
        
        # Sort by modification time (newest first)
        archive_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        result = "Archived Conversations:\n"
        for i, file_path in enumerate(archive_files, 1):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                session_id = data.get('session_id', file_path.stem)
                message_count = data.get('message_count', len(data.get('messages', [])))
                start_time = data.get('start_time', 'Unknown')
                model = data.get('model', 'Unknown')
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_time = start_time
                
                result += f"{i:2d}. {session_id}\n"
                result += f"    Model: {model} | Messages: {message_count} | Started: {formatted_time}\n"
                
            except Exception as e:
                result += f"{i:2d}. {file_path.name} (Error reading: {e})\n"
        
        return result
    
    def view_archived_conversation(self, session_id: str) -> str:
        """View a specific archived conversation."""
        if not session_id:
            return "Please provide a session ID. Use /archive-list to see available sessions."
        
        # Try to find the session file
        session_file = None
        if session_id.isdigit():
            # If it's a number, treat it as an index from the list
            archive_files = sorted(self.archive_dir.glob("session_*.json"), 
                                 key=lambda x: x.stat().st_mtime, reverse=True)
            try:
                index = int(session_id) - 1
                if 0 <= index < len(archive_files):
                    session_file = archive_files[index]
            except ValueError:
                pass
        
        if not session_file:
            # Try to find by partial name match
            for file_path in self.archive_dir.glob("session_*.json"):
                if session_id in file_path.stem:
                    session_file = file_path
                    break
        
        if not session_file or not session_file.exists():
            return f"Session '{session_id}' not found. Use /archive-list to see available sessions."
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            result = f"Session: {data.get('session_id', 'Unknown')}\n"
            result += f"Model: {data.get('model', 'Unknown')}\n"
            result += f"Messages: {data.get('message_count', 0)}\n"
            result += f"Started: {data.get('start_time', 'Unknown')}\n"
            result += f"Last Updated: {data.get('last_updated', 'Unknown')}\n"
            result += "=" * 50 + "\n\n"
            
            messages = data.get('messages', [])
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')
                
                # Truncate long messages
                if len(content) > 200:
                    content = content[:200] + "..."
                
                result += f"{i:3d}. [{role}] {content}\n"
                if timestamp:
                    result += f"     Time: {timestamp}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error reading session file: {e}"
    
    def resume_archived_conversation(self, session_id: str) -> tuple[str, List[Dict[str, str]]]:
        """Resume a specific archived conversation and return the messages."""
        # Find the corresponding archive file
        session_file = None
        for file_path in self.archive_dir.glob("session_*.json"):
            if session_id in file_path.stem:
                session_file = file_path
                break

        if not session_file or not session_file.exists():
            return f"Session '{session_id}' not found. Use /archive-list to see available sessions.", []

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            messages = data.get("messages", [])
            self.current_session_file = session_file  # resume on the same file
            
            # Use view_archived_conversation for formatted display
            formatted_view = self.view_archived_conversation(session_id)
            return f"✅ Resumed conversation '{data.get('session_id', session_file.stem)}' with {len(messages)} messages.\n\n{formatted_view}", messages

        except Exception as e:
            return f"Error resuming session: {e}", []
    
    def get_archive_status(self) -> str:
        """Get archive status information."""
        return f"""
Archive Status:
- Auto-Archive: {'Enabled' if self.auto_archive else 'Disabled'}
- Archive Directory: {self.archive_dir}
- Current Session: {self.current_session_file.name if self.current_session_file else 'None'}

Archive Commands:
- /archive-list        - List all archived conversations
- /archive-view <id>   - View specific archived conversation
- /archive-toggle      - Toggle auto-archiving on/off
- /archive-save        - Manually save current conversation
- /archive-clear       - Clear current session (start new)
- /archive-resume <id> - Resume a specific archived conversation
"""
