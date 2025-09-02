"""
Unit tests for exceptions module
Tests all custom exception classes and error handling utilities
"""

import pytest
from unittest.mock import patch, MagicMock
from src.exceptions import (
    WorkspaceAIError,
    ConfigurationError,
    ConfigFileError,
    PackageManagerError,
    OllamaConnectionError,
    IntentError,
    AmbiguousIntentError,
    UnknownIntentError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolParameterError,
    MemoryError,
    ConversationError,
    handle_exception,
    log_and_raise
)


"""
Unit tests for exceptions module
Tests all custom exception classes and error handling utilities
"""

import pytest
from unittest.mock import patch, MagicMock
from src.exceptions import (
    WorkspaceAIError,
    ConfigurationError,
    ConfigFileError,
    PackageManagerError,
    OllamaConnectionError,
    IntentError,
    AmbiguousIntentError,
    UnknownIntentError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolParameterError,
    MemoryError,
    ConversationError,
    handle_exception,
    log_and_raise
)


class TestExceptionHierarchy:
    """Test exception class hierarchy and inheritance"""
    
    def test_base_exception_hierarchy(self):
        """Test that all exceptions inherit from WorkspaceAIError"""
        # Configuration exceptions
        assert issubclass(ConfigurationError, WorkspaceAIError)
        assert issubclass(ConfigFileError, ConfigurationError)
        
        # Package manager exceptions
        assert issubclass(PackageManagerError, WorkspaceAIError)
        
        # Ollama exceptions
        assert issubclass(OllamaConnectionError, WorkspaceAIError)
        
        # Intent exceptions
        assert issubclass(IntentError, WorkspaceAIError)
        assert issubclass(AmbiguousIntentError, IntentError)
        assert issubclass(UnknownIntentError, IntentError)
        
        # Tool execution exceptions
        assert issubclass(ToolExecutionError, WorkspaceAIError)
        assert issubclass(ToolNotFoundError, ToolExecutionError)
        assert issubclass(ToolParameterError, ToolExecutionError)
        
        # Memory and conversation exceptions
        assert issubclass(MemoryError, WorkspaceAIError)
        assert issubclass(ConversationError, WorkspaceAIError)

    def test_exception_instantiation(self):
        """Test that exceptions can be instantiated with messages"""
        msg = "Test error message"
        
        # Test base exception
        error = WorkspaceAIError(msg)
        assert str(error) == msg
        
        # Test configuration exceptions
        config_error = ConfigurationError(msg)
        assert str(config_error) == msg
        
        file_error = ConfigFileError(msg)
        assert str(file_error) == msg
        
        # Test package manager exception
        pm_error = PackageManagerError(msg)
        assert str(pm_error) == msg
        
        # Test Ollama exception
        ollama_error = OllamaConnectionError(msg)
        assert str(ollama_error) == msg
        
        # Test intent exceptions
        intent_error = IntentError(msg)
        assert str(intent_error) == msg
        
        ambiguous_error = AmbiguousIntentError(msg)
        assert str(ambiguous_error) == msg
        
        unknown_error = UnknownIntentError(msg)
        assert str(unknown_error) == msg
        
        # Test tool execution exceptions
        tool_error = ToolExecutionError(msg)
        assert str(tool_error) == msg
        
        not_found_error = ToolNotFoundError(msg)
        assert str(not_found_error) == msg
        
        param_error = ToolParameterError(msg)
        assert str(param_error) == msg
        
        # Test memory and conversation exceptions
        mem_error = MemoryError(msg)
        assert str(mem_error) == msg
        
        conv_error = ConversationError(msg)
        assert str(conv_error) == msg


class TestExceptionMessages:
    """Test exception message handling"""
    
    def test_empty_message(self):
        """Test exceptions with empty messages"""
        error = WorkspaceAIError("")
        assert str(error) == ""
        
    def test_none_message(self):
        """Test exceptions with None message"""
        error = WorkspaceAIError(None)
        assert str(error) == "None"
        
    def test_complex_message(self):
        """Test exceptions with complex messages"""
        msg = "Error in file '/path/to/file.txt' at line 42: Invalid configuration"
        error = ConfigFileError(msg)
        assert str(error) == msg


