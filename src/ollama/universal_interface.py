"""
Dynamic Tool Interface for WorkspaceAI

This module implements a completely open tool system where any LLM model can call
any tool it wants, and we'll attempt to execute it dynamically.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List

from .client import OllamaClient
from ..universal_tool_handler import handle_any_tool_call
from ..memory import memory
from ..config import load_config, get_workspace_path
from ..progress import show_progress
from ..enhanced_tool_instructions import build_enhanced_tool_instruction, get_context_aware_tool_schemas, build_context_aware_instruction

logger = logging.getLogger(__name__)

# ANSI colors for output
CYAN = "\033[96m"
RESET = "\033[0m"


def call_ollama_with_universal_tools(
    prompt: str, 
    model: Optional[str] = None, 
    use_tools: bool = True,
    verbose_output: Optional[bool] = None
):
    """
    Call Ollama with universal tool support - no predefined schemas.
    
    The model can call any tool it wants, and we'll attempt to execute it.
    
    Args:
        prompt: User input
        model: Optional model override
        use_tools: Whether to enable tool calling
        verbose_output: Whether to show debug information
    """
    try:
        # Load configuration
        config = load_config()
        if verbose_output is None:
            verbose_output = config.get('verbose_output', False)
        
        # Store user message
        memory.add_message("user", prompt)
        
        if not use_tools:
            # Simple chat without tools
            response = _simple_chat_without_tools(prompt, model, verbose_output)
            if response:
                print(f"\n{CYAN}{response}{RESET}")
                memory.add_message("assistant", response)
                memory.save_memory_async()
            return
        
        # Call Ollama with open tool calling
        response = _call_ollama_with_open_tools(prompt, model, verbose_output)
        
        if response and "message" in response:
            message = response["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])
            
            # Handle any tool calls the model made
            if tool_calls:
                for tool_call in tool_calls:
                    result = handle_any_tool_call(tool_call)
                    
                    if verbose_output:
                        print(f"🛠️ Tool: {tool_call.get('function', {}).get('name', 'unknown')}")
                        print(f"📊 Result: {result}")
                    
                    if result.get("success"):
                        print(f"\n{result['result']}")
                    elif result.get("error"):
                        print(f"❌ Tool Error: {result['error']}")
                        if result.get("suggestion"):
                            print(f"💡 Suggestion: {result['suggestion']}")
            
            # Handle text response from model
            if content:
                print(f"\n{CYAN}{content}{RESET}")
                memory.add_message("assistant", content, tool_calls)
                memory.save_memory_async()
            
        else:
            print("❌ No response from Ollama")
            
    except Exception as e:
        logger.error(f"Error in universal tool call: {e}")
        print(f"❌ An error occurred: {e}")


def _simple_chat_without_tools(prompt: str, model: Optional[str], verbose_output: bool) -> Optional[str]:
    """Simple chat without any tool calling"""
    try:
        client = OllamaClient()
        if model:
            client.model = model
        
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(messages, tools=None)
        
        if response and "message" in response:
            return response["message"].get("content", "")
        
        return None
        
    except Exception as e:
        logger.error(f"Error in simple chat: {e}")
        return None


def _call_ollama_with_open_tools(prompt: str, model: Optional[str], verbose_output: bool) -> Optional[Dict]:
    """
    Call Ollama with completely open tool calling.
    
    Instead of sending predefined tool schemas, we send a general instruction
    that the model can call any tool it thinks is appropriate.
    """
    try:
        client = OllamaClient()
        if model:
            client.model = model
        
        # Build context messages
        context_messages = memory.get_context_messages()
        
        # Define flexible tool schemas
        open_tools = get_context_aware_tool_schemas()
        
        # Create context-aware tool instruction
        workspace_path = os.getcwd()  # Current working directory as workspace
        try:
            system_message = build_context_aware_instruction(prompt, workspace_path, open_tools)
        except Exception as e:
            # Fallback to basic enhanced instruction if context analysis fails
            logger.warning(f"Context analysis failed, using basic instruction: {e}")
            system_message = build_enhanced_tool_instruction()
        
        if context_messages:
            context_messages.append({"role": "system", "content": system_message})
        else:
            context_messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        
        # Define flexible tool schemas that cover broad categories
        open_tools = get_context_aware_tool_schemas()
        
        if verbose_output:
            print(f"🔧 Available tool categories: {[tool['function']['name'] for tool in open_tools]}")
        
        # Make the API call
        response = client.chat_completion(context_messages, open_tools)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in open tool call: {e}")
        return None


def _build_open_tool_instruction() -> str:
    """
    Build instruction that tells the model it can call any tool.
    """
    return """You have access to a universal tool system that can handle a wide variety of operations.

Available tool categories:
1. file_operations - Any file or directory operations (create, read, write, delete, list, copy, move, search)
2. code_interpreter - Execute any code or system commands
3. calculator - Mathematical calculations and expressions
4. web_operations - Web-related operations (search, fetch, etc.)
5. system_operations - System information and management

You can call these tools with any parameters you think are appropriate. The system will attempt to handle your tool calls dynamically.

For file operations, you can use actions like: create, read, write, delete, list, copy, move, search
For code execution, you can run Python code, shell commands, etc.
For calculations, you can evaluate mathematical expressions.

Don't worry about exact parameter names - the system will interpret your intent.

Examples:
- file_operations(action="create", path="notes.txt", content="Hello world")
- code_interpreter(language="python", code="print('Hello world')")
- calculator(expression="2 + 2 * 3")
- file_operations(action="list", path=".")

Call the appropriate tools to help the user with their request."""


def _get_open_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get flexible tool schemas that can handle broad categories of operations.
    
    These are intentionally generic to allow the model maximum flexibility.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "file_operations",
                "description": "Perform any file or directory operation including create, read, write, delete, list, copy, move, search files and folders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string", 
                            "description": "The operation to perform: create, read, write, delete, list, copy, move, search, etc."
                        },
                        "path": {
                            "type": "string",
                            "description": "File or directory path"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content for create/write operations or search query"
                        },
                        "destination": {
                            "type": "string", 
                            "description": "Destination path for copy/move operations"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "code_interpreter",
                "description": "Execute code in various languages or run system commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {
                            "type": "string",
                            "description": "Programming language: python, bash, powershell, javascript, etc."
                        },
                        "code": {
                            "type": "string",
                            "description": "Code to execute or command to run"
                        },
                        "command": {
                            "type": "string", 
                            "description": "System command to execute"
                        }
                    }
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "calculator",
                "description": "Perform mathematical calculations and evaluate expressions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_operations", 
                "description": "Perform web-related operations like searching or fetching content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation type: search, fetch, download, etc."
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query or URL"
                        },
                        "url": {
                            "type": "string",
                            "description": "URL for fetch/download operations"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "system_operations",
                "description": "Get system information or perform system management tasks",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "System operation: info, disk_space, processes, etc."
                        },
                        "target": {
                            "type": "string",
                            "description": "Target for the operation"
                        }
                    }
                }
            }
        }
    ]


# Backward compatibility function
def call_ollama_with_tools(prompt: str, model: Optional[str] = None, use_tools: bool = True):
    """
    Backward compatible interface that routes to universal tool system.
    """
    config = load_config()
    verbose_output = config.get('verbose_output', False)
    
    call_ollama_with_universal_tools(prompt, model, use_tools, verbose_output)
