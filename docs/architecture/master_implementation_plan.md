# WorkspaceAI Universal Tool System - Master Implementation Plan

## Current Status Summary

### ✅ WORKING NOW (Ready for qwen2.5:3b)
- **Calculator**: Mathematical expressions (`2 + 2 * 3` → `8`)
- **Python Code Execution**: Safe code execution with output capture
- **Install Commands**: Software installation instruction generation
- **Tool Schema Generation**: 5 broad tool categories defined
- **File Manager Backend**: 25 file operations fully implemented

### 🔧 PARTIALLY WORKING (Needs Connection)
- **File Operations**: Backend works, universal handler connection broken
- **System Commands**: Framework ready, needs testing
- **Web Operations**: Schema defined, needs implementation
- **System Operations**: Schema defined, needs implementation

## Master Tool List

### 1. FILE OPERATIONS (Priority: HIGH)
**Status**: Backend ✅ / Handler Connection ❌

**Available Methods** (25 total):
- `create_file` - Create files with content
- `read_file` - Read file contents  
- `write_to_file` - Write/overwrite files
- `delete_file` - Delete files
- `list_files` - List directory contents
- `copy_file` - Copy files
- `move_file` - Move/rename files
- `search_files` - Search files by keyword
- `create_folder` - Create directories
- `delete_folder` - Delete directories
- `write_json_file` - Write JSON data
- `read_json_file` - Read/parse JSON
- `write_txt_file` - Write text files
- `write_md_file` - Write markdown files
- `get_file_metadata` - Get file information

**Universal Handler Mappings Needed**:
```python
# Standard names qwen2.5:3b might use:
"file_operations" → dispatch to appropriate method
"create_file" → file_manager.create_file()
"read_file" → file_manager.read_file()
"ls" → file_manager.list_files()
"mkdir" → file_manager.create_folder()
"cp" → file_manager.copy_file()
"mv" → file_manager.move_file()
"rm" → file_manager.delete_file()
```

### 2. CODE EXECUTION (Priority: HIGH)
**Status**: Python ✅ / Multi-language ❌

**Currently Working**:
- Python code execution with output capture
- Safe execution environment
- Print statement capture

**Needs Implementation**:
- Shell/Bash command execution
- PowerShell command execution  
- JavaScript execution (Node.js)
- Multi-language support

**Universal Handler Mappings**:
```python
"code_interpreter" → execute_code(language, code)
"python" → execute_python(code)
"bash" → execute_shell(command)
"shell" → execute_shell(command)
"powershell" → execute_powershell(command)
"javascript" → execute_javascript(code)
"node" → execute_javascript(code)
```

### 3. SYSTEM OPERATIONS (Priority: MEDIUM)
**Status**: Schema ✅ / Implementation ❌

**Capabilities to Implement**:
- System information (OS, CPU, memory, disk space)
- Process management (list, kill, monitor)
- Environment variables
- Network information
- File permissions
- System performance metrics

**Universal Handler Mappings**:
```python
"system_operations" → dispatch based on operation
"system_info" → get_system_info()
"disk_space" → get_disk_space()
"processes" → list_processes()
"env" → get_environment()
"kill" → kill_process(pid)
```

### 4. WEB OPERATIONS (Priority: LOW)
**Status**: Schema ✅ / Implementation ❌

**Capabilities to Implement**:
- Web search (if API available)
- URL fetching/downloading
- HTTP requests (GET, POST)
- Web scraping (basic)
- API interactions

**Universal Handler Mappings**:
```python
"web_operations" → dispatch based on operation
"web_search" → search_web(query)
"fetch" → fetch_url(url)
"download" → download_file(url, path)
"http_get" → http_request("GET", url)
"http_post" → http_request("POST", url, data)
```

### 5. CALCULATOR (Priority: COMPLETE ✅)
**Status**: Fully Working

**Current Capabilities**:
- Basic arithmetic (`+`, `-`, `*`, `/`, `**`)
- Parentheses support
- Safe evaluation (no dangerous operations)

