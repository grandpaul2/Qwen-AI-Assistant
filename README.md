# 🤖 Qwen Assistant with File Management v2.1 (All-in-One)

A sophisticated AI assistant combining Qwen 2.5:3B with advanced file management capabilities and persistent memory - **all in a single file!**

## ✨ Features

### 🧠 **Rolling Memory System**
- **2 Recent Conversations**: Full context preserved
- **8 Summarized Conversations**: AI-compressed history
- **Cross-Session Persistence**: Resume conversations after restarts
- **Smart Context Building**: Automatic history injection

### 📁 **Built-in File Management**
- **15+ File Operations**: Create, read, write, delete, copy, move
- **Advanced Features**: Search, compression, backup
- **JSON Handling**: Specialized JSON read/write operations
- **Safety Mode**: Prevents destructive operations
- **Smart Path Resolution**: Configurable base directory

### 📦 **Software Installation Helper**
- **Multiple Methods**: Winget, direct downloads, pip, docker
- **11 Popular Software**: Python, Git, VS Code, Chrome, Discord, etc.
- **Smart Matching**: Flexible software name recognition
- **Method Selection**: Auto-detect best installation method

### 🎯 **User Experience**
- **Auto-Detection**: Smart keyword-based tool triggering
- **Progress Indicators**: Visual feedback for slow operations
- **Command Shortcuts**: `/new`, `/memory`, `/reset`
- **Mode Control**: Force chat vs tools with prefixes
- **Single File**: No dependencies or separate imports needed!

## 🚀 Quick Start

### 1. **Setup File**
```bash
# Just copy ONE file to your user directory
copy qwen.py C:\Users\Grandpaul\qwen.py
```

### 2. **Install Dependencies**
```bash
pip install requests tqdm
```

### 3. **Setup Ollama**
```bash
# Install Ollama from https://ollama.ai/download
ollama pull qwen2.5:3b
ollama serve
```

### 4. **Test Setup**
```bash
python test_qwen.py  # Run diagnostics
```

### 5. **Start Assistant**
```bash
python C:\Users\Grandpaul\qwen.py
```

## 📂 Directory Structure
```
C:\Users\Grandpaul\
├── qwen.py                    # EVERYTHING in one file!
└── .ollama\
    ├── outputs\               # File operations base directory
    └── memory\
        └── memory.json        # Persistent conversation memory
```

## 🎛️ Usage Examples

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

### **File Manager Settings** (in qwen.py around line 35)
```python
self.base_path = "C:\\Users\\Grandpaul\\.ollama\\outputs"
self.safe_mode = True  # Prevents destructive operations
```

### **Memory Settings** (in qwen.py around line 278)
```python
MEMORY_FILE = r'C:\Users\Grandpaul\.ollama\memory\memory.json'
```

## 🏆 What Makes This Special

1. **Single File Architecture**: Everything you need in one `qwen.py` file
2. **No Import Dependencies**: File management built directly in
3. **Persistent AI Memory**: Unlike standard chat sessions, maintains context across restarts
4. **Hybrid Intelligence**: Combines AI reasoning with programmatic file operations  
5. **Safety First**: Built-in protections prevent accidental data loss
6. **Production Ready**: Robust error handling, logging, and user feedback
7. **Self-Contained**: No external services required beyond Ollama

## 🎯 Single File Benefits

- ✅ **Easy Deployment**: Just copy one file
- ✅ **No Import Errors**: Everything is self-contained
- ✅ **Easier Updates**: Modify one file to change everything
- ✅ **Simpler Backup**: Just backup qwen.py
- ✅ **Portable**: Works anywhere Python + Ollama are installed

## 📈 Version History

- **v2.1**: All-in-one architecture, no separate files needed
- **v2.0**: Rolling memory system, software installation database
- **v1.1**: Added safety features, file management tools
- **v1.0**: Basic chat with Ollama integration

## 📄 License

MIT License - Feel free to use and modify for personal or commercial projects.
