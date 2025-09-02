"""
Test infrastructure validation

This test ensures our testing setup is working correctly.
"""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.mark.unit
def test_pytest_working():
    """Test that pytest is working correctly"""
    assert True
    assert 1 + 1 == 2
    assert "hello" == "hello"


@pytest.mark.unit
def test_fixtures_available(test_workspace, test_config, sample_prompts):
    """Test that our fixtures are working"""
    # Test workspace fixture
    assert os.path.exists(test_workspace)
    assert os.path.isdir(test_workspace)
    
    # Test config fixture
    assert isinstance(test_config, dict)
    assert 'model' in test_config
    assert 'safe_mode' in test_config
    
    # Test sample prompts fixture
    assert isinstance(sample_prompts, dict)
    assert 'content_creation' in sample_prompts
    assert 'file_management' in sample_prompts


@pytest.mark.unit
def test_file_manager_fixture(file_manager_instance):
    """Test that file manager fixture works"""
    assert file_manager_instance is not None
    assert hasattr(file_manager_instance, 'create_file')
    assert hasattr(file_manager_instance, 'base_path')
    assert os.path.exists(file_manager_instance.base_path)


@pytest.mark.unit  
def test_mock_ollama_client(mock_ollama_client):
    """Test that mock Ollama client works"""
    assert mock_ollama_client is not None
    assert mock_ollama_client.test_connection() is True
    
    response = mock_ollama_client.simple_chat("test prompt")
    assert response == "Mock response"


@pytest.mark.unit
def test_sample_files_fixture(sample_files, clean_workspace):
    """Test that sample files are created correctly"""
    assert isinstance(sample_files, dict)
    assert len(sample_files) > 0
    
    # Check that files actually exist
    for filename, content in sample_files.items():
        filepath = os.path.join(clean_workspace, filename)
        assert os.path.exists(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            assert f.read() == content


@pytest.mark.unit
def test_workspace_isolation(clean_workspace):
    """Test that each test gets a clean workspace"""
    test_file = os.path.join(clean_workspace, "isolation_test.txt")
    
    # Create a file
    with open(test_file, 'w') as f:
        f.write("test content")
    
    assert os.path.exists(test_file)


@pytest.mark.unit
def test_workspace_isolation_second(clean_workspace):
    """Test that workspace is actually clean between tests"""
    test_file = os.path.join(clean_workspace, "isolation_test.txt")
    
    # This file should NOT exist from the previous test
    assert not os.path.exists(test_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
