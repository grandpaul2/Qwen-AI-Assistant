"""
WorkspaceAI v3.0 - Enhanced AI Assistant with File Management and Memory
Modular architecture for collaborative development
"""

__version__ = "3.0"
__author__ = "Grandpaul"

# Import main components for easy access
from .config import CONSTANTS, APP_CONFIG
from .memory import MemoryManager, memory
from .file_manager import FileManager, file_manager
from .ollama import call_ollama_with_tools
from .app import main, interactive_mode

__all__ = [
    'CONSTANTS', 'APP_CONFIG', 'MemoryManager', 'FileManager', 
    'call_ollama_with_tools', 'main', 'interactive_mode',
    'memory', 'file_manager'
]