class TestExceptionHandling:
    """Test the handle_exception utility function"""
    
    @patch('logging.getLogger')
    def test_handle_exception_with_logging(self, mock_get_logger):
        """Test handle_exception logs the error"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        error = ConfigurationError("Test config error")
        context = "Testing configuration"
        
        result = handle_exception(context, error)
        
        mock_get_logger.assert_called_once_with('src.exceptions')
        mock_logger.error.assert_called_once_with("Testing configuration: Test config error")
        assert result == error
        
    @patch('logging.getLogger')
    def test_handle_exception_different_types(self, mock_get_logger):
        """Test handle_exception with different exception types"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        errors = [
            (ConfigFileError("Config file not found"), "Config loading"),
            (OllamaConnectionError("Connection timeout"), "Ollama connection"),
            (ToolNotFoundError("Tool not found"), "Tool execution"),
            (MemoryError("Memory load failed"), "Memory system")
        ]
        
        for error, context in errors:
            result = handle_exception(context, error)
            assert result == error
            
        assert mock_logger.error.call_count == len(errors)
        
    @patch('logging.getLogger')
    def test_log_and_raise_backward_compatibility(self, mock_get_logger):
        """Test log_and_raise backward compatibility function"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        error = PackageManagerError("Package manager not found")
        context = "Package detection"
        
        result = log_and_raise(context, error)
        
        mock_get_logger.assert_called_once_with('src.exceptions')
        mock_logger.error.assert_called_once_with("Package detection: Package manager not found")
        assert result == error


class TestSpecificExceptionBehavior:
    """Test specific behaviors of exception classes"""
    
    def test_intent_error_hierarchy(self):
        """Test intent error hierarchy and specificity"""
        # Test that specific intent errors are more specific than general
        ambiguous = AmbiguousIntentError("Multiple matches found")
        unknown = UnknownIntentError("No matches found")
        
        assert isinstance(ambiguous, IntentError)
        assert isinstance(unknown, IntentError)
        assert isinstance(ambiguous, WorkspaceAIError)
        assert isinstance(unknown, WorkspaceAIError)
        
    def test_tool_error_hierarchy(self):
        """Test tool execution error hierarchy"""
        not_found = ToolNotFoundError("Tool 'nonexistent' not found")
        param_error = ToolParameterError("Missing required parameter 'query'")
        
        assert isinstance(not_found, ToolExecutionError)
        assert isinstance(param_error, ToolExecutionError)
        assert isinstance(not_found, WorkspaceAIError)
        assert isinstance(param_error, WorkspaceAIError)
        
    def test_connection_error_context(self):
        """Test OllamaConnectionError in network context"""
        error = OllamaConnectionError("Connection refused to localhost:11434")
        assert "connection" in str(error).lower()
        assert "11434" in str(error)  # Default Ollama port


class TestExceptionChaining:
    """Test exception chaining and cause tracking"""
    
    def test_exception_with_cause(self):
        """Test exceptions can be chained with __cause__"""
        original = ValueError("Original error")
        wrapped = ConfigurationError("Configuration failed")
        wrapped.__cause__ = original
        
        assert wrapped.__cause__ is original
        assert str(wrapped) == "Configuration failed"
        
    def test_raise_from_chain(self):
        """Test 'raise ... from ...' exception chaining"""
        with pytest.raises(ToolExecutionError) as exc_info:
            try:
                raise PermissionError("Access denied")
            except PermissionError as e:
                raise ToolExecutionError("Tool execution failed") from e
                
        assert exc_info.value.__cause__.__class__ == PermissionError
        assert "Access denied" in str(exc_info.value.__cause__)


class TestExceptionSerialization:
    """Test exception serialization for logging/debugging"""
    
    def test_exception_repr(self):
        """Test exception __repr__ method"""
        error = ToolParameterError("Invalid parameter type")
        repr_str = repr(error)
        assert "ToolParameterError" in repr_str
        assert "Invalid parameter type" in repr_str
        
    def test_exception_str_vs_repr(self):
        """Test difference between str() and repr() of exceptions"""
        msg = "Memory validation failed"
        error = MemoryError(msg)
        
        assert str(error) == msg
        assert "MemoryError" in repr(error)
        assert msg in repr(error)


class TestExceptionUseCases:
    """Test realistic exception use cases"""
    
    def test_configuration_workflow(self):
        """Test configuration-related exception workflow"""
        # Config file missing
        with pytest.raises(ConfigFileError):
            raise ConfigFileError("Config file not found: config.json")
            
        # Invalid configuration
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Invalid configuration: missing required field 'api_key'")
    
    def test_tool_execution_workflow(self):
        """Test tool execution exception workflow"""
        # Tool not found
        with pytest.raises(ToolNotFoundError):
            raise ToolNotFoundError("Tool 'generate_code' not found in registry")
            
        # Invalid parameters
        with pytest.raises(ToolParameterError):
            raise ToolParameterError("Missing required parameter 'prompt' for tool 'generate_code'")
    
    def test_intent_classification_workflow(self):
        """Test intent classification exception workflow"""
        # Ambiguous intent
        with pytest.raises(AmbiguousIntentError):
            raise AmbiguousIntentError("Multiple intents match with equal confidence: 'file_create', 'file_write'")
            
        # Unknown intent
        with pytest.raises(UnknownIntentError):
            raise UnknownIntentError("No intent pattern matches input: 'xyzabc123'")
    
    def test_memory_system_workflow(self):
        """Test memory system exception workflow"""
        with pytest.raises(MemoryError):
            raise MemoryError("Failed to load conversation history from memory.json")
    
    def test_ollama_connection_workflow(self):
        """Test Ollama connection exception workflow"""
        with pytest.raises(OllamaConnectionError):
            raise OllamaConnectionError("Failed to connect to Ollama server at localhost:11434")
