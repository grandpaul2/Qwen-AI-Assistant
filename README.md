# WorkspaceAI v3.0 - Modular Architecture

AI assistant with universal tool system and secure file management. Features modular architecture with comprehensive testing suite. Works with Ollama models (optimized for qwen2.5:3b).

## 🚀 What's New in v3.0

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Universal Tool Handler**: Enhanced dynamic tool execution engine  
- **Comprehensive Testing**: 91.4% test coverage with 212+ passing tests
- **Enhanced Tool Instructions**: Context-aware instruction system
- **Improved Error Handling**: Robust exception management
- **Configuration Management**: Advanced settings and path management

## Quick Start

### Installation
Clone the repository or download:
- `src/` folder (complete modular architecture)
- `main.py` (entry point)
- `requirements.txt`
- `tests/` folder (comprehensive test suite)

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

- **Universal Tool System**: Dynamic tool execution handles any request
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
```
t: to use tools

- /new        Start new conversation
- /tools      List available tools
- /memory     Show memory status
- /config     Configure settings
- /reset      Clear all memory
- exit        Quit
```

## Architecture v3.0 - Modular Design

```
main.py               # Entry point
src/                  # Core modular architecture
├── app.py            # Main application logic and interface
├── config.py         # Configuration management and constants
├── memory.py         # Conversation memory and persistence
├── file_manager.py   # Secure file operations with enhanced safety
├── universal_tool_handler.py  # Dynamic tool execution engine
├── tool_schemas.py   # Tool definitions and schemas
├── enhanced_tool_instructions.py  # Context-aware instruction system
├── utils.py          # Utility functions and helpers
├── exceptions.py     # Comprehensive error handling
├── progress.py       # Progress display and tracking
├── software_installer.py  # System software installation
└── ollama/           # Ollama integration modules
    ├── client.py     # Ollama API client with connection management
    ├── universal_interface.py  # Main Ollama interface
    └── connection_test.py      # Connection testing utilities

tests/                # Comprehensive testing suite (91.4% coverage)
├── conftest.py       # Test configuration and fixtures
├── unit/             # Unit tests for all modules
│   ├── test_app.py                    # Application logic tests
│   ├── test_config.py                 # Configuration tests (100% pass)
│   ├── test_universal_tool_handler.py # Tool handler tests (100% pass)
│   ├── test_enhanced_tool_instructions.py # Instructions tests
│   ├── test_file_manager.py           # File operations tests
│   ├── test_memory.py                 # Memory system tests
│   └── test_ollama_client.py          # Ollama client tests (100% pass)
├── security/         # Security and safety tests
└── system/           # Integration and system tests

WorkspaceAI/          # Auto-created runtime folder
├── workspace/        # File operations sandbox
├── memory/          # Conversation history storage
└── config.json     # User settings and configuration

archive/              # Historical components and old tests
├── deprecated_components/  # Previous architecture components
└── old tests/             # Archived obsolete tests
```

## 🧪 Testing Suite

### Test Coverage Status
- **Total Tests**: 232 tests
- **Passing**: 212 tests ✅
- **Success Rate**: **91.4%** 🎉
- **Perfect Modules**: Universal Tool Handler, Config, Ollama Client

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific module tests
python -m pytest tests/unit/test_universal_tool_handler.py -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
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
- Ollama installed and running
- Dependencies: `requests`, `tqdm`, `pytest` (for testing)

## Development

### Contributing
1. Fork the repository
2. Create a feature branch from `feature/modular-architecture`
3. Run tests: `python -m pytest tests/`
4. Submit a pull request

### Branch Structure
- `main`: Stable releases
- `feature/modular-architecture`: Current v3.0 development (91.4% test coverage)

---
*Modern AI assistant with modular architecture, comprehensive testing, and secure workspace management.*
