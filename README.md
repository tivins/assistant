# Terminal AI Assistant

A powerful command-line AI assistant that integrates with Ollama and can execute scripts from a dedicated scripts folder.

## Features

- 🤖 **AI Chat**: Interactive conversation with Ollama models
- 📝 **Context Management**: Maintains full conversation history
- 🔧 **Script Execution**: Run Python, Shell, Batch, and PowerShell scripts
- 💾 **Real-time Archiving**: Automatically saves conversations in real-time
- 📚 **Archive Management**: Browse, view, and manage conversation archives
- 🎯 **Multiple Models**: Switch between different Ollama models
- 📁 **Script Management**: Organize and execute scripts from ./scripts folder

## Installation

### Quick Setup (Recommended)

1. **Run the setup script**:
   ```bash
   python setup.py
   ```

2. **Activate the virtual environment**:
   
   **Windows (Command Prompt)**:
   ```cmd
   activate.bat
   ```
   
   **Windows (PowerShell)**:
   ```powershell
   .\activate.ps1
   ```
   
   **Linux/macOS**:
   ```bash
   source activate.sh
   ```

3. **Install Ollama**: Download and install from [ollama.ai](https://ollama.ai)

4. **Pull an Ollama model** (e.g., Llama 3.2):
   ```bash
   ollama pull llama3.2
   ```

### Manual Setup

If you prefer to set up manually:

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   
   **Windows**:
   ```cmd
   venv\Scripts\activate
   ```
   
   **Linux/macOS**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r scripts/requirements.txt  # Optional script dependencies
   ```

4. **Install Ollama** and pull a model as above.

## Usage

### Basic Usage
```bash
# Make sure virtual environment is activated first
python main.py
```

### With Custom Model
```bash
python main.py --model llama3.2
```

### With Custom Scripts Directory
```bash
python main.py --scripts-dir ./my_scripts
```

### Skip Virtual Environment Check
```bash
python main.py --skip-venv-check
```

## Commands

| Command | Description |
|---------|-------------|
| `/help` or `/h` | Show help message |
| `/scripts` or `/s` | List available scripts |
| `/execute <script>` | Execute a script |
| `/save [filename]` | Save conversation to file |
| `/load <filename>` | Load conversation from file |
| `/clear` or `/c` | Clear conversation history |
| `/history` or `/hist` | Show conversation history |
| `/model <name>` | Change AI model |
| `/info` or `/i` | Show assistant info |
| `/quit` or `/q` | Exit the assistant |

### Archive Commands

| Command | Description |
|---------|-------------|
| `/archive` or `/a` | Show archive status and commands |
| `/archive-list` | List all archived conversations |
| `/archive-view <id>` | View specific archived conversation |
| `/archive-toggle` | Toggle auto-archiving on/off |
| `/archive-save` | Manually save current conversation |
| `/archive-clear` | Clear current session (start new) |
| `/archive-resume <id>` | Resume an archived conversation |

## Scripts Directory

The assistant can execute scripts from the `./scripts` folder. Supported formats:
- **Python**: `.py` files
- **Shell**: `.sh` files  
- **Batch**: `.bat` files
- **PowerShell**: `.ps1` files

### Example Scripts

Create a `./scripts` directory and add some example scripts:

**hello.py**:
```python
print("Hello from Python script!")
import datetime
print(f"Current time: {datetime.datetime.now()}")
```

**system_info.sh**:
```bash
#!/bin/bash
echo "System Information:"
uname -a
df -h
```

## Conversation Management

### Real-time Archiving
- **Auto-archive**: Conversations are automatically saved in real-time to `./conversations/`
- **Session files**: Each conversation session is saved as `session_YYYYMMDD_HHMMSS.json`
- **Background saving**: Messages are archived immediately when sent
- **Session metadata**: Includes model used, timestamps, and message count

### Manual Management
- **Manual save**: Use `/save [filename]` to save to a custom JSON file
- **Load**: Use `/load <filename>` to restore a previous conversation
- **Clear**: Use `/clear` to start fresh
- **Archive toggle**: Use `/archive-toggle` to enable/disable auto-archiving

### Archive Browsing
- **List archives**: Use `/archive-list` to see all saved conversations
- **View archive**: Use `/archive-view <id>` to view a specific conversation
- **Archive status**: Use `/archive` to see current archiving status

## Configuration

The assistant uses the following defaults:
- **Model**: `llama3.2`
- **Scripts Directory**: `./scripts`
- **Archive Directory**: `./conversations`
- **Auto-Archive**: `Enabled`
- **Timeout**: 30 seconds for script execution

You can override these with command-line arguments or change settings during runtime.

## Examples

### Basic Chat
```
> Hello! Can you help me with Python?
🤖 AI Assistant:
Hello! I'd be happy to help you with Python! I can assist with:
- Writing and debugging Python code
- Explaining Python concepts
- Creating scripts and functions
- Best practices and optimization

What specific Python topic would you like help with?
```

### Script Execution
```
> /scripts
Available scripts:
  - hello.py
  - system_info.sh

> /execute hello.py
Exit code: 0
STDOUT:
Hello from Python script!
Current time: 2024-01-15 10:30:45.123456
```

### Model Switching
```
> /model codellama
Model changed to codellama

> /info
Terminal AI Assistant
Model: codellama
Scripts Directory: ./scripts
Conversation Length: 5 messages
Available Scripts: 2
```

## Troubleshooting

### Virtual Environment Issues
- **Not activated**: Make sure to activate the virtual environment before running
- **Setup failed**: Run `python setup.py` to recreate the environment
- **Dependencies missing**: Reinstall with `pip install -r requirements.txt`

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Pull the model if needed: `ollama pull <model_name>`

### Script Execution Issues
- Ensure scripts have proper permissions
- Check file paths and extensions
- Verify the scripts directory exists
- Install script dependencies: `pip install -r scripts/requirements.txt`

### Python Dependencies
- Always use the virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS)
- Reinstall requirements if needed: `pip install -r requirements.txt`
- Check Python version: Requires Python 3.7+

## License

MIT License - feel free to use and modify as needed.
