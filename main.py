#!/usr/bin/env python3
"""
Terminal AI Assistant
A command-line AI assistant that integrates with Ollama and can execute scripts.
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from typing import List, Dict, Any
import ollama
from pathlib import Path
import threading
import time

class TerminalAIAssistant:
    def __init__(self, model: str = "llama3.2:3B", scripts_dir: str = "./scripts", archive_dir: str = "./conversations"):
        self.model = model
        self.scripts_dir = Path(scripts_dir)
        self.archive_dir = Path(archive_dir)
        self.conversation_history: List[Dict[str, str]] = []
        self.scripts_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        
        # Real-time archiving settings
        self.auto_archive = True
        self.archive_interval = 5  # seconds
        self.current_session_file = None
        self.archive_thread = None
        self.stop_archive = False
        
        # Initialize Ollama client
        try:
            self.client = ollama.Client()
            # Test connection
            self.client.list()
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running and accessible.")
            sys.exit(1)
    
    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        
        # Auto-archive if enabled
        if self.auto_archive:
            self._archive_message(message)
    
    def _get_session_filename(self) -> str:
        """Generate a unique session filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}.json"
    
    def _archive_message(self, message: Dict[str, str]):
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
                    "model": self.model,
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
    
    def start_auto_archive(self):
        """Start the automatic archiving thread."""
        if self.archive_thread and self.archive_thread.is_alive():
            return
        
        self.stop_archive = False
        self.archive_thread = threading.Thread(target=self._archive_worker, daemon=True)
        self.archive_thread.start()
    
    def stop_auto_archive(self):
        """Stop the automatic archiving thread."""
        self.stop_archive = True
        if self.archive_thread:
            self.archive_thread.join(timeout=1)
    
    def _archive_worker(self):
        """Background worker for periodic archiving."""
        while not self.stop_archive:
            try:
                if self.conversation_history and self.auto_archive:
                    self._archive_full_conversation()
                time.sleep(self.archive_interval)
            except Exception as e:
                print(f"Archive worker error: {e}")
                time.sleep(self.archive_interval)
    
    def _archive_full_conversation(self):
        """Archive the complete conversation to a session file."""
        if not self.current_session_file:
            self.current_session_file = self.archive_dir / self._get_session_filename()
        
        try:
            session_data = {
                "session_id": self.current_session_file.stem,
                "model": self.model,
                "start_time": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "message_count": len(self.conversation_history),
                "messages": self.conversation_history.copy()
            }
            
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to archive conversation: {e}")

    def resume_archived_conversation(self, session_id: str):
        """Resume a specific archived conversation and continue it."""
        # Trouver le fichier d’archive correspondant
        session_file = None
        for file_path in self.archive_dir.glob("session_*.json"):
            if session_id in file_path.stem:
                session_file = file_path
                break

        if not session_file or not session_file.exists():
            return f"Session '{session_id}' not found. Use /archive-list to see available sessions."

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.conversation_history = data.get("messages", [])
            self.current_session_file = session_file  # reprendre sur le même fichier
            return f"✅ Resumed conversation '{data.get('session_id', session_file.stem)}' with {len(self.conversation_history)} messages."

        except Exception as e:
            return f"Error resuming session: {e}"


    def get_ai_response(self, user_input: str) -> str:
        """Get AI response from Ollama with full conversation context."""
        # Add user input to history
        self.add_to_history("user", user_input)
        
        # Prepare messages for Ollama (including system prompt and history)
        messages = [
            {
                "role": "system",
                "content": """You are a helpful terminal AI assistant. You can:
- Answer questions and provide assistance
- Execute scripts from the ./scripts folder
- Help with coding, debugging, and system administration
- Provide explanations and guidance

When you want to execute a script, use the format: [EXECUTE_SCRIPT:filename.py] in your response.
The user will see this and can choose to run it."""
            }
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=False
            )
            
            ai_response = response['message']['content']
            self.add_to_history("assistant", ai_response)
            return ai_response
            
        except Exception as e:
            error_msg = f"Error getting AI response: {e}"
            self.add_to_history("assistant", error_msg)
            return error_msg
    
    def list_scripts(self) -> List[str]:
        """List available scripts in the scripts directory."""
        if not self.scripts_dir.exists():
            return []
        
        scripts = []
        for file in self.scripts_dir.iterdir():
            if file.is_file() and file.suffix in ['.py', '.sh', '.bat', '.ps1']:
                scripts.append(file.name)
        return sorted(scripts)
    
    def execute_script(self, script_name: str) -> str:
        """Execute a script from the scripts directory."""
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            return f"Script '{script_name}' not found in {self.scripts_dir}"
        
        try:
            if script_name.endswith('.py'):
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif script_name.endswith('.sh'):
                result = subprocess.run(
                    ['bash', str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif script_name.endswith('.bat'):
                result = subprocess.run(
                    [str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif script_name.endswith('.ps1'):
                result = subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                return f"Unsupported script type: {script_name}"
            
            output = f"Exit code: {result.returncode}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Script execution timed out after 30 seconds"
        except Exception as e:
            return f"Error executing script: {e}"
    
    def save_conversation(self, filename: str = None):
        """Save conversation history to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def load_conversation(self, filename: str):
        """Load conversation history from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            return f"Loaded conversation from {filename}"
        except Exception as e:
            return f"Error loading conversation: {e}"
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        return "Conversation history cleared"
    
    def show_help(self):
        """Show available commands."""
        help_text = """
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
        return help_text
    
    def show_info(self):
        """Show assistant information."""
        info = f"""
Terminal AI Assistant
Model: {self.model}
Scripts Directory: {self.scripts_dir}
Archive Directory: {self.archive_dir}
Conversation Length: {len(self.conversation_history)} messages
Available Scripts: {len(self.list_scripts())}
Auto-Archive: {'Enabled' if self.auto_archive else 'Disabled'}
Current Session: {self.current_session_file.name if self.current_session_file else 'None'}
"""
        return info
    
    def show_archive_status(self):
        """Show archive status and available commands."""
        status = f"""
Archive Status:
- Auto-Archive: {'Enabled' if self.auto_archive else 'Disabled'}
- Archive Directory: {self.archive_dir}
- Current Session: {self.current_session_file.name if self.current_session_file else 'None'}
- Messages in Session: {len(self.conversation_history)}

Archive Commands:
- /archive-list        - List all archived conversations
- /archive-view <id>   - View specific archived conversation
- /archive-toggle      - Toggle auto-archiving on/off
- /archive-save        - Manually save current conversation
- /archive-clear       - Clear current session (start new)
- /archive-resume <id> - Resume a specific archived conversation
"""
        return status
    
    def list_archived_conversations(self):
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
    
    def view_archived_conversation(self, session_id: str):
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
    
    def toggle_auto_archive(self):
        """Toggle auto-archiving on/off."""
        self.auto_archive = not self.auto_archive
        
        if self.auto_archive:
            self.start_auto_archive()
            return "Auto-archiving enabled. Conversations will be saved automatically."
        else:
            self.stop_auto_archive()
            return "Auto-archiving disabled. Conversations will not be saved automatically."
    
    def manual_archive_save(self):
        """Manually save the current conversation."""
        if not self.conversation_history:
            return "No conversation to save."
        
        try:
            self._archive_full_conversation()
            return f"Conversation saved to: {self.current_session_file.name}"
        except Exception as e:
            return f"Error saving conversation: {e}"
    
    def clear_current_session(self):
        """Clear current session and start a new one."""
        self.conversation_history = []
        self.current_session_file = None
        return "Current session cleared. New conversation will start fresh."
    
    def process_command(self, user_input: str) -> str:
        """Process special commands."""
        command = user_input.strip().lower()
        
        if command in ['/help', '/h']:
            return self.show_help()
        elif command in ['/scripts', '/s']:
            scripts = self.list_scripts()
            if scripts:
                return f"Available scripts:\n" + "\n".join(f"  - {s}" for s in scripts)
            else:
                return "No scripts found in ./scripts directory"
        elif command.startswith('/execute '):
            script_name = user_input[9:].strip()
            return self.execute_script(script_name)
        elif command.startswith('/save'):
            filename = user_input[6:].strip() or None
            filepath = self.save_conversation(filename)
            return f"Conversation saved to {filepath}"
        elif command.startswith('/load '):
            filename = user_input[6:].strip()
            return self.load_conversation(filename)
        elif command in ['/clear', '/c']:
            return self.clear_history()
        elif command in ['/history', '/hist']:
            if not self.conversation_history:
                return "No conversation history"
            
            history_text = "Conversation History:\n"
            for i, msg in enumerate(self.conversation_history, 1):
                role = msg['role'].upper()
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                history_text += f"{i}. [{role}] {content}\n"
            return history_text
        elif command.startswith('/model '):
            new_model = user_input[7:].strip()
            try:
                # Test if model exists
                models = self.client.list()
                available_models = [m['name'] for m in models['models']]
                if new_model in available_models:
                    self.model = new_model
                    return f"Model changed to {new_model}"
                else:
                    return f"Model {new_model} not found. Available models: {', '.join(available_models)}"
            except Exception as e:
                return f"Error changing model: {e}"
        elif command in ['/info', '/i']:
            return self.show_info()
        elif command in ['/archive', '/a']:
            return self.show_archive_status()
        elif command == '/archive-list':
            return self.list_archived_conversations()
        elif command.startswith('/archive-view '):
            session_id = user_input[14:].strip()
            return self.view_archived_conversation(session_id)
        elif command == '/archive-toggle':
            return self.toggle_auto_archive()
        elif command == '/archive-save':
            return self.manual_archive_save()
        elif command == '/archive-clear':
            return self.clear_current_session()
        elif command.startswith('/archive-resume '):
            session_id = user_input[16:].strip()
            return self.resume_archived_conversation(session_id)
         
        elif command in ['/quit', '/q']:
            return "quit"
        else:
            return None  # Not a special command
    
    def run(self):
        """Main run loop."""
        print("🤖 Terminal AI Assistant")
        print("Type '/help' for available commands or start chatting!")
        print("=" * 50)
        
        # Start auto-archiving
        if self.auto_archive:
            self.start_auto_archive()
            print("📁 Auto-archiving enabled. Conversations will be saved automatically.")
        
        try:
            while True:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Check for special commands
                command_result = self.process_command(user_input)
                if command_result is not None:
                    if command_result == "quit":
                        print("Goodbye! 👋")
                        break
                    print(command_result)
                    continue
                
                # Get AI response
                print("\n🤖 AI Assistant:")
                response = self.get_ai_response(user_input)
                print(response)
                
                # Check for script execution suggestions
                if "[EXECUTE_SCRIPT:" in response:
                    print("\n" + "="*50)
                    print("The AI suggested executing a script. Use '/execute <script_name>' to run it.")
                    print("="*50)
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
        except EOFError:
            print("\n\nGoodbye! 👋")
        except Exception as e:
            print(f"\nError: {e}")
        
        finally:
            # Stop auto-archiving when exiting
            self.stop_auto_archive()
            if self.auto_archive and self.current_session_file:
                print(f"📁 Final conversation saved to: {self.current_session_file.name}")

def check_virtual_environment():
    """Check if running in a virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️  WARNING: You are not running in a virtual environment!")
        print("It's recommended to use a virtual environment for this project.")
        print("Run 'python setup.py' to create and setup a virtual environment.")
        print("Or manually create one with: python -m venv venv")
        print()
        
        response = input("Do you want to continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting. Please setup a virtual environment first.")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Terminal AI Assistant")
    parser.add_argument("--model", "-m", default="llama3.2", help="Ollama model to use")
    parser.add_argument("--scripts-dir", "-s", default="./scripts", help="Scripts directory")
    parser.add_argument("--archive-dir", "-a", default="./conversations", help="Archive directory")
    parser.add_argument("--skip-venv-check", action="store_true", help="Skip virtual environment check")
    
    args = parser.parse_args()
    
    # Check virtual environment unless explicitly skipped
    if not args.skip_venv_check:
        check_virtual_environment()
    
    assistant = TerminalAIAssistant(model=args.model, scripts_dir=args.scripts_dir, archive_dir=args.archive_dir)
    assistant.run()

if __name__ == "__main__":
    main()
