#!/usr/bin/env python3
"""
Script Executor
Handles script discovery, execution, and management.
"""

import subprocess
import sys
from pathlib import Path
from typing import List


class ScriptExecutor:
    """Manages script execution and discovery."""
    
    def __init__(self, scripts_dir: str = "./scripts"):
        self.scripts_dir = Path(scripts_dir)
        self.scripts_dir.mkdir(exist_ok=True)
    
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
    
    def get_scripts_info(self) -> str:
        """Get information about available scripts."""
        scripts = self.list_scripts()
        if scripts:
            return f"Available scripts:\n" + "\n".join(f"  - {s}" for s in scripts)
        else:
            return "No scripts found in ./scripts directory"
