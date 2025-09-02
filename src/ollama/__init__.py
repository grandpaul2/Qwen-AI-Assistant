"""
Ollama client package for WorkspaceAI

This package provides modular components for Ollama API integration:
- Core API client for connection and requests
- Universal tool interface for dynamic tool execution
- Connection testing utilities
"""

from .client import OllamaClient
from .universal_interface import call_ollama_with_tools
from .connection_test import test_ollama_connection

__all__ = [
    'OllamaClient',
    'call_ollama_with_tools',
    'test_ollama_connection'
]
