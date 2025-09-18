#!/usr/bin/env python3
"""
Setup script for Terminal AI Assistant
Creates virtual environment and installs dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error {description}: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def create_virtual_environment():
    """Create virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    # Create virtual environment
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    return True

def get_activation_command():
    """Get the activation command based on the platform."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def get_python_command():
    """Get the Python command for the virtual environment."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\python"
    else:
        return "venv/bin/python"

def get_pip_command():
    """Get the pip command for the virtual environment."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"

def install_dependencies():
    """Install project dependencies."""
    python_cmd = get_python_command()
    pip_cmd = get_pip_command()
    
    # Upgrade pip first using python -m pip (recommended method)
    if not run_command(f"{python_cmd} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Failed to upgrade pip, continuing with current version")
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements"):
        return False
    
    # Install optional script dependencies
    scripts_req = Path("scripts/requirements.txt")
    if scripts_req.exists():
        if not run_command(f"{pip_cmd} install -r scripts/requirements.txt", "Installing script requirements"):
            print("⚠️  Warning: Some script dependencies failed to install")
    
    return True

def create_activation_scripts():
    """Create platform-specific activation scripts."""
    
    # Windows batch file
    with open("activate.bat", "w", encoding="utf-8") as f:
        f.write("""@echo off
echo Activating Terminal AI Assistant environment...
call venv\\Scripts\\activate.bat
echo Virtual environment activated!
echo.
echo To run the assistant: python main.py
echo To deactivate: deactivate
""")
    
    # Unix shell script
    with open("activate.sh", "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
echo "Activating Terminal AI Assistant environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo ""
echo "To run the assistant: python main.py"
echo "To deactivate: deactivate"
""")
    
    # PowerShell script
    with open("activate.ps1", "w", encoding="utf-8") as f:
        f.write("""# Terminal AI Assistant Environment Activation
Write-Host "Activating Terminal AI Assistant environment..." -ForegroundColor Green
& "venv\\Scripts\\Activate.ps1"
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the assistant: python main.py" -ForegroundColor Yellow
Write-Host "To deactivate: deactivate" -ForegroundColor Yellow
""")
    
    # Make shell script executable on Unix
    if platform.system() != "Windows":
        os.chmod("activate.sh", 0o755)

def main():
    """Main setup function."""
    print("🚀 Setting up Terminal AI Assistant")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create activation scripts
    create_activation_scripts()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    
    if platform.system() == "Windows":
        print("   - Run: activate.bat")
        print("   - Or: activate.ps1 (PowerShell)")
    else:
        print("   - Run: source activate.sh")
    
    print("2. Install Ollama from https://ollama.ai")
    print("3. Pull a model: ollama pull llama3.2")
    print("4. Run the assistant: python main.py")
    
    print(f"\n💡 Virtual environment location: {Path('venv').absolute()}")

if __name__ == "__main__":
    main()
