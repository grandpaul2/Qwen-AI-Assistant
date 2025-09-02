# WorkspaceAI v3.0

AI assistant with smart tool selection and file management capabilities. Works with Ollama models (optimized for qwen2.5:3b).

## Quick Start

### Installation
Download only these files from the repository:
- `src/` folder (complete directory)
- `main.py`
- `requirements.txt`

### Setup
```bash
# 1. Install Ollama and load model
ollama run qwen2.5:3b

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Run
python main.py
```

### Linux Quick Install
```bash
chmod +x install_linux.sh && ./install_linux.sh
```

## Key Features

- **Smart Tool Selection**: Context-aware file operation detection
- **Secure Workspace**: All operations contained in `WorkspaceAI/workspace/`
- **Persistent Memory**: Conversation history across sessions
- **18+ File Operations**: Create, read, write, delete, copy, move, compress
- **Software Installation**: Helper for common software via multiple package managers

## Universal Tool System

Dynamic tool execution that handles any request without predefined schemas. The system automatically detects intent and executes appropriate actions:

### File Operations
- **Core**: `create_file`, `read_file`, `write_file`, `delete_file`, `list_files`
- **Management**: `copy_file`, `move_file`, `search_files`, `find`, `grep`
- **Aliases**: `save_file`, `remove_file`, `ls`, `dir`, `cp`, `mv`

### Code Execution
- **Languages**: `python`, `javascript`, `shell`, `powershell`, `cmd`
- **Interpreters**: `code_interpreter`, `exec`, `eval`, `node`, `bash`
- **Enhanced**: Cross-platform compatibility, smart command detection

### System Operations
- **Info**: `system_info`, `os_info`, `cpu_usage`, `memory_usage`, `disk_usage`
- **Processes**: `list_processes`, `ps`, `kill_process`, `process_info`
- **Network**: `network_info`, `ping`, `env_vars`, `path_info`

### Web Operations
- **Search**: `web_search`, `google`, `bing` (simulated)
- **HTTP**: `http_get`, `http_post`, `fetch`, `download`, `curl`
- **Scraping**: `scrape`, `extract_text`, `get_webpage`

### Calculator
- **Math**: `calculator`, `calc`, `math`, `calculate` (safe evaluation)

The AI intelligently maps requests to available tools - just describe what you want to do!

## Usage

### Chat Interface
```bash
/new        # Start new conversation
/memory     # Show memory status  
/config     # Configure settings
/reset      # Clear memory
exit        # Quit
```

### Force Modes
```bash
chat: your question          # Force chat mode
tools: your command          # Force file tools
install: software name       # Get install commands
```

## Architecture

```
main.py                 # Entry point
src/                   # Core modules
├── main.py           # Application logic
├── config.py         # Configuration
├── memory.py         # Conversation memory
├── file_manager.py   # File operations
├── ollama/           # Ollama integration
│   ├── enhanced_interface.py    # Context-aware interface
│   ├── tool_executor.py        # Direct tool execution
│   └── legacy_interface.py     # Backward compatibility
└── ...               # Other modules
WorkspaceAI/          # Auto-created runtime folder
├── workspace/        # File operations sandbox
├── memory/          # Conversation history
└── config.json     # Settings
```

## File Operations

Available in workspace sandbox:
- **Core**: create, read, write, delete, copy, move
- **Advanced**: compress, search, metadata, JSON handling
- **Organization**: list, backup, sync folders

## Memory System

- **Recent**: 2 full conversations
- **History**: 20 AI-summarized conversations  
- **Persistent**: Auto-saves across sessions

## Configuration

Edit `WorkspaceAI/config.json`:
```json
{
  "model": "qwen2.5:3b",
  "safe_mode": true,
  "ollama_host": "localhost:11434",
  "verbose_output": false
}
```

## Commands

### Ollama Management
```bash
ollama ps              # Show loaded models
ollama stop            # Unload models
ollama serve           # Start Ollama service
```

### Tool Detection Keywords
Auto-triggers file operations: `file`, `folder`, `create`, `delete`, `read`, `write`, `copy`, `move`, `list`, `search`, `compress`

## Requirements

- Python 3.7+
- Ollama installed
- Dependencies: `requests`, `tqdm`

---
*Streamlined AI assistant focused on tool selection accuracy and file management.*
