# Tool Architecture Analysis: How WorkspaceAI Uses Ollama Tools

## Overview
WorkspaceAI integrates with Ollama's **native tool calling capabilities**. We're not creating our own tool execution system - we're leveraging Ollama's built-in function calling feature.

## Architecture Flow

```
User Input: t: create a file called test.txt
     ↓
Main Interface (src/main.py)
     ↓ calls call_ollama_with_tools(use_tools=True)
Enhanced Interface (src/ollama/enhanced_interface.py)
     ↓ two execution paths:

Path 1: Direct Tool Execution (Fast Path)
     ↓
Tool Executor (src/ollama/tool_executor.py)
     ↓ generates parameters from prompt
File Manager (src/file_manager.py)
     ↓ executes actual file operation
Result returned to user

Path 2: LLM-Guided Tool Execution (Full Path)
     ↓
Context-Aware Pipeline
     ↓ 1. Intent Classification
     ↓ 2. Smart Tool Selection  
     ↓ 3. Confidence Assessment
Ollama API Call with Tools
     ↓ POST /api/chat with tools array
Ollama LLM Response
     ↓ returns tool_calls in JSON format
Tool Call Executor (src/ollama/legacy_interface.py)
     ↓ executes _execute_tool_call()
File Manager (src/file_manager.py)
     ↓ executes actual file operation
Result returned to user
```

## Key Components

### 1. Ollama Native Tool Calling
- **Location**: `src/ollama/client.py`
- **Method**: `chat_completion(messages, tools)`
- **API**: Uses Ollama's `/api/chat` endpoint with `tools` parameter
- **Format**: Tools sent as JSON schemas following OpenAI function calling format

### 2. Tool Schema Definition
- **Location**: `src/tool_schemas.py`
- **Purpose**: Defines available tools in JSON schema format
- **Current Tools**:
  - `create_file` - Create any type of file
  - `write_to_file` - Write/overwrite file content
  - `read_file` - Read file contents
  - `delete_file` - Delete a file
  - `generate_install_commands` - Generate installation instructions

### 3. Dual Execution Paths

#### Fast Path (Direct Execution)
- **When**: Simple, unambiguous requests
- **How**: Extract parameters directly from user prompt
- **Benefits**: No LLM call needed, instant execution
- **Example**: "t: create file test.txt" → direct parameter extraction

#### Full Path (LLM-Guided)
- **When**: Complex or ambiguous requests
- **How**: Let Ollama's LLM decide which tools to call and with what parameters
- **Benefits**: Handles complex scenarios, natural language understanding
- **Example**: "t: help me organize my project files" → LLM analyzes and calls multiple tools

### 4. Tool Selection Intelligence
- **Context-Aware**: Uses conversation history and file state
- **Multi-Step Planning**: Can execute sequences of operations
- **Auto-Correction**: Fixes common function name and parameter errors

## Tool Call Flow in Detail

1. **Tool Schema Registration**
   ```python
   tools = get_all_tool_schemas()  # JSON schemas for Ollama
   response = client.chat_completion(messages, tools)
   ```

2. **Ollama Response Processing**
   ```python
   tool_calls = response["message"]["tool_calls"]
   for tool_call in tool_calls:
       _execute_tool_call(tool_call)
   ```

3. **Tool Execution**
   ```python
   function_name = tool_call["function"]["name"]
   function_args = tool_call["function"]["arguments"] 
   result = file_manager.function_name(**function_args)
   ```

## Benefits of This Architecture

1. **Native Integration**: Uses Ollama's built-in tool calling (no custom parsing)
2. **Standards Compliant**: OpenAI-compatible function calling format
3. **Flexible**: Can handle both simple and complex tool requests
4. **Intelligent**: LLM understands context and can plan multi-step operations
5. **Extensible**: Easy to add new tools by updating schemas

## Current Optimization Opportunities

1. **Fast Path Enhancement**: Improve direct parameter extraction for common patterns
2. **Tool Selection**: Optimize the context-aware pipeline for better tool choice
3. **Error Handling**: Better fallback when tool execution fails
4. **User Feedback**: Show which tools are being called and why (in verbose mode)

## Answer to Your Question

Yes, we ARE using Ollama's native tool calling capabilities! We're not inventing our own tool system - we're leveraging Ollama's built-in function calling feature by:

1. Sending tool schemas to Ollama in the standard format
2. Letting Ollama's LLM decide which tools to call
3. Executing the tools Ollama selects with the parameters it provides
4. Returning results back to the user

This gives us the best of both worlds: the intelligence of a modern LLM for tool selection, plus our own file management capabilities for execution.
