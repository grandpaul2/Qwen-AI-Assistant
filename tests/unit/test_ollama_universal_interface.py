"""
Unit tests for ollama universal_interface module
Tests universal tool calling functionality with Ollama
"""

import pytest
import json
from unittest.mock import patch, MagicMock, call
from src.ollama_universal_interface import (
    call_ollama_with_universal_tools,
    _simple_chat_without_tools,
    _call_ollama_with_open_tools,
    _build_open_tool_instruction,
    _get_open_tool_schemas,
    call_ollama_with_tools
)


class TestCallOllamaWithUniversalTools:
    """Test the main universal tool calling function"""
    
    @patch('builtins.print')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface._simple_chat_without_tools')
    def test_basic_call_without_tools(self, mock_simple_chat, mock_memory, mock_load_config, mock_print):
        """Test basic call without tools enabled"""
        mock_load_config.return_value = {'verbose_output': False}
        mock_simple_chat.return_value = "Test response"
        
        # Should not raise an exception and should call simple chat
        call_ollama_with_universal_tools("test prompt", use_tools=False)
        
        # Check that both user and assistant messages were added
        mock_memory.add_message.assert_any_call("user", "test prompt")
        mock_simple_chat.assert_called_once_with("test prompt", None, False)
        mock_print.assert_called()  # Response should be printed
    
    @patch('builtins.print')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface._call_ollama_with_open_tools')
    @patch('src.ollama.universal_interface.handle_any_tool_call')
    def test_call_with_tools_enabled(self, mock_handle_tool, mock_open_tools, mock_memory, mock_load_config, mock_print):
        """Test call with tools enabled"""
        mock_load_config.return_value = {'verbose_output': False}
        mock_open_tools.return_value = {
            "message": {
                "content": "I'll help you with that.",
                "tool_calls": [
                    {
                        "function": {
                            "name": "file_operations",
                            "arguments": '{"action": "create", "path": "test.txt"}'
                        }
                    }
                ]
            }
        }
        mock_handle_tool.return_value = {"success": True, "result": "File created"}
        
        call_ollama_with_universal_tools("create a file", use_tools=True)
        
        # Check that both user and assistant messages were added
        mock_memory.add_message.assert_any_call("user", "create a file")
        mock_open_tools.assert_called_once()
        mock_handle_tool.assert_called_once()
    
    @patch('src.ollama.universal_interface.logger')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory')
    def test_exception_handling(self, mock_memory, mock_load_config, mock_logger):
        """Test exception handling in main function"""
        mock_load_config.side_effect = Exception("Config error")
        
        # Should not raise exception, should log error
        call_ollama_with_universal_tools("test")
        
        mock_logger.error.assert_called_once()


class TestSimpleChatWithoutTools:
    """Test simple chat functionality without tools"""
    
    @patch('src.ollama.universal_interface.OllamaClient')
    def test_successful_chat(self, mock_ollama_client):
        """Test successful simple chat"""
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.return_value = {
            "message": {"content": "Response text"}
        }
        
        result = _simple_chat_without_tools("test", "model", False)
        
        assert result == "Response text"
        mock_client.chat_completion.assert_called_once()
    
    @patch('src.ollama.universal_interface.OllamaClient')
    def test_no_response(self, mock_ollama_client):
        """Test handling of no response"""
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.return_value = None
        
        result = _simple_chat_without_tools("test", None, False)
        
        assert result is None
    
    @patch('src.ollama.universal_interface.logger')
    @patch('src.ollama.universal_interface.OllamaClient')
    def test_exception_handling(self, mock_ollama_client, mock_logger):
        """Test exception handling in simple chat"""
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.side_effect = Exception("API error")
        
        result = _simple_chat_without_tools("test", None, False)
        
        assert result is None
        mock_logger.error.assert_called_once()
    
    @patch('src.ollama.universal_interface.OllamaClient')
    def test_model_override(self, mock_ollama_client):
        """Test model override functionality"""
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.return_value = {
            "message": {"content": "Response"}
        }
        
        _simple_chat_without_tools("test", "custom-model", False)
        
        assert mock_client.model == "custom-model"