### 6. UTILITY TOOLS (Priority: MEDIUM)
**Status**: Partial ✅

**Currently Working**:
- `generate_install_commands` - Software installation instructions

**Could Add**:
- Text processing (regex, format, transform)
- Data conversion (JSON, CSV, XML)
- Encoding/decoding (base64, URL, etc.)
- Hash generation (MD5, SHA256)
- Date/time operations

## Implementation Plan

### Phase 1: Fix File Operations (IMMEDIATE - 30 minutes)
**Goal**: Connect file manager to universal handler

**Tasks**:
1. Fix file manager import in universal handler
2. Map all 25 file operations to handler
3. Test file_operations, create_file, read_file, etc.
4. Verify qwen2.5:3b can call file operations

**Expected Outcome**: qwen2.5:3b can create, read, write, delete, list, copy, move files

### Phase 2: Expand Code Execution (1-2 hours)
**Goal**: Multi-language code execution

**Tasks**:
1. Implement shell command execution
2. Add PowerShell support for Windows
3. Add JavaScript/Node.js execution
4. Add timeout and security controls
5. Test with qwen2.5:3b

**Expected Outcome**: qwen2.5:3b can run any code or system command

### Phase 3: System Operations (2-3 hours)
**Goal**: System information and management

**Tasks**:
1. Implement system info gathering
2. Add process management
3. Add disk/memory monitoring
4. Add environment variable access
5. Test system operations

**Expected Outcome**: qwen2.5:3b can get system info, manage processes

### Phase 4: Web Operations (Optional - 3-4 hours)
**Goal**: Internet connectivity for AI

**Tasks**:
1. Implement basic HTTP requests
2. Add file downloading
3. Add web search (if API available)
4. Add simple web scraping
5. Test web capabilities

**Expected Outcome**: qwen2.5:3b can fetch web content, search internet

### Phase 5: Enhanced Utilities (Future)
**Goal**: Advanced text/data processing

**Tasks**:
1. Text processing tools
2. Data format conversion
3. Encoding/hashing utilities
4. Date/time tools

## Success Metrics

### Phase 1 Success:
- [ ] qwen2.5:3b can create files: `t: create a Python script`
- [ ] qwen2.5:3b can read files: `t: show me the contents of config.json`
- [ ] qwen2.5:3b can list files: `t: what files are in this directory?`
- [ ] qwen2.5:3b can copy/move: `t: copy readme.md to docs folder`

### Phase 2 Success:
- [ ] qwen2.5:3b can run Python: `t: calculate fibonacci numbers with Python`
- [ ] qwen2.5:3b can run shell: `t: list running processes`
- [ ] qwen2.5:3b can run multi-step: `t: create and run a test script`

### Phase 3 Success:
- [ ] qwen2.5:3b can get system info: `t: how much disk space is available?`
- [ ] qwen2.5:3b can manage processes: `t: show me running Python processes`

### Phase 4 Success:
- [ ] qwen2.5:3b can fetch web: `t: download the latest Python installer`
- [ ] qwen2.5:3b can search: `t: search for Python documentation`

## Estimated Timeline

- **Phase 1 (File Ops)**: 30 minutes - CRITICAL
- **Phase 2 (Code Exec)**: 1-2 hours - HIGH IMPACT  
- **Phase 3 (System Ops)**: 2-3 hours - MEDIUM IMPACT
- **Phase 4 (Web Ops)**: 3-4 hours - NICE TO HAVE

**Total for Core Functionality**: ~4-6 hours
**Total for Complete System**: ~7-10 hours

## Next Immediate Action

**START WITH PHASE 1**: Fix file operations connection
- This gives the biggest immediate impact
- Unlocks 25 file operations for qwen2.5:3b
- Takes only 30 minutes
- Provides visible user value

Once file operations work, qwen2.5:3b will be able to handle the majority of common user requests involving file management, which is the core use case for WorkspaceAI.
