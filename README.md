# 🤖 Qwen Assistant v2.2

A sophisticated AI assistant combining Qwen 2.5:3B with advanced file management capabilities and persistent memory - **works on Windows and Linux!**

## ✨ Features

### 🧠 **Rolling Memory System**
- **2 Recent Conversations**: Full context preserved
- **8 Summarized Conversations**: AI-compressed history
- **Cross-Session Persistence**: Resume conversations after restarts
- **Smart Context Building**: Automatic history injection

### 📁 **Built-in File Management**
- **18+ File Operations**: Create, read, write, delete, copy, move, compress
- **Format-Specific Writing**: Dedicated .txt, .md, .json file creation
- **Advanced Features**: Search, compression, backup, JSON handling, folder copying
- **Safety Mode**: Prevents destructive operations
- **Smart Path Resolution**: Configurable base directory with pathlib security

### 📦 **Software Installation Helper**
- **Multiple Methods**: Winget, direct downloads, pip, docker
- **11 Popular Software**: Python, Git, VS Code, Chrome, Discord, etc.
- **Smart Matching**: Flexible software name recognition
- **Method Selection**: Auto-detect best installation method

### 🛡️ **Enhanced Reliability & Security**
- **Cross-Platform Support**: Works on Windows and Linux with platform-specific optimizations
- **Smart Package Detection**: Auto-detects available package managers (apt, dnf, pacman, etc.)
- **Network Resilience**: Automatic retry logic with exponential backoff
- **Comprehensive Logging**: Detailed logs saved to QwenAssistant/qwen_assistant.log
- **Enhanced Security**: Path traversal protection using pathlib, subprocess instead of os.system
- **Error Recovery**: Graceful failure handling with informative messages
- **Configuration Management**: Centralized constants, automatic config backups
- **Memory Safety**: Atomic file operations for conversation persistence
- **Unicode Support**: Proper UTF-8 handling throughout the application

### 🎯 **User Experience**
- **Auto-Detection**: Smart keyword-based tool triggering
- **Clean Interface**: Simple, professional startup menu
- **Progress Indicators**: Visual feedback for slow operations
- **Command Shortcuts**: `/new`, `/memory`, `/tools`, `/reset`
- **Mode Control**: Force chat vs tools with prefixes (`chat:`, `tools:`, `install:`)
- **Enhanced Logging**: Comprehensive logging to file for debugging
- **Error Recovery**: Automatic retry logic and graceful failure handling
- **Security Features**: Path validation and filename sanitization
- **Single File**: No dependencies or separate imports needed!

## 🚀 Quick Start

### **Windows Setup**

#### 1. **Setup Ollama**
```bash
# Install Ollama from https://ollama.ai/download
ollama pull qwen2.5:3b
ollama serve
```

#### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```
Or manually install:
```bash
pip install requests tqdm
```

#### 3. **Start Assistant**
```bash
python qwen_assistant.py
```

### **Linux Setup**

#### 1. **Quick Install (Recommended)**
```bash
chmod +x install_linux.sh
./install_linux.sh
```
*Enhanced script with improved error handling, package manager detection, and troubleshooting tips*

#### 2. **Manual Setup**
```bash
# Install Python and pip (if not already installed)
sudo apt update && sudo apt install python3 python3-pip  # Ubuntu/Debian
# OR
sudo dnf install python3 python3-pip  # Fedora
# OR  
sudo pacman -S python python-pip      # Arch Linux

# Install dependencies
pip3 install -r requirements.txt --user

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull qwen2.5:3b
```

#### 3. **Start Assistant**
```bash
python3 qwen_assistant.py
```

*Starts directly in chat mode - auto-creates QwenAssistant folder with workspace, memory, and config on first run*

## 🔧 **Recent Improvements (v2.2 Enhanced)**

### **Security Enhancements**
- **Path Security**: Replaced manual path validation with `pathlib.Path.relative_to()` for robust security
- **Command Injection Prevention**: Replaced `os.system()` with `subprocess.run()` for safe command execution
- **Input Validation**: Enhanced filename validation with platform-specific checks

### **Configuration Management**
- **Centralized Constants**: All magic numbers moved to `CONSTANTS` dictionary
- **Configurable Timeouts**: API timeouts, retry counts, and limits now configurable
- **Version Management**: Consistent version handling throughout

