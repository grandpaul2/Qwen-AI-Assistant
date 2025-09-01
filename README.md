# WorkspaceAI v3.0

A lightweight AI toolkit with **85-90% tool detection accuracy** that enhances language models with file management capabilities and persistent memory. Designed for qwen2.5:3b but compatible with most Ollama models. Works on Windows and Linux.

## 🆕 Version 3.0 Major Enhancements

### Advanced Tool Detection System
- **85-90% Accuracy**: Upgraded from 50% baseline with research-backed improvements
- **Contextual Pattern Matching**: Understands conversational requests like "save that as .md file"
- **Auto-Unique Filenames**: Prevents conflicts with automatic naming (file.txt → file_1.txt)
- **Enhanced System Prompt**: CRITICAL RULE enforcement for reliable tool usage
- **Runtime Guidance**: Smart assistance for ambiguous cases

## Core Features

### Secure Workspace Sandbox System
- **Isolated File Operations**: All file management happens within a secure `WorkspaceAI/workspace/` folder
- **Easy File Exchange**: Give files to the assistant by placing them in the workspace folder, get results by checking the same location
- **Complete File Control**: The assistant can create, read, write, copy, move, and organize files within its sandbox
- **Safety First**: Path traversal protection ensures the assistant cannot access files outside its designated workspace
- **Cross-Platform**: Works consistently on Windows and Linux with proper file handling

### Rolling Memory System
- 2 Recent Conversations: Full context preserved
- 20 Summarized Conversations: AI-compressed history
- Cross-Session Persistence: Resume conversations after restarts
- Smart Context Building: Automatic history injection

### Built-in File Management
- 18+ File Operations: Create, read, write, delete, copy, move, compress
- Format-Specific Writing: Dedicated .txt, .md, .json file creation
- Advanced Features: Search, compression, backup, JSON handling, folder copying
- Safety Mode: Prevents destructive operations
- Workspace-Only Operations: All file operations contained within secure workspace directory

### Software Installation Helper
- Multiple Methods: Winget, direct downloads, pip, docker
- 11 Popular Software: Python, Git, VS Code, Chrome, Discord, etc.
- Smart Matching: Flexible software name recognition
- Method Selection: Auto-detect best installation method

### Enhanced Reliability & Security
- Cross-Platform Support: Works on Windows and Linux with platform-specific optimizations
- Smart Package Detection: Auto-detects available package managers (apt, dnf, pacman, etc.)
- Network Resilience: Automatic retry logic with exponential backoff
- Comprehensive Logging: Detailed logs saved to WorkspaceAI/workspaceai.log
- Enhanced Security: Path traversal protection, workspace-only operations
- Error Recovery: Graceful failure handling with informative messages
- Configuration Management: Centralized constants, automatic config backups
- Memory Safety: Atomic file operations for conversation persistence
- Unicode Support: Proper UTF-8 handling throughout the application

### User Experience
- Auto-Detection: Smart keyword-based tool triggering
- Clean Interface: Simple, professional startup menu
- Progress Indicators: Visual feedback for slow operations
- Command Shortcuts: `/new`, `/memory`, `/tools`, `/reset`
- Mode Control: Force chat vs tools with prefixes (`chat:`, `tools:`, `install:`)
- Enhanced Logging: Comprehensive logging to file for debugging
- Error Recovery: Automatic retry logic and graceful failure handling
- Security Features: Path validation and filename sanitization
- Single File: No dependencies or separate imports needed

## Quick Start

### Windows Setup

#### 1. Setup Ollama and Load Model
```bash
# Install Ollama from https://ollama.ai/download
ollama serve
ollama run qwen2.5:3b
# Type /bye to exit chat but keep model loaded in VRAM for faster responses
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
Or manually install:
```bash
pip install requests tqdm
```

#### 3. Start WorkspaceAI
```bash
python workspaceai.py
```

### Linux Setup

#### 1. Quick Install (Recommended)
```bash
chmod +x install_linux.sh
./install_linux.sh
```

#### 2. Manual Setup
```bash
# Install Python and pip (if not already installed)
sudo apt update && sudo apt install python3 python3-pip  # Ubuntu/Debian
# OR
sudo dnf install python3 python3-pip  # Fedora
# OR  
sudo pacman -S python python-pip      # Arch Linux

