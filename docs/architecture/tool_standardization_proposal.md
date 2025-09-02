# Proposal: Standardize WorkspaceAI Tools to Match Industry Conventions

## Problem
Our current tools are domain-specific and don't align with standard AI tool conventions, causing confusion for users familiar with other AI systems.

## Current Tools (Domain-Specific)
1. `create_file` - Create a new file with content
2. `write_to_file` - Write/overwrite file content  
3. `read_file` - Read file contents
4. `delete_file` - Delete a file
5. `generate_install_commands` - Generate installation instructions

## Proposed Standard Tools

### 1. `file_operations` (Standard Name)
**Description**: Comprehensive file management operations
**Parameters**:
- `action`: "create", "read", "write", "delete", "list", "move", "copy"
- `path`: File path
- `content`: Content (for create/write operations)
- `destination`: Destination path (for move/copy operations)

**Benefits**:
- Single tool covers all file operations
- Matches industry standards
- Familiar to users of other AI systems
- Extensible for future file operations

### 2. `code_interpreter` (Standard Name)  
**Description**: Execute code and scripts
**Parameters**:
- `language`: "python", "bash", "powershell", "javascript"
- `code`: Code to execute
- `args`: Optional arguments

**Benefits**:
- Standard name used by GPT, Claude, etc.
- Can handle installation commands via script execution
- More powerful than our current `generate_install_commands`

### 3. `web_search` (Standard Name)
**Description**: Search the internet for information
**Parameters**:
- `query`: Search query
- `max_results`: Maximum number of results

**Benefits**:
- Standard tool in most AI systems
- Useful for finding documentation, solutions
- Could help with software installation research

### 4. `calculator` (Standard Name)
**Description**: Perform mathematical calculations
**Parameters**:
- `expression`: Mathematical expression to evaluate

**Benefits**:
- Standard tool name
- Useful for file size calculations, etc.

## Migration Strategy

### Phase 1: Add Standard Tools Alongside Current Ones
- Implement new standard tools
- Keep existing tools for backward compatibility
- Update tool selection logic to prefer standard tools

### Phase 2: Update Tool Selection
- Modify `SmartToolSelector` to map user requests to standard tools
- Update tool schemas with standard names
- Test with existing conversations

### Phase 3: Deprecate Custom Tools (Optional)
- Phase out domain-specific tools
- Migrate all functionality to standard tools
- Update documentation

## Implementation Example

```python
# Current
{
    "type": "function",
    "function": {
        "name": "create_file",
        "description": "Create a new file with specified content",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["file_name", "content"]
        }
    }
}

# Proposed Standard
{
    "type": "function", 
    "function": {
        "name": "file_operations",
        "description": "Perform file system operations",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "read", "write", "delete", "list", "move", "copy"],
                    "description": "The file operation to perform"
                },
                "path": {
                    "type": "string", 
                    "description": "File or directory path"
                },
                "content": {
                    "type": "string",
                    "description": "Content for create/write operations"
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path for move/copy operations"
                }
            },
            "required": ["action", "path"]
        }
    }
}
```

## Benefits of Standardization

1. **User Familiarity**: Users coming from ChatGPT, Claude, etc. will recognize tools
2. **Industry Alignment**: Follows established conventions
3. **Reduced Confusion**: Clear, standard tool names
4. **Better Integration**: Could potentially work with other AI systems
5. **Extensibility**: Standard patterns make it easier to add new capabilities

## Recommendation

Start with implementing `file_operations` as our primary tool, keeping it compatible with Ollama's tool calling format but using industry-standard naming conventions.