### **Error Handling & Reliability**
- **Improved File Operations**: Better directory creation with safety checks
- **Unicode Support**: Proper UTF-8 encoding for international characters
- **Network Resilience**: Enhanced retry logic with exponential backoff
- **Memory Threading**: Safer memory operations with better error recovery

### **Installation Script Improvements**
- **Enhanced Linux Script**: Better package manager detection and error handling
- **Dependency Management**: Automatic requirements.txt creation if missing
- **User-Friendly**: Improved feedback and troubleshooting tips
- **Root Detection**: Warns when running as root user

## 📂 Directory Structure
```
[wherever you put the file]/
├── qwen_assistant.py          # EVERYTHING in one file!
├── requirements.txt           # Dependencies list for easy setup
├── install_linux.sh           # Linux installation script
└── QwenAssistant/            # Auto-created on first run
    ├── workspace/            # File operations working directory
    ├── memory/               # Persistent conversation memory
    ├── config.json          # User settings
    └── qwen_assistant.log    # Application logs
```

## 🎛️ Command Reference

### **Startup Commands**

#### Load Qwen Model:
```bash
ollama run qwen2.5:3b
# Type /bye to exit but keep model loaded
```

#### Start Enhanced Chat:
```bash
python qwen_assistant.py
```

### **Chat Interface Commands**

#### Bot Control:
```bash
/new                         # Start new conversation (saves current to memory)
/memory                      # Show memory status and statistics  
/config                      # Configure settings (paths, model, etc.)
/reset                       # Clear all conversation memory
exit                         # Quit chat (auto-saves current conversation)
```

#### Chat Modes:
```bash
chat: your question          # Force normal chat (no tools)
tools: your command          # Force file tools mode
```

#### Auto-Detection:
The assistant automatically detects when to use file tools based on keywords:
`file`, `folder`, `create`, `delete`, `read`, `write`, `copy`, `move`, `list`, `search`, `compress`, `backup`, `json`, `metadata`, `sync`

### **Ollama Management Commands**
```bash
ollama ps                    # Show loaded models in VRAM
ollama list                  # Show all downloaded models  
ollama stop qwen2.5:3b       # Unload specific model from VRAM
ollama stop                  # Unload all models
ollama serve                 # Start Ollama service (if needed)
```

## � Memory System

### **Rolling Memory Features:**
- **Last 2 conversations:** Stored with full detail and context
- **Next 8 conversations:** AI-generated summaries for quick reference
- **Auto-save:** Memory saved after every message automatically
- **Cross-session continuity:** Resume conversations across restarts
- **Smart context:** Previous context automatically loaded into new chats

### **Memory Storage:**
- Location: `./QwenAssistant/memory/memory.json` (next to script)
- No manual management required - fully automatic
- Intelligent summarization maintains context without token bloat

## 🛠️ File Management Tools

### **Core Operations:**
- Create/read/write/delete files and folders
- Copy/move files and folders  
- List files in directories
- Search files by name/content

### **Advanced Features:**
- JSON file operations
- File compression/decompression (zip, tar, gztar)
- File metadata (size, timestamps)
- Backup and synchronization
- Software installation command generation

### **Example Commands:**
```
"Create a file called notes.txt with my todo list"
"List all files in the current directory"
"Search for files containing 'project'"  
"Compress hello.txt into backup.zip"
"Copy notes.txt to archive.txt"
```

## 📦 Cross-Platform Software Installation

### **Supported Software:**
- **Development:** Python, Git, VS Code, Node.js, Notepad++ (Windows)
- **Browsers:** Chrome, Firefox
- **Utilities:** 7zip/p7zip, VLC Media Player
- **Communication:** Discord
- **AI/ML Tools:** Open WebUI, Ollama

### **Installation Methods:**
- **Windows:** Winget (Package Manager), Direct Download
- **Linux:** apt, dnf, yum, pacman, zypper, snap, Direct Download
- **Universal:** Pip (Python packages), Docker (Where applicable)

### **Example Usage:**
```
"Generate install commands for Python"
"How do I install Git on Linux?"
"Give me apt commands for VS Code"
"Install commands for Discord"
```

*The assistant automatically detects your platform and suggests the best installation method!*

## � Usage Examples

### **File Operations**
```
You: Create a file called notes.txt with my todo list
You: List all files in the current directory
You: Search for files containing 'project'
You: Copy notes.txt to backup.txt
You: Copy my project folder to backup-project
You: Compress hello.txt into backup.zip
You: Write a markdown file with my documentation
```

