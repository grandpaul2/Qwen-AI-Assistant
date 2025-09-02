"""
Pytest configuration and shared fixtures for WorkspaceAI tests

This module provides common fixtures, test configuration, and utilities
used across all test modules.
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, Generator

# Add src to path for importing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import APP_CONFIG
from src.file_manager import FileManager
from src.memory import MemoryManager
from src.ollama_client import OllamaClient


@pytest.fixture(scope="session")
def test_workspace() -> Generator[str, None, None]:
    """
    Create a temporary workspace directory for testing
    
    Yields:
        Path to temporary workspace directory
    """
    temp_dir = tempfile.mkdtemp(prefix="workspaceai_test_")
    workspace_path = os.path.join(temp_dir, "workspace")
    os.makedirs(workspace_path, exist_ok=True)
    
    yield workspace_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def clean_workspace(test_workspace: str) -> Generator[str, None, None]:
    """
    Provide a clean workspace for each test
    
    Args:
        test_workspace: Session-level workspace fixture
        
    Yields:
        Path to clean workspace directory
    """
    # Clean the workspace before each test
    if os.path.exists(test_workspace):
        for item in os.listdir(test_workspace):
            item_path = os.path.join(test_workspace, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    
    yield test_workspace


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """
    Provide test configuration
    
    Returns:
        Test configuration dictionary
    """
    return {
        'model': 'test-model',
        'safe_mode': True,
        'ollama_host': 'localhost:11434',
        'search_max_file_kb': 1024,
        'verbose_output': False
    }


@pytest.fixture
def file_manager_instance(clean_workspace: str, test_config: Dict[str, Any]) -> FileManager:
    """
    Create a FileManager instance with test workspace
    
    Args:
        clean_workspace: Clean workspace fixture
        test_config: Test configuration
        
    Returns:
        FileManager instance configured for testing
    """
    config = test_config.copy()
    
    # Use a custom FileManager that uses our test workspace
    class TestFileManager(FileManager):
        def __init__(self, config, workspace_path):
            super().__init__(config)
            self.base_path = workspace_path
    
    return TestFileManager(config, clean_workspace)


@pytest.fixture
def memory_manager_instance(clean_workspace: str) -> MemoryManager:
    """
    Create a MemoryManager instance with test workspace
    
    Args:
        clean_workspace: Clean workspace fixture
        
    Returns:
        MemoryManager instance configured for testing
    """
    # Create a temporary memory file in the test workspace
    memory_dir = os.path.join(clean_workspace, "memory")
    os.makedirs(memory_dir, exist_ok=True)
    
    class TestMemoryManager(MemoryManager):
        def __init__(self, memory_dir):
            super().__init__()
            self.memory_file = os.path.join(memory_dir, "memory.json")
    
    return TestMemoryManager(memory_dir)


@pytest.fixture
def mock_ollama_client() -> Mock:
    """
    Create a mock Ollama client for testing
    
    Returns:
        Mock OllamaClient instance
    """
    mock_client = Mock(spec=OllamaClient)
    mock_client.test_connection.return_value = True
    mock_client.simple_chat.return_value = "Mock response"
    mock_client.chat_completion.return_value = {
        "message": {
            "content": "Mock completion response",
            "tool_calls": []
        }
    }
    return mock_client


@pytest.fixture
def sample_prompts() -> Dict[str, list[str]]:
    """
    Provide sample prompts for testing
    
    Returns:
        Dictionary of sample prompts categorized by intent
    """
    return {
        'content_creation': [
            "create a file called notes.txt with my todo list",
            "write me a Python script named hello.py",
            "make a markdown file for documentation",
            "save this as config.json",
            "generate a CSV file with data"
        ],
        'file_management': [
            "list all files in the directory",
            "read the contents of readme.txt",
            "copy notes.txt to backup.txt",
            "delete old_file.txt",
            "search for files containing 'project'"
        ],
        'software_installation': [
            "install Python",
            "how to install Git on Windows",
            "setup VS Code",
            "install commands for Docker",
            "get Node.js installation steps"
        ],
        'unclear': [
            "what's the weather?",
            "hello",
            "how are you?",
            "tell me a joke",
            "what time is it?"
        ]
    }


@pytest.fixture
def mock_ollama_responses() -> Dict[str, Dict[str, Any]]:
    """
    Provide mock Ollama API responses
    
    Returns:
        Dictionary of mock responses for different scenarios
    """
    return {
        'simple_chat': {
            "message": {
                "content": "This is a simple chat response"
            }
        },
        'tool_call_create_file': {
            "message": {
                "content": "I'll create that file for you.",
                "tool_calls": [{
                    "function": {
                        "name": "create_file",
                        "arguments": {
                            "file_name": "test.txt",
                            "content": "Test content"
                        }
                    }
                }]
            }
        },
        'tool_call_list_files': {
            "message": {
                "content": "Here are the files:",
                "tool_calls": [{
                    "function": {
                        "name": "list_files",
                        "arguments": {}
                    }
                }]
            }
        },
        'error_response': {
            "error": "Model not found"
        }
    }


@pytest.fixture
def sample_files(clean_workspace: str) -> Dict[str, str]:
    """
    Create sample files in the test workspace
    
    Args:
        clean_workspace: Clean workspace fixture
        
    Returns:
        Dictionary mapping filenames to their content
    """
    files = {
        'sample.txt': 'This is a sample text file for testing.',
        'data.json': '{"key": "value", "number": 42}',
        'readme.md': '# Test README\n\nThis is a test markdown file.',
        'script.py': 'print("Hello, World!")\n# This is a test Python script',
        'config.ini': '[section]\nkey=value\nanother_key=another_value'
    }
    
    for filename, content in files.items():
        filepath = os.path.join(clean_workspace, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return files


@pytest.fixture(autouse=True)
def reset_global_state():
    """
    Reset global state before each test
    
    This fixture automatically runs before each test to ensure
    clean state and prevent test interference.
    """
    # Reset any global variables or singletons here
    yield
    # Cleanup after test if needed


# Test markers are configured in pytest_configure function below


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")  
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
