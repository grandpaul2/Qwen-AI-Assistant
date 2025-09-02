"""
Unit Tests for Ollama Connection Test Module
Tests the connection testing utilities for WorkspaceAI
"""

import unittest
from unittest.mock import patch, Mock, MagicMock

from src.ollama.connection_test import test_ollama_connection


class TestOllamaConnectionTest(unittest.TestCase):
    """Test the Ollama connection testing functionality"""

    @patch('src.ollama.connection_test.OllamaClient')
    def test_ollama_connection_success(self, mock_client_class):
        """Test successful Ollama connection"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.test_connection.return_value = True
        
        # Execute
        result = test_ollama_connection()
        
        # Verify
        self.assertTrue(result)
        mock_client_class.assert_called_once()
        mock_client.test_connection.assert_called_once()

    @patch('src.ollama.connection_test.OllamaClient')
    def test_ollama_connection_failure(self, mock_client_class):
        """Test Ollama connection failure"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.test_connection.return_value = False
        
        # Execute
        result = test_ollama_connection()
        
        # Verify
        self.assertFalse(result)
        mock_client_class.assert_called_once()
        mock_client.test_connection.assert_called_once()

    @patch('src.ollama.connection_test.logger')
    @patch('src.ollama.connection_test.OllamaClient')
    def test_ollama_connection_client_creation_exception(self, mock_client_class, mock_logger):
        """Test exception during client creation"""
        # Setup mock
        mock_client_class.side_effect = Exception("Failed to create client")
        
        # Execute
        result = test_ollama_connection()
        
        # Verify
        self.assertFalse(result)
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        self.assertIn("Ollama connection test failed", error_call)
        self.assertIn("Failed to create client", error_call)

    @patch('src.ollama.connection_test.logger')
    @patch('src.ollama.connection_test.OllamaClient')
    def test_ollama_connection_test_method_exception(self, mock_client_class, mock_logger):
        """Test exception during connection test method"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.test_connection.side_effect = ConnectionError("Network unreachable")
        
        # Execute
        result = test_ollama_connection()
        
        # Verify
        self.assertFalse(result)
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        self.assertIn("Ollama connection test failed", error_call)
        self.assertIn("Network unreachable", error_call)

    @patch('src.ollama.connection_test.logger')
    @patch('src.ollama.connection_test.OllamaClient')
    def test_ollama_connection_various_exceptions(self, mock_client_class, mock_logger):
        """Test handling of various exception types"""
        exception_types = [
            ConnectionError("Connection failed"),
            TimeoutError("Request timeout"),
            ValueError("Invalid response"),
            RuntimeError("Runtime error"),
            Exception("Generic error")
        ]
        
        for exception in exception_types:
            with self.subTest(exception=type(exception).__name__):
                # Reset mock
                mock_logger.reset_mock()
                mock_client_class.reset_mock()
                
                # Setup mock for this exception
                mock_client_class.side_effect = exception
                
                # Execute
                result = test_ollama_connection()
                
                # Verify
                self.assertFalse(result)
                mock_logger.error.assert_called_once()
                error_message = mock_logger.error.call_args[0][0]
                self.assertIn("Ollama connection test failed", error_message)
                self.assertIn(str(exception), error_message)

    @patch('src.ollama.connection_test.OllamaClient')
    def test_ollama_connection_client_instantiation(self, mock_client_class):
        """Test that client is instantiated correctly"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.test_connection.return_value = True
        
        # Execute
        test_ollama_connection()
        
        # Verify client instantiation
        mock_client_class.assert_called_once_with()
        
    @patch('src.ollama.connection_test.OllamaClient')
    def test_ollama_connection_return_type(self, mock_client_class):
        """Test that function returns boolean values"""
        # Test True case
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.test_connection.return_value = True
        
        result = test_ollama_connection()
        self.assertIsInstance(result, bool)
        self.assertTrue(result)
        
        # Reset and test False case
        mock_client.test_connection.return_value = False
        result = test_ollama_connection()
        self.assertIsInstance(result, bool)
        self.assertFalse(result)
        
        # Test exception case
        mock_client_class.side_effect = Exception("Error")
        result = test_ollama_connection()
        self.assertIsInstance(result, bool)
        self.assertFalse(result)


class TestConnectionTestIntegration(unittest.TestCase):
    """Integration tests for connection testing"""

    @patch('src.ollama.connection_test.OllamaClient')
    def test_connection_test_workflow(self, mock_client_class):
        """Test the complete connection testing workflow"""
        # Setup mock for successful workflow
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.test_connection.return_value = True
        
        # Execute multiple times to ensure consistency
        results = [test_ollama_connection() for _ in range(3)]
        
        # Verify consistent behavior
        self.assertTrue(all(results))
        self.assertEqual(mock_client_class.call_count, 3)
        self.assertEqual(mock_client.test_connection.call_count, 3)

    @patch('src.ollama.connection_test.logger')
    @patch('src.ollama.connection_test.OllamaClient')
    def test_error_logging_format(self, mock_client_class, mock_logger):
        """Test that error logging follows expected format"""
        # Setup mock
        test_error = ConnectionError("Specific connection error")
        mock_client_class.side_effect = test_error
        
        # Execute
        test_ollama_connection()
        
        # Verify error logging format
        mock_logger.error.assert_called_once()
        logged_message = mock_logger.error.call_args[0][0]
        
        # Check format components
        self.assertTrue(logged_message.startswith("Ollama connection test failed:"))
        self.assertIn("Specific connection error", logged_message)
        
        # Verify it's an f-string format (contains the exception)
        self.assertIn(str(test_error), logged_message)


class TestConnectionTestErrorConditions(unittest.TestCase):
    """Test various error conditions for connection testing"""

    @patch('src.ollama.connection_test.logger')
    @patch('src.ollama.connection_test.OllamaClient')
    def test_network_related_errors(self, mock_client_class, mock_logger):
        """Test handling of network-related errors"""
        network_errors = [
            ConnectionError("Connection refused"),
            TimeoutError("Connection timeout"),
            OSError("Network is unreachable")
        ]
        
        for error in network_errors:
            with self.subTest(error=type(error).__name__):
                # Reset mocks
                mock_logger.reset_mock()
                mock_client_class.reset_mock()
                
                # Setup error
                mock_client_class.side_effect = error
                
                # Execute
                result = test_ollama_connection()
                
                # Verify error handling
                self.assertFalse(result)
                mock_logger.error.assert_called_once()

    @patch('src.ollama.connection_test.logger')
    @patch('src.ollama.connection_test.OllamaClient')
    def test_configuration_errors(self, mock_client_class, mock_logger):
        """Test handling of configuration-related errors"""
        config_errors = [
            ValueError("Invalid host configuration"),
            TypeError("Invalid parameter type"),
            AttributeError("Missing configuration attribute")
        ]
        
        for error in config_errors:
            with self.subTest(error=type(error).__name__):
                # Reset mocks
                mock_logger.reset_mock()
                mock_client_class.reset_mock()
                
                # Setup error
                mock_client_class.side_effect = error
                
                # Execute
                result = test_ollama_connection()
                
                # Verify error handling
                self.assertFalse(result)
                mock_logger.error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
