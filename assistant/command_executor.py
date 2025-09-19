#!/usr/bin/env python3
"""
Command Executor
Handles system command execution with safety controls.
"""

import subprocess
import sys
import os
import shlex
from pathlib import Path
from typing import List, Tuple, Optional


class CommandExecutor:
    """Manages system command execution with safety controls."""
    
    # Allowed commands for security
    ALLOWED_COMMANDS = {
        'cd', 'ls', 'cat', 'echo', 'pwd', 'mkdir', 'rmdir', 'touch', 
        'cp', 'mv', 'rm', 'grep', 'find', 'head', 'tail', 'wc', 'sort',
        'ps', 'top', 'df', 'du', 'free', 'uname', 'whoami', 'date',
        'python', 'python3', 'pip', 'git', 'git status', 'git log',
        'git add', 'git commit', 'git push', 'git pull', 'git clone',
        # Windows commands
        'dir', 'type', 'copy', 'move', 'del', 'ren', 'md', 'rd'
    }
    
    def __init__(self):
        self.current_dir = os.getcwd()
    
    def is_command_allowed(self, command: str) -> bool:
        """Check if a command is in the allowed list."""
        # Extract the base command (first word)
        base_command = command.split()[0] if command.split() else ""
        
        # Check if the base command is allowed
        if base_command in self.ALLOWED_COMMANDS:
            return True
        
        # Special case for Windows cd command with /d flag
        if base_command == 'cd' and '/d' in command:
            return True
        
        # Special case for Windows dir command
        if base_command == 'dir':
            return True
        
        return False
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a system command safely.
        Returns (return_code, stdout, stderr)
        """
        if not self.is_command_allowed(command):
            return 1, "", f"Command '{command}' is not allowed for security reasons"
        
        try:
            # Handle cd command specially as it needs to change directory
            if command.startswith('cd '):
                return self._handle_cd_command(command)
            
            # Execute other commands
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.current_dir
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return 1, "", "Command execution timed out after 30 seconds"
        except Exception as e:
            return 1, "", f"Error executing command: {e}"
    
    def _handle_cd_command(self, command: str) -> Tuple[int, str, str]:
        """Handle cd command by changing the current working directory."""
        try:
            # Extract the directory from 'cd <directory>'
            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                # Just 'cd' - go to home directory
                new_dir = os.path.expanduser("~")
            else:
                new_dir = parts[1]
            
            # Resolve the path
            if os.path.isabs(new_dir):
                target_dir = new_dir
            else:
                target_dir = os.path.join(self.current_dir, new_dir)
            
            # Check if directory exists
            if not os.path.isdir(target_dir):
                return 1, "", f"Directory '{target_dir}' does not exist"
            
            # Change directory
            self.current_dir = os.path.abspath(target_dir)
            return 0, f"Changed directory to: {self.current_dir}", ""
            
        except Exception as e:
            return 1, "", f"Error changing directory: {e}"
    
    def get_current_directory(self) -> str:
        """Get the current working directory."""
        return self.current_dir
    
    def get_allowed_commands(self) -> List[str]:
        """Get list of allowed commands."""
        return sorted(list(self.ALLOWED_COMMANDS))
