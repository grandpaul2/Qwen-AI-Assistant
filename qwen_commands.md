# Qwen + Supreme File Management - Command Reference

## **Startup Commands**

### **1. Load Qwen Model:**
```bash
ollama run qwen2.5:3b
```
*(Type `/bye` to exit but keep model loaded)*

### **2. Start Enhanced Chat:**
```bash
python C:\Users\Grandpaul\qwen.py
```

---

## **Software Installation Command Generator**

### **Supported Software:**
- **Development:** Python, Git, VS Code, Node.js, Notepad++
- **Browsers:** Chrome, Firefox  
- **Utilities:** 7zip, VLC Media Player
- **Communication:** Discord
- **AI/ML Tools:** Open WebUI, Ollama

### **Installation Methods:**
- **Winget** (Windows Package Manager) - Recommended
- **Pip** (Python packages)
- **Direct Download** (Official websites with links)
- **Docker** (Where applicable)

### **Example Usage:**
- `"Generate install commands for Python"`
- `"How do I install Git using winget?"`  
- `"Give me Docker commands for Open WebUI"`
- `"Install commands for VS Code"`

---

## **Memory System**

### **Rolling Memory Features:**
- **Last 2 conversations:** Stored with full detail and context
- **Next 8 conversations:** AI-generated summaries for quick reference  
- **Auto-save:** Memory saved after every message automatically
- **Cross-session continuity:** Resume conversations across restarts
- **Smart context:** Previous context automatically loaded into new chats

### **Memory Commands:**
- `/memory` - View current memory usage and statistics
- `/new` - Archive current conversation and start fresh
- `/reset` - Clear all stored conversations and summaries
- Auto-save on exit preserves current conversation

### **Memory Storage:**
- Location: `C:\Users\Grandpaul\.ollama_tools\memory.json`
- No manual management required - fully automatic
- Intelligent summarization maintains context without token bloat

---

## **Progress Indicators**

- **Long operations:** Progress bars for file searches, backups, compression
- **Context processing:** Loading indicator when processing lots of conversation history
- **Background saving:** Memory saves automatically while you read responses

---

## **Ollama Management Commands**

```bash
ollama ps                    # Show loaded models in VRAM
ollama list                  # Show all downloaded models
ollama stop qwen2.5:3b       # Unload specific model from VRAM
ollama stop                  # Unload all models
ollama serve                 # Start Ollama service (if needed)
```

---

## **Chat Interface Commands**

### **Bot Control Commands:**
```bash
/new                         # Start new conversation (saves current to memory)
/memory                      # Show memory status and statistics
/reset                       # Clear all conversation memory
exit                         # Quit chat (auto-saves current conversation)
```

### **Chat Modes:**
```bash
chat: your question          # Force normal chat (no tools)
tools: your command          # Force file tools
```

### **Auto-Detection:**
- **Normal chat:** General questions, conversations
- **File tools:** Any mention of file-related keywords

**File Keywords that Trigger Tools:**
`file`, `folder`, `create`, `delete`, `read`, `write`, `copy`, `move`, `list`, `search`, `compress`, `backup`, `json`, `metadata`, `sync`

---

## **Available File Management Tools**

### **Core Operations:**
- Create/read/write/delete files
- Create/delete folders
- Copy/move files and folders
- List files in directories
- Search files by name/content

### **Advanced Features:**
- JSON file operations
- File compression/decompression (zip, tar, gztar)
- File metadata (size, timestamps)
- Backup and synchronization
- File encryption/decryption
- Batch rename operations
- File versioning and tagging
- Software installation command generation

### **Example Commands:**
- `"Create a file called notes.txt with my todo list"`
- `"List all files in the current directory"`
- `"Search for files containing 'project'"`
- `"Compress hello.txt into backup.zip"`
- `"Copy notes.txt to archive.txt"`
- `"Generate install commands for Python"`
- `"How do I install VS Code?"`

---

## **Configuration**

- **Base Path:** `C:\Users\Grandpaul\Outputs`
- **Safe Mode:** `True` (prevents destructive operations)
- **Model:** Qwen 2.5:3B via Ollama
- **Script Location:** `C:\Users\Grandpaul\qwen.py`

---

## **Notes**

- Models stay loaded in VRAM until manually unloaded or system restart
- First model load takes ~5-10 seconds, subsequent calls are instant
- Safe mode prevents file deletions and overwrites
- Auto-detection works well, but you can force modes with `chat:` or `tools:` prefixes
- All file operations respect the configured base path