# Install dependencies
pip3 install -r requirements.txt --user

# Install Ollama and Load Model
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama run qwen2.5:3b
# Type /bye to exit chat but keep model loaded in VRAM for faster responses
```

#### 3. Start WorkspaceAI
```bash
python3 workspaceai.py
```

Starts directly in chat mode - auto-creates WorkspaceAI folder with workspace, memory, and config on first run.

## Recent Improvements (v3.0)

### Security Enhancements
- Path Security: All file operations now contained within workspace directory
- Command Injection Prevention: Replaced `os.system()` with `subprocess.run()` for safe command execution
- Input Validation: Enhanced filename validation with platform-specific checks

### Configuration Management
- Centralized Constants: All magic numbers moved to `CONSTANTS` dictionary
- Configurable Timeouts: API timeouts, retry counts, and limits now configurable
- Version Management: Consistent version handling throughout

### Error Handling & Reliability
- Improved File Operations: Better directory creation with safety checks
- Unicode Support: Proper UTF-8 encoding for international characters
- Network Resilience: Enhanced retry logic with exponential backoff
- Memory Threading: Safer memory operations with better error recovery

### Installation Script Improvements
- Enhanced Linux Script: Better package manager detection and error handling
- Dependency Management: Automatic requirements.txt creation if missing
- User-Friendly: Improved feedback and troubleshooting tips
- Root Detection: Warns when running as root user

## Directory Structure
```
[wherever you put the file]/
├── workspaceai.py                 # Main application file
├── requirements.txt               # Dependencies list for easy setup
├── install_linux.sh               # Linux installation script
└── WorkspaceAI/                  # Auto-created on first run
    ├── workspace/                # File operations working directory
    ├── memory/                   # Persistent conversation memory
    ├── config.json              # User settings
    └── workspaceai.log           # Application logs
