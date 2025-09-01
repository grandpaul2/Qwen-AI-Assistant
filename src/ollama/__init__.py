"""
Ollama client package for WorkspaceAI

This package provides modular components for Ollama API integration:
- Core API client for connection and requests
- Tool execution and parameter handling  
- Response formatting and output processing
- Function validation and auto-correction
"""

from .client import OllamaClient
from .tool_executor import ToolExecutor
from .response_formatter import ResponseFormatter
from .parameter_extractor import ParameterExtractor
from .function_validator import FunctionValidator

# Maintain backward compatibility
from .legacy_interface import (
    call_ollama_with_tools,
    detect_file_intent,
    test_ollama_connection,
    enhanced_tool_selection_pipeline
)

__all__ = [
    'OllamaClient',
    'ToolExecutor', 
    'ResponseFormatter',
    'ParameterExtractor',
    'FunctionValidator',
    'call_ollama_with_tools',
    'detect_file_intent',
    'test_ollama_connection',
    'enhanced_tool_selection_pipeline'
]