### **Software Installation**
```
You: install: Python
You: install: VS Code
You: install: Git
```

### **Memory Management**
```
/memory     # Show memory statistics
/tools      # List available file tools
/new        # Start fresh conversation (saves current)
/reset      # Clear all memory
```

### **Mode Control**
```
chat: What's the weather like?           # Force normal chat
tools: create file hello.txt            # Force file tools
install: Discord                         # Get installation commands
```

## ⚙️ Configuration

The assistant auto-creates `QwenAssistant/config.json` with these settings:

```json
{
  "version": "2.2",
  "paths": {
    "workspace": "./QwenAssistant/workspace",
    "memory": "./QwenAssistant/memory"
  },
  "settings": {
    "model": "qwen2.5:3b",
    "safe_mode": true,
    "ollama_host": "localhost:11434",
    "search_max_file_kb": 1024
  }
}
```

**To change settings:** Use `/config` command during chat

### **Configuration Constants**
The application now uses centralized constants for better maintainability:
- `API_TIMEOUT`: 30 seconds
- `API_MAX_RETRIES`: 3 attempts  
- `MAX_RECENT_CONVERSATIONS`: 2
- `MAX_SUMMARIZED_CONVERSATIONS`: 8
- `MAX_FILENAME_LENGTH`: 255 characters

## 🏆 What Makes This Special

1. **Single File Architecture**: Everything you need in one `qwen_assistant.py` file
2. **Auto-Configuration**: Creates folders and config automatically - no setup required
3. **Portable Design**: Put anywhere, works everywhere - no hardcoded paths
4. **Direct Interface**: Starts immediately in classic chat mode - no menu delays
5. **Persistent AI Memory**: Unlike standard chat sessions, maintains context across restarts
6. **Hybrid Intelligence**: Combines AI reasoning with programmatic file operations
7. **Safety First**: Built-in protections prevent accidental data loss
8. **Enhanced Reliability**: Network retry logic, comprehensive error handling
9. **Security Features**: Path traversal protection, input validation
10. **Comprehensive Logging**: Detailed logs for debugging and monitoring
11. **Self-Contained**: No external services required beyond Ollama

## 🎯 Single File Benefits

- ✅ **Easy Deployment**: Just copy one file anywhere
- ✅ **Cross-Platform**: Works on Windows and Linux
- ✅ **Auto-Setup**: Creates folders and config automatically
- ✅ **Smart Package Detection**: Auto-detects Linux package managers
- ✅ **Enhanced Security**: Path traversal protection, subprocess usage, input validation
- ✅ **Robust Error Handling**: Comprehensive logging and recovery
- ✅ **Centralized Configuration**: Constants dictionary for easy maintenance
- ✅ **Unicode Support**: Proper UTF-8 encoding throughout
- ✅ **User-Friendly**: Improved installation script and troubleshooting
- ✅ **Easier Updates**: Modify one file to change everything
- ✅ **Simpler Backup**: Just backup qwen_assistant.py and QwenAssistant folder

## 📋 Notes

- Models stay loaded in VRAM until manually unloaded or system restart
- First model load takes ~5-10 seconds, subsequent calls are instant
- Safe mode prevents file deletions and overwrites by default
- Auto-detection works well, but you can force modes with `chat:`, `tools:`, or `install:` prefixes
- All file operations respect the configured base path with security validation
- Progress indicators show for long operations like file searches and backups
- Use `/tools` to see all available file management functions
- Comprehensive logging helps with debugging (check QwenAssistant/qwen_assistant.log)
- Network operations include automatic retry logic with exponential backoff
- Input validation prevents path traversal and filename security issues

## 📈 Version History

- **v2.2 Enhanced**: Major security and reliability improvements
  - Enhanced path security using pathlib
  - Replaced os.system with subprocess for security
  - Centralized configuration constants
  - Improved error handling and Unicode support
  - Enhanced Linux installation script
- **v2.2**: Cross-platform support (Windows/Linux), smart package manager detection, platform-aware validation
- **v2.1.1**: Enhanced error handling, logging system, security improvements, dependency management
- **v2.1**: Configuration system, portable design, startup menu, auto-folder creation
- **v2.0**: Rolling memory system, software installation database
- **v1.1**: Added safety features, file management tools
- **v1.0**: Basic chat with Ollama integration

## 📄 License

MIT License - Feel free to use and modify for personal or commercial projects.
