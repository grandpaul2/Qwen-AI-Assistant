# WorkspaceAI v3.0 - Complete Project Outline

## Project Overview
WorkspaceAI is an AI assistant with a universal tool system and secure file management capabilities. The project uses a modular architecture designed for collaborative development and works with Ollama models (optimized for qwen2.5:3b).

## Repository Structure

### Root Level
```
WorkspaceAI_project/
├── main.py                 # Entry point that bootstraps the application
├── README.md              # Primary documentation and quick start guide
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration and metadata
├── install_linux.sh       # Linux installation script
└── workspaceai.py         # Legacy/standalone version (archived functionality)
```

## Core Architecture (`src/`)

The `src/` directory contains the modular core of the application:

### Main Components
```
src/
├── __init__.py                      # Package initialization and exports
├── app.py                          # Main application logic and interface orchestration
├── config.py                       # Configuration management and settings
├── memory.py                       # Conversation memory and persistence system
├── file_manager.py                 # Secure file operations within workspace sandbox
├── universal_tool_handler.py       # Dynamic tool execution engine
├── tool_schemas.py                 # Tool definitions and validation schemas
├── enhanced_tool_instructions.py   # Context-aware tool instruction system
├── utils.py                        # Shared utility functions
├── exceptions.py                   # Custom exception hierarchy
├── progress.py                     # Progress display and user feedback
└── software_installer.py           # Cross-platform software installation helpers
```

### Ollama Integration (`src/ollama/`)
```
src/ollama/
├── client.py                # Ollama API client implementation
├── universal_interface.py   # Unified Ollama interaction interface
└── connection_test.py       # Connectivity and setup testing
```

## Runtime Environment (`WorkspaceAI/`)

Auto-created runtime folder for application data:
```
WorkspaceAI/
├── config.json             # Runtime configuration settings
├── workspace/              # Sandboxed file operations directory
└── memory/                 # Persistent conversation history storage
```

## Testing Infrastructure (`tests/`)

Comprehensive testing system organized by test type:

### Test Categories
```
tests/
├── __init__.py             # Test package initialization
├── conftest.py             # Pytest configuration and fixtures
├── automated_bot_testing.py        # Automated bot behavior testing
├── interactive_bot_test.py         # Interactive testing interface
├── interactive_tool_detection.py   # Tool detection validation
├── quick_test_commands.py          # Fast test command suite
├── quick_tool_test.py              # Rapid tool functionality testing
├── run_all_tests.py                # Master test runner
├── test_infrastructure.py          # Test infrastructure utilities
├── security/                       # Security and vulnerability tests
├── unit/                          # Unit tests for individual modules
└── system/                        # Integration and system-level tests
```

### Security Tests (`tests/security/`)
- Input validation and sanitization
- File system security boundaries
- Code execution safety
- Configuration security

### Unit Tests (`tests/unit/`)
- Individual module functionality
- Function-level testing
- Mock-based isolated testing
- Edge case validation

### System Tests (`tests/system/`)
- End-to-end workflow testing
- Integration between modules
- Performance and load testing
- Cross-platform compatibility

## Documentation (`docs/`)

Comprehensive project documentation organized by purpose:

### Documentation Structure
```
docs/
├── architecture/           # Architectural documentation and design decisions
├── reports/               # Implementation progress and status reports
└── research/              # Research notes and experimental findings
```

### Architecture Documentation (`docs/architecture/`)
- System design and component relationships
- API specifications and interfaces
- Database and persistence layer design
- Security architecture and threat model
- Deployment and scaling considerations

### Reports (`docs/reports/`)
- Implementation progress tracking
- Error handling improvement reports
- Testing enhancement plans
- Performance analysis
- Code quality metrics

### Research (`docs/research/`)
- Technology evaluation and comparisons
- Experimental feature prototypes
- Performance optimization research
- Integration pattern studies

## Archive (`archive/`)

Historical and deprecated components for reference:

### Archive Structure
```
archive/
├── .git/                   # Git repository history
├── .github/               # GitHub workflows and templates
├── deprecated_components/ # Obsolete modules and legacy code
└── old tests/            # Previous testing implementations
```

