# WorkspaceAI v3.0 - Modular Architecture

⚠️ **DEVELOPMENT NOTICE**: This project is currently on hold due to complexity issues with tool integration. While the core memory system is highly advanced and functional, the universal tool calling system requires significant refactoring.

**Current Status**: 
- ✅ Advanced memory system (fully functional)
- ✅ Multi-model support with adaptive context management  
- ❌ Universal tool integration (development issues - context contamination)
- ❌ Real-time tool execution (on hold)

We are focusing development efforts on a streamlined version called "MemoryAI" that concentrates solely on the memory system without tool complexity.

## What's Working in v3.0

- **Memory System**: Model-specific memory isolation with adaptive context management
- **Modular Architecture**: Separation of concerns with dedicated modules
- **Error Handling**: Exception management framework
- **Configuration Management**: Settings and path management
- **Testing**: Test coverage across memory system components

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

- **Universal Tool System**: Dynamic tool execution for various requests
- **Secure Workspace**: Operations contained in `WorkspaceAI/workspace/`
- **Persistent Memory**: Conversation history across sessions
- **File Operations**: Create, read, write, delete, copy, move, compress
- **Software Installation**: Helper for common software via package managers

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

## Architecture v3.0 - Flattened Modular Design

```
main.py                              # Entry point
src/                                 # Core modular architecture (flat structure)
├── app.py                           # Main application logic and interface
├── config.py                        # Configuration management and constants
├── memory.py                        # Legacy memory system with v3.0 integration
├── unified_memory_manager.py        # v3.0 memory system orchestrator
├── model_specific_memory.py         # Per-model memory isolation
├── adaptive_budget_manager.py       # Complexity-aware context allocation
├── safety_validator.py              # System validation framework
├── token_counter.py                 # Enhanced token estimation
├── memory_integration.py            # Backward compatibility interface
├── file_manager.py                  # Secure file operations with enhanced safety
├── universal_tool_handler.py        # Dynamic tool execution engine
├── tool_schemas.py                  # Tool definitions and schemas
├── enhanced_tool_instructions.py    # Context-aware instruction system
├── utils.py                         # Utility functions and helpers
├── exceptions.py                    # Comprehensive error handling
├── progress.py                      # Progress display and tracking
├── software_installer.py            # System software installation
├── ollama_client.py                 # Ollama API client with connection management
├── ollama_universal_interface.py    # Main Ollama interface
└── ollama_connection_test.py        # Connection testing utilities

tests/                               # Comprehensive testing suite
├── conftest.py                      # Test configuration and fixtures
├── unit/                            # Unit tests for all modules
├── security/                        # Security and safety tests
└── system/                          # Integration and system tests

testing/                             # Production validation testing
├── comprehensive_tool_test_suite.py # Real-world tool scenario testing
├── intensive_stress_test.py         # Memory and performance stress testing  
├── real_world_memory_test.py        # Live model interaction validation
└── COMPREHENSIVE_TESTING_RESULTS.md # Complete testing results and analysis

WorkspaceAI/                         # Auto-created runtime folder
├── workspace/                       # File operations sandbox
├── memory/                          # Conversation history storage
└── config.json                     # User settings and configuration

archive/                             # Historical components and old tests
├── deprecated_components/           # Previous architecture components
└── old tests/                       # Archived obsolete tests

docs/                                # Project documentation
├── architecture/                    # Architectural documentation and design decisions
├── reports/                         # Implementation progress and status reports
└── research/                        # Research notes and experimental findings
```

## Testing Suite

The system includes comprehensive testing across multiple categories.

### Test Categories
- **Unit Tests**: Core module functionality testing
- **Integration Tests**: Cross-component interaction validation  
- **Real-World Testing**: Live model interaction validation
- **Stress Testing**: Performance under load conditions
- **Security Testing**: Safety and validation framework testing

### Running Tests
```bash
# Standard unit tests
python -m pytest tests/

# Tool functionality testing
python testing/comprehensive_tool_test_suite.py

# Performance testing
python testing/intensive_stress_test.py

# Memory system validation
python testing/real_world_memory_test.py

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Results Summary
- Memory usage: Stable during extended operation
- Model isolation: Proper separation maintained
- Context retrieval: 0.004s for 118 messages
- Large context: Handles 15KB+ prompts
- Tool integration: Core functionality operational

## File Operations

Available in workspace sandbox:
- **Core**: create, read, write, delete, copy, move
- **Advanced**: compress, search, metadata, JSON handling
- **Organization**: list, backup, sync folders

## Memory System v3.0

**Model-Specific Memory**: Each model maintains isolated conversation history, preventing cross-contamination between different model interactions.

**Adaptive Context Management**: 
- Chat mode: 60-80% context window utilization based on query complexity
- Tools mode: 80-90% context window utilization based on query complexity
- Intelligent budget allocation between memory and response generation

**Enhanced Reliability**:
- Atomic file operations prevent corruption
- Automatic error recovery and backup creation
- Comprehensive validation at all system levels
- Legacy memory migration support

**Key Features**:
- Per-model memory isolation with collision-safe filename generation
- Complexity-aware context preparation with anti-gaming measures
- Backward compatibility with existing memory interfaces
- Comprehensive safety validation and structured error reporting

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
- `feature/modular-architecture`: Current v3.0 development

---
*AI assistant with modular architecture and secure workspace management.*
