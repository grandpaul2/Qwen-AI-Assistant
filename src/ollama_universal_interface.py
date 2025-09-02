"""
Dynamic Tool Interface for WorkspaceAI

This module implements a completely open tool system where any LLM model can call
any tool it wants, and we'll attempt to execute it dynamically.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List

from .ollama_client import OllamaClient
from .universal_tool_handler import handle_any_tool_call
from .memory import memory
from .config import load_config, get_workspace_path
from .progress import show_progress
from .enhanced_tool_instructions import build_enhanced_tool_instruction, get_context_aware_tool_schemas, build_context_aware_instruction

logger = logging.getLogger(__name__)
# ANSI colors for output
CYAN = "\033[96m"
RESET = "\033[0m"

def call_ollama_with_universal_tools(prompt: str, model: Optional[str] = None, use_tools: bool = True, verbose_output: bool = False):
    """
    Call Ollama with universal tool interface; chooses simple chat or open tool calling.
    """
    try:
        config = load_config()
        verbose_output = verbose_output or config.get('verbose_output', False)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        verbose_output = False
        
    # Store user message
    memory.add_message("user", prompt)
    
    if not use_tools:
        response = _simple_chat_without_tools(prompt, model, verbose_output)
        if response:
            print(response)
            memory.add_message("assistant", response)
        return response
    else:
        return _call_ollama_with_open_tools(prompt, model, verbose_output)


def _simple_chat_without_tools(prompt: str, model: Optional[str], verbose_output: Optional[bool]) -> Optional[str]:
    """Simple chat without any tool calling"""
    # Dynamic import for patched client
    from .ollama_client import OllamaClient
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


def _call_ollama_with_open_tools(prompt: str, model: Optional[str], verbose_output: Optional[bool]) -> Optional[Dict[str, Any]]:
    """
    Call Ollama with completely open tool calling.
    
    Instead of sending predefined tool schemas, we send a general instruction
    that the model can call any tool it thinks is appropriate.
    """
    # Dynamic imports for patched client and instruction builders
    from .ollama_client import OllamaClient
    from .enhanced_tool_instructions import (
        get_context_aware_tool_schemas,
        build_context_aware_instruction,
        build_enhanced_tool_instruction,
    )
    try:
        client = OllamaClient()
        if model:
            client.model = model
        # Build context messages
        context_messages = memory.get_context_messages()
        # Define flexible tool schemas
        open_tools = get_context_aware_tool_schemas()
        # Create context-aware tool instruction
        workspace_path = os.getcwd()
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

Examples:
- file_operations(action="create", path="notes.txt", content="Hello world")
- code_interpreter(language="python", code="print('Hello world')")
- calculator(expression="2 + 2 * 3")
- file_operations(action="list", path=".")
"""

# Aliases for tests
_get_open_tool_schemas = get_context_aware_tool_schemas
call_ollama_with_tools = call_ollama_with_universal_tools