### Deprecated Components (`archive/deprecated_components/`)
- Legacy tool selection systems
- Obsolete context management
- Retired intent classification modules
- Old architecture implementations

### GitHub Workflows (`archive/.github/`)
- Previous CI/CD configurations
- Historical workflow definitions
- Archived automation scripts

### Old Tests (`archive/old tests/`)
- Legacy test implementations
- Historical test data and results
- Retired testing frameworks

## Key Features and Capabilities

### Universal Tool System
- **Dynamic Tool Execution**: Handles requests without predefined schemas
- **Intent Detection**: Automatic mapping from natural language to tool functions
- **18+ File Operations**: Create, read, write, delete, copy, move, compress
- **Code Execution**: Multi-language support (Python, JavaScript, Shell, PowerShell)
- **System Operations**: Process management, system info, network utilities
- **Web Operations**: HTTP requests, web scraping, search capabilities
- **Calculator**: Safe mathematical expression evaluation

### Security and Sandboxing
- **Workspace Isolation**: All operations contained in `WorkspaceAI/workspace/`
- **Safe Mode**: Configurable protection against destructive operations
- **Input Validation**: Comprehensive sanitization and validation
- **Path Security**: Prevents directory traversal and unauthorized access

### Memory and Persistence
- **Recent Memory**: 2 full conversations retained
- **History Management**: 20 AI-summarized conversations
- **Cross-Session Persistence**: Automatic save/restore functionality
- **Configurable Retention**: Adjustable memory policies

### Configuration Management
- **Runtime Configuration**: Dynamic settings in `WorkspaceAI/config.json`
- **Environment Detection**: Cross-platform compatibility
- **Model Configuration**: Ollama model selection and optimization
- **Feature Toggles**: Safe mode and verbose output controls

## Development Workflow

### Entry Point Flow
1. `main.py` → Bootstrap and error handling
2. `src.app.main()` → Application initialization
3. Interactive mode or batch processing
4. Tool detection and execution
5. Memory persistence and cleanup

### Tool Execution Pipeline
1. Natural language input processing
2. Intent classification and tool mapping
3. Parameter extraction and validation
4. Secure execution within sandbox
5. Result formatting and user feedback

### Error Handling Strategy
- Custom exception hierarchy in `src/exceptions.py`
- Graceful degradation and recovery
- Comprehensive logging and diagnostics
- User-friendly error messages

## Collaboration Guidelines

### Module Responsibilities
- **app.py**: Application orchestration and user interface
- **file_manager.py**: All file system operations and security
- **memory.py**: Conversation state and persistence
- **universal_tool_handler.py**: Tool discovery and execution
- **tool_schemas.py**: Tool definitions and validation
- **ollama/**: External AI model integration

### Testing Requirements
- Unit tests for all new functionality
- Security tests for file operations
- Integration tests for tool workflows
- Performance benchmarks for critical paths

### Documentation Standards
- Inline code documentation (docstrings)
- Architecture decision records (ADRs)
- API documentation for public interfaces
- User-facing documentation updates

## Dependencies and Requirements

### Core Dependencies
- **Python 3.7+**: Minimum runtime requirement
- **Ollama**: AI model hosting and inference
- **requests**: HTTP client functionality
- **tqdm**: Progress display and user feedback

### Development Dependencies
- **pytest**: Testing framework
- **pytest-cov**: Code coverage analysis
- **black**: Code formatting
- **flake8**: Linting and style checking

## Future Roadmap

### Planned Enhancements
- Enhanced tool schema validation
- Improved natural language processing
- Extended platform support
- Advanced memory management
- Plugin architecture for custom tools

### Performance Optimization
- Caching layer for frequent operations
- Async/await support for I/O operations
- Memory usage optimization
- Startup time improvements

### Security Hardening
- Enhanced input validation
- Audit logging capabilities
- Privilege escalation prevention
- Code execution isolation

---

This outline provides a comprehensive view of the WorkspaceAI project structure, designed to facilitate collaborative development and maintenance while ensuring security, modularity, and extensibility.
