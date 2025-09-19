#!/usr/bin/env python3
"""
Terminal AI Assistant
A command-line AI assistant that integrates with Ollama and can execute system commands.
"""

import sys
import argparse
from assistant import AIClient, ArchiveManager, CommandProcessor, ConversationManager, CommandExecutor


class TerminalAIAssistant:
    def __init__(self, model: str = "llama3.2:3B", archive_dir: str = "./conversations"):
        # Initialize components
        self.ai_client = AIClient(model)
        self.command_executor = CommandExecutor()
        self.archive_manager = ArchiveManager(archive_dir)
        self.conversation_manager = ConversationManager()
        self.command_processor = CommandProcessor(
            self.ai_client, 
            self.command_executor, 
            self.archive_manager
        )
    
    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history."""
        message = self.conversation_manager.add_message(role, content)
        
        # Auto-archive if enabled
        self.archive_manager.archive_message(message, self.ai_client.model)
    
    def resume_archived_conversation(self, session_id: str):
        """Resume a specific archived conversation and continue it."""
        message, messages = self.archive_manager.resume_archived_conversation(session_id)
        if messages:
            self.conversation_manager.set_history(messages)
        return message


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
- Execute system commands safely
- Help with coding, debugging, and system administration
- Provide explanations and guidance

When you want to execute a system command, you MUST use the EXACT format: [EXECUTE:command] in your response.
IMPORTANT: Always include the square brackets [ ] around EXECUTE:command
Example: [EXECUTE:ls -la] or [EXECUTE:cd /home/user]
The user will see this and can choose to run it.

Available commands include: cd, ls, cat, echo, pwd, mkdir, touch, cp, mv, rm, grep, find, python, git, etc."""
            }
        ]
        
        # Add conversation history
        messages.extend(self.conversation_manager.get_history())
        
        # Get AI response
        ai_response = self.ai_client.get_ai_response(messages)
        self.add_to_history("assistant", ai_response)
        return ai_response
    
    def list_commands(self):
        """List available system commands."""
        return self.command_executor.get_allowed_commands()
    
    def execute_command(self, command: str) -> str:
        """Execute a system command."""
        return_code, stdout, stderr = self.command_executor.execute_command(command)
        result = f"Executed: {command}\nExit code: {return_code}\n"
        if stdout:
            result += f"Output:\n{stdout}\n"
        if stderr:
            result += f"Error:\n{stderr}\n"
        return result
    
    def save_conversation(self, filename: str = None):
        """Save conversation history to a JSON file."""
        return self.command_processor._save_conversation(self.conversation_manager.get_history(), filename)
    
    def load_conversation(self, filename: str):
        """Load conversation history from a JSON file."""
        message, history = self.command_processor._load_conversation(filename)
        if history:
            self.conversation_manager.set_history(history)
        return message
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_manager.clear_history()
        return "Conversation history cleared"
    
    
    def process_command(self, user_input: str) -> str:
        """Process special commands."""
        return self.command_processor.process_command(user_input, self.conversation_manager.get_history())
    
    def run(self):
        """Main run loop."""
        print("🤖 Terminal AI Assistant")
        print("Type '/help' for available commands or start chatting!")
        print("=" * 50)
        
        # Start auto-archiving
        if self.archive_manager.auto_archive:
            self.archive_manager.start_auto_archive(
                self.conversation_manager.get_history(), 
                self.ai_client.model
            )
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
                
                # Check if this is an approval response for pending commands
                if self.command_processor.pending_commands:
                    if self.command_processor.approval_analyzer.analyze_approval_response(user_input):
                        print("\n✅ Executing approved commands:")
                        result = self.command_processor._execute_pending_commands()
                        print(result)
                        continue
                    else:
                        self.command_processor.pending_commands = []
                        print("❌ Command execution cancelled.")
                        continue
                
                # Get AI response
                print("\n🤖 AI Assistant:")
                response = self.get_ai_response(user_input)
                print(response)
                
                # Check for command execution suggestions
                if "[EXECUTE:" in response:
                    # Extract and store commands for approval
                    execute_commands = self.command_processor._extract_execute_commands(response)
                    if execute_commands:
                        self.command_processor.pending_commands = execute_commands
                        print("\n" + "="*50)
                        print("The AI suggested executing commands. Type 'yes'/'oui' to approve or use /approve.")
                        print("="*50)
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
        except EOFError:
            print("\n\nGoodbye! 👋")
        except Exception as e:
            print(f"\nError: {e}")
        
        finally:
            # Stop auto-archiving when exiting
            self.archive_manager.stop_auto_archive()
            if self.archive_manager.auto_archive and self.archive_manager.current_session_file:
                print(f"📁 Final conversation saved to: {self.archive_manager.current_session_file.name}")

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
    parser.add_argument("--archive-dir", "-a", default="./conversations", help="Archive directory")
    parser.add_argument("--skip-venv-check", action="store_true", help="Skip virtual environment check")
    
    args = parser.parse_args()
    
    # Check virtual environment unless explicitly skipped
    if not args.skip_venv_check:
        check_virtual_environment()
    
    assistant = TerminalAIAssistant(model=args.model, archive_dir=args.archive_dir)
    assistant.run()

if __name__ == "__main__":
    main()