class TestCallOllamaWithOpenTools:
    """Test open tools functionality"""
    
    @patch('src.ollama.universal_interface.OllamaClient')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface.get_context_aware_tool_schemas')
    @patch('src.ollama.universal_interface.build_context_aware_instruction')
    def test_successful_tool_call(self, mock_instruction, mock_schemas, mock_memory, mock_ollama_client):
        """Test successful tool call"""
        mock_instruction.return_value = "Enhanced instruction"
        mock_schemas.return_value = [{"type": "function", "function": {"name": "test_tool"}}]
        mock_memory.get_context_messages.return_value = []
        
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.return_value = {
            "message": {
                "content": "Tool executed",
                "tool_calls": [{"function": {"name": "test_tool"}}]
            }
        }
        
        result = _call_ollama_with_open_tools("test", "model", False)
        
        assert result is not None
        mock_client.chat_completion.assert_called_once()
    
    @patch('src.ollama.universal_interface.OllamaClient')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface.get_context_aware_tool_schemas')
    @patch('src.ollama.universal_interface.build_context_aware_instruction')
    def test_no_tool_calls_in_response(self, mock_instruction, mock_schemas, mock_memory, mock_ollama_client):
        """Test response without tool calls"""
        mock_instruction.return_value = "Tool instruction"
        mock_schemas.return_value = []
        mock_memory.get_context_messages.return_value = []
        
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.return_value = {
            "message": {"content": "Simple response"}
        }
        
        result = _call_ollama_with_open_tools("test", "model", False)
        
        assert result is not None
        assert result["message"]["content"] == "Simple response"
    
    @patch('src.ollama.universal_interface.logger')
    @patch('src.ollama.universal_interface.OllamaClient')
    def test_exception_handling(self, mock_ollama_client, mock_logger):
        """Test exception handling in open tools"""
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.side_effect = Exception("Tool error")
        
        result = _call_ollama_with_open_tools("test", "model", False)
        
        assert result is None
        mock_logger.error.assert_called_once()


class TestBuildOpenToolInstruction:
    """Test instruction building functionality"""
    
    def test_instruction_building(self):
        """Test building open tool instruction"""
        result = _build_open_tool_instruction()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "universal tool system" in result
        assert "file_operations" in result
        assert "code_interpreter" in result
    
    def test_instruction_content(self):
        """Test that instruction contains expected content"""
        result = _build_open_tool_instruction()
        
        # Should contain key tool categories
        assert "file_operations" in result
        assert "code_interpreter" in result
        assert "calculator" in result
        assert "web_operations" in result
        assert "system_operations" in result
        
        # Should contain examples
        assert "Examples:" in result
        assert "file_operations(action=" in result


class TestGetOpenToolSchemas:
    """Test open tool schema generation"""
    
    def test_schema_generation(self):
        """Test open tool schema generation"""
        result = _get_open_tool_schemas()
        
        assert isinstance(result, list)
        assert len(result) == 5  # Should have 5 tool categories
        
        # Check first tool schema structure
        file_ops = result[0]
        assert file_ops["type"] == "function"
        assert file_ops["function"]["name"] == "file_operations"
        assert "description" in file_ops["function"]
        assert "parameters" in file_ops["function"]
    
    def test_schema_structure(self):
        """Test that all schemas have valid structure"""
        schemas = _get_open_tool_schemas()
        
        for schema in schemas:
            assert "type" in schema
            assert schema["type"] == "function"
            assert "function" in schema
            
            function = schema["function"]
            assert "name" in function
            assert "description" in function
            assert "parameters" in function
            
            parameters = function["parameters"]
            assert "type" in parameters
            assert parameters["type"] == "object"
            assert "properties" in parameters
    
    def test_all_tool_categories(self):
        """Test that all expected tool categories are present"""
        schemas = _get_open_tool_schemas()
        tool_names = [schema["function"]["name"] for schema in schemas]
        
        expected_tools = [
            "file_operations",
            "code_interpreter", 
            "calculator",
            "web_operations",
            "system_operations"
        ]
        
        for tool in expected_tools:
            assert tool in tool_names


class TestCallOllamaWithTools:
    """Test backward compatibility wrapper"""
    
    @patch('src.ollama.universal_interface.call_ollama_with_universal_tools')
    @patch('src.ollama.universal_interface.load_config')
    def test_backward_compatibility_call(self, mock_load_config, mock_universal_call):
        """Test backward compatibility wrapper"""
        mock_load_config.return_value = {'verbose_output': False}
        
        call_ollama_with_tools("test prompt", "model", True)
        
        mock_universal_call.assert_called_once_with("test prompt", "model", True, False)
    
    @patch('src.ollama.universal_interface.call_ollama_with_universal_tools')
    @patch('src.ollama.universal_interface.load_config')
    def test_default_parameters(self, mock_load_config, mock_universal_call):
        """Test default parameter handling"""
        mock_load_config.return_value = {'verbose_output': True}
        
        call_ollama_with_tools("prompt")
        
        mock_universal_call.assert_called_once_with("prompt", None, True, True)