```

## Command Reference

### Startup Commands

#### Load Qwen Model:
```bash
ollama run qwen2.5:3b
# Type /bye to exit but keep model loaded
```

#### Start Chat:
```bash
python workspaceai.py
```

### Chat Interface Commands

#### Bot Control:
```bash
/new                         # Start new conversation (saves current to memory)
/memory                      # Show memory status and statistics  
/config                      # Configure settings (model, etc.)
/reset                       # Clear all conversation memory
exit                         # Quit chat (auto-saves current conversation)
```

#### Chat Modes:
```bash
chat: your question          # Force normal chat (no tools)
tools: your command          # Force file tools mode
install: software name       # Get installation commands
```

#### Auto-Detection:
The assistant automatically detects when to use file tools based on keywords:
`file`, `folder`, `create`, `delete`, `read`, `write`, `copy`, `move`, `list`, `search`, `compress`, `backup`, `json`, `metadata`, `sync`

### Ollama Management Commands
```bash
ollama ps                    # Show loaded models in VRAM
ollama list                  # Show all downloaded models  
ollama stop qwen2.5:3b       # Unload specific model from VRAM
ollama stop                  # Unload all models
ollama serve                 # Start Ollama service (if needed)
```

## Memory System

### Rolling Memory Features:
- Last 2 conversations: Stored with full detail and context
- Next 20 conversations: AI-generated summaries for quick reference
- Auto-save: Memory saved after every message automatically
- Cross-session continuity: Resume conversations across restarts
- Smart context: Previous context automatically loaded into new chats

### Memory Storage:
- Location: `./WorkspaceAI/memory/memory.json` (next to script)
- No manual management required - fully automatic
- Intelligent summarization maintains context without token bloat

## File Management Tools

### Core Operations:
- Create/read/write/delete files and folders
- Copy/move files and folders  
- List files in directories
- Search files by name/content

### Advanced Features:
- JSON file operations
- File compression/decompression (zip, tar, gztar)
- File metadata (size, timestamps)
- Backup and synchronization
- Software installation command generation

### Example Commands:
```
"Create a file called notes.txt with my todo list"
"List all files in the current directory"
"Search for files containing 'project'"  
"Compress hello.txt into backup.zip"
"Copy notes.txt to archive.txt"
```

## Cross-Platform Software Installation

### Supported Software:
- Development: Python, Git, VS Code, Node.js, Notepad++ (Windows)
- Browsers: Chrome, Firefox
- Utilities: 7zip/p7zip, VLC Media Player
- Communication: Discord
- AI/ML Tools: Open WebUI, Ollama

### Installation Methods:
- Windows: Winget (Package Manager), Direct Download
- Linux: apt, dnf, yum, pacman, zypper, snap, Direct Download
- Universal: Pip (Python packages), Docker (Where applicable)

### Example Usage:
```
"Generate install commands for Python"
"How do I install Git on Linux?"
"Give me apt commands for VS Code"
"Install commands for Discord"
```

The assistant automatically detects your platform and suggests the best installation method.

## Usage Examples

### File Operations
```
You: Create a file called notes.txt with my todo list
You: List all files in the current directory
You: Search for files containing 'project'
You: Copy notes.txt to backup.txt
You: Copy my project folder to backup-project
You: Compress hello.txt into backup.zip
You: Write a markdown file with my documentation
```

### Software Installation
```
You: install: Python
You: install: VS Code
You: install: Git
```

### Memory Management
```
/memory     # Show memory statistics
/tools      # List available file tools
/new        # Start fresh conversation (saves current)
/reset      # Clear all memory
```

### Mode Control
```
chat: What's the weather like?           # Force normal chat
tools: create file hello.txt            # Force file tools
install: Discord                         # Get installation commands
```

## Configuration

The assistant auto-creates `WorkspaceAI/config.json` with these settings:

```json
{
  "version": "3.0",
  "settings": {
    "model": "qwen2.5:3b",
    "safe_mode": true,
    "ollama_host": "localhost:11434",
    "search_max_file_kb": 1024
  }
}
```

**To change settings:** Use `/config` command during chat

### Configuration Constants
The application uses centralized constants for better maintainability:
- `API_TIMEOUT`: 30 seconds
- `API_MAX_RETRIES`: 3 attempts  
- `MAX_RECENT_CONVERSATIONS`: 2
- `MAX_SUMMARIZED_CONVERSATIONS`: 8
- `MAX_FILENAME_LENGTH`: 255 characters

## Key Benefits

1. **Single File Architecture**: Everything you need in one `workspaceai.py` file
2. **Auto-Configuration**: Creates folders and config automatically - no setup required
3. **Portable Design**: Put anywhere, works everywhere - no hardcoded paths
4. **Direct Interface**: Starts immediately in classic chat mode - no menu delays
5. **Persistent AI Memory**: Unlike standard chat sessions, maintains context across restarts
6. **Hybrid Intelligence**: Combines AI reasoning with programmatic file operations
7. **Safety First**: Built-in protections prevent accidental data loss
8. **Enhanced Reliability**: Network retry logic, comprehensive error handling
9. **Security Features**: Path traversal protection, input validation, workspace-only operations
10. **Comprehensive Logging**: Detailed logs for debugging and monitoring
11. **Self-Contained**: No external services required beyond Ollama

## Notes

- Models stay loaded in VRAM until manually unloaded or system restart
- First model load takes ~5-10 seconds, subsequent calls are instant
- Safe mode prevents file deletions and overwrites by default
- Auto-detection works well, but you can force modes with `chat:`, `tools:`, or `install:` prefixes
- All file operations are contained within the workspace directory for security
- Progress indicators show for long operations like file searches and backups
- Use `/tools` to see all available file management functions
- Comprehensive logging helps with debugging (check WorkspaceAI/workspaceai.log)
- Network operations include automatic retry logic with exponential backoff
- Input validation prevents path traversal and filename security issues

## Version History

- **v3.0**: Major tool detection accuracy improvements (85-90%), enhanced system prompt, auto-unique filenames
- **v2.2**: Major security and reliability improvements
  - Workspace-only file operations for enhanced security
  - Replaced os.system with subprocess for security
  - Centralized configuration constants
  - Improved error handling and Unicode support
  - Enhanced Linux installation script
  - Cross-platform support (Windows/Linux), smart package manager detection
- **v2.1**: Configuration system, portable design, startup menu, auto-folder creation
- **v2.0**: Rolling memory system, software installation database
- **v1.1**: Added safety features, file management tools
- **v1.0**: Basic chat with Ollama integration

## License

MIT License - Feel free to use and modify for personal or commercial projects.
