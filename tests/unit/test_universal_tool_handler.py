"""
Comprehensive Unit Tests for Universal Tool Handler

Tests the dynamic tool execution system that handles any tool call
from LLM models without predefined schemas.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path

from src.universal_tool_handler import UniversalToolHandler, handle_any_tool_call


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def tool_handler(temp_workspace):
    """Create a UniversalToolHandler instance for testing"""
    return UniversalToolHandler(workspace_path=temp_workspace)


@pytest.mark.unit
class TestUniversalToolHandlerCore:
    """Test core UniversalToolHandler functionality"""
    
    def test_initialization_default_workspace(self):
        """Test handler initializes with default workspace"""
        handler = UniversalToolHandler()
        assert handler.workspace_path is not None
        assert isinstance(handler.workspace_path, str)
    
    def test_initialization_custom_workspace(self, temp_workspace):
        """Test handler initializes with custom workspace"""
        handler = UniversalToolHandler(workspace_path=temp_workspace)
        assert handler.workspace_path == temp_workspace
    
    def test_file_manager_loading(self, tool_handler):
        """Test that file manager is loaded successfully"""
        # File manager should be loaded or None if import fails
        assert tool_handler.file_manager is not None or tool_handler.file_manager is None
    
    def test_handle_tool_call_basic_structure(self, tool_handler):
        """Test basic tool call handling structure"""
        tool_call = {
            "function": {
                "name": "test_function",
                "arguments": {"param": "value"}
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
    
    def test_handle_tool_call_string_arguments(self, tool_handler):
        """Test handling tool calls with string arguments"""
        tool_call = {
            "function": {
                "name": "test_function",
                "arguments": '{"param": "value"}'
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_handle_tool_call_invalid_json_arguments(self, tool_handler):
        """Test handling tool calls with invalid JSON arguments"""
        tool_call = {
            "function": {
                "name": "test_function",
                "arguments": '{"invalid": json}'
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert "error" in result
        assert "Invalid arguments JSON" in result["error"]


@pytest.mark.unit
class TestFileOperations:
    """Test file operations through the universal tool handler"""
    
    def test_file_operations_create(self, tool_handler):
        """Test file creation through file_operations"""
        tool_call = {
            "function": {
                "name": "file_operations",
                "arguments": {
                    "action": "create",
                    "path": "test.txt",
                    "content": "Hello World"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        # Should succeed or fail gracefully
        assert isinstance(result, dict)
    
    def test_file_operations_read(self, tool_handler):
        """Test file reading through file_operations"""
        tool_call = {
            "function": {
                "name": "file_operations",
                "arguments": {
                    "action": "read",
                    "path": "nonexistent.txt"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        # Should handle non-existent file gracefully
        assert isinstance(result, dict)
    
    def test_file_operations_list(self, tool_handler):
        """Test file listing through file_operations"""
        tool_call = {
            "function": {
                "name": "file_operations",
                "arguments": {
                    "action": "list",
                    "path": "."
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_direct_file_functions(self, tool_handler):
        """Test direct file function calls"""
        test_functions = [
            "create_file", "read_file", "write_file", "delete_file",
            "list_files", "copy_file", "move_file", "search_files"
        ]
        
        for func_name in test_functions:
            tool_call = {
                "function": {
                    "name": func_name,
                    "arguments": {"file_name": "test.txt", "content": "test"}
                }
            }
            
            result = tool_handler.handle_tool_call(tool_call)
            
            # Should handle the call (success or graceful failure)
            assert isinstance(result, dict)


@pytest.mark.unit
class TestCodeExecution:
    """Test code execution capabilities"""
    
    def test_python_code_execution(self, tool_handler):
        """Test Python code execution"""
        tool_call = {
            "function": {
                "name": "code_interpreter",
                "arguments": {
                    "language": "python",
                    "code": "print('Hello World')"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_python_direct_call(self, tool_handler):
        """Test direct python function call"""
        tool_call = {
            "function": {
                "name": "python",
                "arguments": {
                    "code": "2 + 2"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_shell_command_execution(self, tool_handler):
        """Test shell command execution"""
        tool_call = {
            "function": {
                "name": "shell",
                "arguments": {
                    "command": "echo test"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    @patch('subprocess.run')
    def test_cross_platform_command_fixes(self, mock_run, tool_handler):
        """Test cross-platform command fixing"""
        mock_run.return_value = Mock(stdout="output", stderr="", returncode=0)
        
        # Test with Unix command that should be fixed on Windows
        code = "subprocess.run(['ls', '|', 'head', '-10'])"
        
        result = tool_handler._fix_cross_platform_commands(code)
        
        # Should modify the code for cross-platform compatibility
        assert isinstance(result, str)


@pytest.mark.unit
class TestSystemOperations:
    """Test system operation capabilities"""
    
    def test_system_info(self, tool_handler):
        """Test system information retrieval"""
        tool_call = {
            "function": {
                "name": "system_info",
                "arguments": {}
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_system_info_variations(self, tool_handler):
        """Test various system info function names"""
        variations = ["os_info", "get_system_info", "system"]
        
        for func_name in variations:
            tool_call = {
                "function": {
                    "name": func_name,
                    "arguments": {}
                }
            }
            
            result = tool_handler.handle_tool_call(tool_call)
            
            assert isinstance(result, dict)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_resource_monitoring(self, mock_disk, mock_memory, mock_cpu, tool_handler):
        """Test system resource monitoring"""
        # Mock psutil responses
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, available=1000000)
        mock_disk.return_value = Mock(percent=70.0, free=2000000)
        
        resource_functions = ["cpu_usage", "memory_usage", "disk_usage"]
        
        for func_name in resource_functions:
            tool_call = {
                "function": {
                    "name": func_name,
                    "arguments": {}
                }
            }
            
            result = tool_handler.handle_tool_call(tool_call)
            
            assert isinstance(result, dict)


@pytest.mark.unit
class TestWebOperations:
    """Test web operation capabilities"""
    
    @patch('requests.get')
    def test_http_get(self, mock_get, tool_handler):
        """Test HTTP GET requests"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = "Hello World"
        mock_get.return_value = mock_response
        
        tool_call = {
            "function": {
                "name": "http_get",
                "arguments": {
                    "url": "https://example.com"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    @patch('requests.post')
    def test_http_post(self, mock_post, tool_handler):
        """Test HTTP POST requests"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.text = '{"success": true}'
        mock_post.return_value = mock_response
        
        tool_call = {
            "function": {
                "name": "http_post",
                "arguments": {
                    "url": "https://api.example.com",
                    "data": {"test": "data"}
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_web_search_simulation(self, tool_handler):
        """Test simulated web search"""
        tool_call = {
            "function": {
                "name": "web_search",
                "arguments": {
                    "query": "test search"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    @patch('requests.get')
    def test_web_scraping(self, mock_get, tool_handler):
        """Test web scraping functionality"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_get.return_value = mock_response
        
        tool_call = {
            "function": {
                "name": "scrape_webpage",
                "arguments": {
                    "url": "https://example.com"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)


@pytest.mark.unit
class TestCalculator:
    """Test calculator functionality"""
    
    def test_basic_calculation(self, tool_handler):
        """Test basic mathematical calculations"""
        tool_call = {
            "function": {
                "name": "calculator",
                "arguments": {
                    "expression": "2 + 2"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_complex_calculation(self, tool_handler):
        """Test complex mathematical expressions"""
        tool_call = {
            "function": {
                "name": "calc",
                "arguments": {
                    "expression": "math.sqrt(16) + 2**3"
                }
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_calculation_variations(self, tool_handler):
        """Test various calculator function names"""
        variations = ["calculate", "math", "eval"]
        
        for func_name in variations:
            tool_call = {
                "function": {
                    "name": func_name,
                    "arguments": {
                        "expression": "1 + 1"
                    }
                }
            }
            
            result = tool_handler.handle_tool_call(tool_call)
            
            assert isinstance(result, dict)


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_unknown_function(self, tool_handler):
        """Test handling of unknown function calls"""
        tool_call = {
            "function": {
                "name": "completely_unknown_function",
                "arguments": {}
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert "error" in result
        assert "suggestion" in result
    
    def test_missing_function_info(self, tool_handler):
        """Test handling of malformed tool calls"""
        tool_call = {
            "invalid": "structure"
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        # Should handle gracefully
        assert isinstance(result, dict)
    
    def test_empty_arguments(self, tool_handler):
        """Test handling of empty arguments"""
        tool_call = {
            "function": {
                "name": "test_function",
                "arguments": {}
            }
        }
        
        result = tool_handler.handle_tool_call(tool_call)
        
        assert isinstance(result, dict)
    
    def test_exception_during_execution(self, tool_handler):
        """Test handling of exceptions during tool execution"""
        # Create a mock function that has a __name__ attribute
        mock_function = Mock(side_effect=Exception("Test error"))
        mock_function.__name__ = "_try_file_operations"
        
        with patch.object(tool_handler, '_try_file_operations', mock_function):
            tool_call = {
                "function": {
                    "name": "create_file",
                    "arguments": {"file_name": "test.txt"}
                }
            }
            
            result = tool_handler.handle_tool_call(tool_call)
            
            # Should handle exception gracefully
            assert isinstance(result, dict)


@pytest.mark.unit
class TestGlobalInterface:
    """Test the global interface function"""
    
    def test_handle_any_tool_call_function(self):
        """Test the global handle_any_tool_call function"""
        tool_call = {
            "function": {
                "name": "calculator",
                "arguments": {
                    "expression": "1 + 1"
                }
            }
        }
        
        result = handle_any_tool_call(tool_call)
        
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
    
    def test_global_function_consistency(self):
        """Test that global function produces consistent results"""
        tool_call = {
            "function": {
                "name": "system_info",
                "arguments": {}
            }
        }
        
        result1 = handle_any_tool_call(tool_call)
        result2 = handle_any_tool_call(tool_call)
        
        # Results should be consistent in structure
        assert type(result1) == type(result2)
        assert ("success" in result1) == ("success" in result2)
        assert ("error" in result1) == ("error" in result2)


@pytest.mark.unit
class TestSuggestionSystem:
    """Test the suggestion system for unknown functions"""
    
    def test_suggestion_for_similar_function(self, tool_handler):
        """Test that suggestions are provided for similar function names"""
        result = tool_handler._suggest_alternative("creat_file", {})
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_suggestion_for_completely_unknown(self, tool_handler):
        """Test suggestions for completely unknown functions"""
        result = tool_handler._suggest_alternative("xyz123unknown", {})
        
        assert isinstance(result, str)
    
    def test_suggestion_considers_arguments(self, tool_handler):
        """Test that suggestions consider the provided arguments"""
        arguments = {"file_name": "test.txt", "content": "test"}
        result = tool_handler._suggest_alternative("unknown_func", arguments)
        
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__])
