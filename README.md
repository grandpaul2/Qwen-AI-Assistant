# 🤖 Qwen Assistant with File Management v2.2 (Cross-Platform)

A sophisticated AI assistant combining Qwen 2.5:3B with advanced file management capabilities and persistent memory - **works on Windows and Linux!**

## ✨ Features

### 🧠 **Rolling Memory System**
- **2 Recent Conversations**: Full context preserved
- **8 Summarized Conversations**: AI-compressed history
- **Cross-Session Persistence**: Resume conversations after restarts
- **Smart Context Building**: Automatic history injection

### 📁 **Built-in File Management**
- **15+ File Operations**: Create, read, write, delete, copy, move
- **Advanced Features**: Search, compression, backup, JSON handling
- **Safety Mode**: Prevents destructive operations
- **Smart Path Resolution**: Configurable base directory

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
- **Input Validation**: Platform-aware filename sanitization and path traversal protection
- **Error Recovery**: Graceful failure handling with informative messages
- **Configuration Backup**: Automatic config backups before changes
- **Memory Safety**: Atomic file operations for conversation persistence

### 🎯 **User Experience**
- **Auto-Detection**: Smart keyword-based tool triggering
- **Progress Indicators**: Visual feedback for slow operations
- **Command Shortcuts**: `/new`, `/memory`, `/reset`
- **Mode Control**: Force chat vs tools with prefixes
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

#### 2. **Manual Setup**
```bash
# Install Python and pip (if not already installed)
sudo apt update && sudo apt install python3 python3-pip  # Ubuntu/Debian
# OR
sudo dnf install python3 python3-pip  # Fedora
# OR  
sudo pacman -S python python-pip      # Arch Linux

# Install dependencies
pip3 install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull qwen2.5:3b
```

#### 3. **Start Assistant**
```bash
python3 qwen_assistant.py
```

*Starts directly in chat mode - no menu system. Auto-creates QwenAssistant folder with outputs, memory, and config on first run*

## 📂 Directory Structure
```
[wherever you put the file]/
├── qwen_assistant.py          # EVERYTHING in one file!
├── requirements.txt           # Dependencies list for easy setup
├── install_linux.sh           # Linux installation script
└── QwenAssistant/            # Auto-created on first run
    ├── outputs/              # File operations base directory
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
You: Compress hello.txt into backup.zip
```

### **Software Installation**
```
You: How do I install Python?
You: Generate install commands for VS Code  
You: What's the best way to install Git?
```

### **Memory Management**
```
/memory     # Show memory statistics
/new        # Start fresh conversation (saves current)
/reset      # Clear all memory
```

### **Mode Control**
```
chat: What's the weather like?           # Force normal chat
tools: create file hello.txt            # Force file tools
```

## ⚙️ Configuration

The assistant auto-creates `QwenAssistant/config.json` with these settings:

```json
{
  "version": "2.1",
  "paths": {
    "outputs": "./QwenAssistant/outputs",
    "memory": "./QwenAssistant/memory"
  },
  "settings": {
    "model": "qwen2.5:3b",
    "safe_mode": true,
    "ollama_host": "localhost:11434"
  }
}
```

**To change settings:** Use `/config` command during chat

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
- ✅ **Dependency Management**: Simple requirements.txt for easy setup
- ✅ **Robust Error Handling**: Comprehensive logging and recovery
- ✅ **Security Built-in**: Platform-aware input validation and path protection
- ✅ **User-Friendly**: Startup menu and configuration options
- ✅ **Easier Updates**: Modify one file to change everything
- ✅ **Simpler Backup**: Just backup qwen_assistant.py and QwenAssistant folder

## 📋 Notes

- Models stay loaded in VRAM until manually unloaded or system restart
- First model load takes ~5-10 seconds, subsequent calls are instant
- Safe mode prevents file deletions and overwrites by default
- Auto-detection works well, but you can force modes with `chat:` or `tools:` prefixes
- All file operations respect the configured base path with security validation
- Progress indicators show for long operations like file searches and backups
- Comprehensive logging helps with debugging (check QwenAssistant/qwen_assistant.log)
- Network operations include automatic retry logic with exponential backoff
- Input validation prevents path traversal and filename security issues

## 📈 Version History

- **v2.2**: Cross-platform support (Windows/Linux), smart package manager detection, platform-aware validation
- **v2.1.1**: Enhanced error handling, logging system, security improvements, dependency management
- **v2.1**: Configuration system, portable design, startup menu, auto-folder creation
- **v2.0**: Rolling memory system, software installation database
- **v1.1**: Added safety features, file management tools
- **v1.0**: Basic chat with Ollama integration

## 📄 License

MIT License - Feel free to use and modify for personal or commercial projects.