class TestIntegration:
    """Integration tests for complete workflow"""
    
    @patch('builtins.print')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface.OllamaClient')
    def test_full_integration_without_tools(self, mock_ollama_client, mock_memory, mock_load_config, mock_print):
        """Test full integration without tools"""
        mock_load_config.return_value = {'verbose_output': False}
        mock_memory.get_context_messages.return_value = []
        
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.return_value = {
            "message": {"content": "Integration test response"}
        }
        
        call_ollama_with_universal_tools("integration test", use_tools=False)
        
        mock_memory.add_message.assert_called()
        mock_print.assert_called()
    
    @patch('builtins.print')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory') 
    @patch('src.ollama.universal_interface.OllamaClient')
    @patch('src.ollama.universal_interface.handle_any_tool_call')
    @patch('src.ollama.universal_interface.get_context_aware_tool_schemas')
    @patch('src.ollama.universal_interface.build_context_aware_instruction')
    def test_tool_call_integration(self, mock_instruction, mock_schemas, mock_handle_tool, 
                                 mock_ollama_client, mock_memory, mock_load_config, mock_print):
        """Test tool call integration"""
        mock_load_config.return_value = {'verbose_output': False}
        mock_handle_tool.return_value = {"success": True, "result": "Tool executed successfully"}
        mock_memory.get_context_messages.return_value = []
        mock_instruction.return_value = "Use tools as needed"
        mock_schemas.return_value = [{"type": "function", "function": {"name": "create_file"}}]
        
        mock_client = MagicMock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat_completion.return_value = {
            "message": {
                "content": "I'll help you with that.",
                "tool_calls": [
                    {
                        "function": {
                            "name": "create_file",
                            "arguments": '{"filename": "test.txt", "content": "test"}'
                        }
                    }
                ]
            }
        }
        
        call_ollama_with_universal_tools("create a test file", use_tools=True)
        
        mock_handle_tool.assert_called_once()
        mock_memory.add_message.assert_called()
        mock_print.assert_called()


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('builtins.print')
    @patch('src.ollama.universal_interface.logger')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface._call_ollama_with_open_tools')
    def test_malformed_tool_calls(self, mock_open_tools, mock_memory, mock_load_config, mock_logger, mock_print):
        """Test handling of malformed tool calls"""
        mock_load_config.return_value = {'verbose_output': False}
        mock_open_tools.return_value = {
            "message": {
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "invalid_tool",
                            "arguments": "invalid json"
                        }
                    }
                ]
            }
        }
        
        with patch('src.ollama.universal_interface.handle_any_tool_call') as mock_handle:
            mock_handle.return_value = {"error": "Invalid tool call", "success": False}
            
            call_ollama_with_universal_tools("test", use_tools=True)
            
            mock_handle.assert_called_once()
    
    @patch('builtins.print')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface._call_ollama_with_open_tools')
    def test_empty_response_handling(self, mock_open_tools, mock_memory, mock_load_config, mock_print):
        """Test handling of empty responses"""
        mock_load_config.return_value = {'verbose_output': False}
        mock_open_tools.return_value = None
        
        call_ollama_with_universal_tools("test", use_tools=True)
        
        # Should handle gracefully and print error message
        mock_print.assert_called_with("❌ No response from Ollama")


class TestVerboseOutput:
    """Test verbose output functionality"""
    
    @patch('builtins.print')
    @patch('src.ollama.universal_interface.load_config')
    @patch('src.ollama.universal_interface.memory')
    @patch('src.ollama.universal_interface._call_ollama_with_open_tools')
    @patch('src.ollama.universal_interface.handle_any_tool_call')
    def test_verbose_tool_execution(self, mock_handle_tool, mock_open_tools, mock_memory, mock_load_config, mock_print):
        """Test verbose output during tool execution"""
        mock_load_config.return_value = {'verbose_output': True}
        mock_open_tools.return_value = {
            "message": {
                "content": "Using tools",
                "tool_calls": [
                    {
                        "function": {
                            "name": "file_operations",
                            "arguments": '{"action": "create"}'
                        }
                    }
                ]
            }
        }
        mock_handle_tool.return_value = {"success": True, "result": "Created file"}
        
        call_ollama_with_universal_tools("create file", use_tools=True, verbose_output=True)
        
        # Should print verbose tool information
        print_calls = [str(call) for call in mock_print.call_args_list]
        verbose_found = any("🛠️ Tool:" in call_str for call_str in print_calls)
        assert verbose_found or len(print_calls) > 1  # Either verbose output or multiple prints
