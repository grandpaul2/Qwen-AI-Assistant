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
    Provide a clean workspace directory for each test
    
    Args:
        test_workspace: Base workspace path from session fixture
        
    Yields:
        Path to clean workspace directory
    """
    # Clean the workspace before each test
    if os.path.exists(test_workspace):
        for item in os.listdir(test_workspace):
            item_path = os.path.join(test_workspace, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    
    yield test_workspace


@pytest.fixture
def temp_workspace() -> Generator[str, None, None]:
    """
    Create a temporary workspace directory for a single test
    
    Yields:
        Path to temporary workspace directory
    """
    temp_dir = tempfile.mkdtemp(prefix="workspaceai_temp_")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """
    Provide a sample configuration for testing
    
    Returns:
        Sample configuration dictionary
    """
    return {
        "workspace_path": "/tmp/test_workspace",
        "memory_path": "/tmp/test_memory", 
        "safe_mode": True,
        "auto_save": False,
        "search": {
            "max_file_size": 1024 * 1024,
            "excluded_extensions": [".exe", ".bin"],
            "case_sensitive": False
        },
        "ollama": {
            "host": "localhost",
            "port": 11434,
            "model": "qwen2.5:3b",
            "timeout": 30
        }
    }


@pytest.fixture
def mock_ollama_client():
    """
    Provide a mock Ollama client for testing
    
    Returns:
        Mock OllamaClient instance
    """
    mock_client = Mock(spec=OllamaClient)
    mock_client.chat_completion.return_value = {
        "message": {
            "content": "Test response",
            "role": "assistant"
        }
    }
    mock_client.simple_chat.return_value = "Test response"
    mock_client.test_connection.return_value = True
    return mock_client


@pytest.fixture
def file_manager_instance(temp_workspace: str, sample_config: Dict[str, Any]):
    """
    Provide a FileManager instance for testing
    
    Args:
        temp_workspace: Temporary workspace path
        sample_config: Sample configuration
        
    Returns:
        FileManager instance configured for testing
    """
    config = sample_config.copy()
    config["workspace_path"] = temp_workspace
    return FileManager(config)


@pytest.fixture
def memory_manager_instance(temp_workspace: str, sample_config: Dict[str, Any]):
    """
    Provide a MemoryManager instance for testing
    
    Args:
        temp_workspace: Temporary workspace path
        sample_config: Sample configuration
        
    Returns:
        MemoryManager instance configured for testing
    """
    config = sample_config.copy()
    config["memory_path"] = os.path.join(temp_workspace, "memory")
    config["auto_save"] = False  # Disable auto-save for tests
    return MemoryManager(config)


# Common test utilities
def create_test_file(workspace_path: str, filename: str, content: str = "test content") -> str:
    """
    Create a test file in the workspace
    
    Args:
        workspace_path: Path to workspace
        filename: Name of file to create
        content: Content to write to file
        
    Returns:
        Full path to created file
    """
    file_path = os.path.join(workspace_path, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path


def create_test_directory(workspace_path: str, dirname: str) -> str:
    """
    Create a test directory in the workspace
    
    Args:
        workspace_path: Path to workspace
        dirname: Name of directory to create
        
    Returns:
        Full path to created directory
    """
    dir_path = os.path.join(workspace_path, dirname)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


@pytest.fixture
def temp_files_workspace(temp_workspace: str) -> str:
    """
    Create a workspace with some test files
    
    Args:
        temp_workspace: Temporary workspace path
        
    Returns:
        Path to workspace with test files
    """
    # Create some test files
    create_test_file(temp_workspace, "test1.txt", "Hello World")
    create_test_file(temp_workspace, "test2.py", "print('Hello Python')")
    create_test_file(temp_workspace, "subdir/test3.md", "# Test Markdown")
    create_test_file(temp_workspace, "data.json", '{"key": "value"}')
    
    return temp_workspace


# Disable warnings for tests
@pytest.fixture(autouse=True)
def disable_warnings():
    """
    Disable warnings during test execution
    """
    import warnings
    warnings.filterwarnings("ignore")
