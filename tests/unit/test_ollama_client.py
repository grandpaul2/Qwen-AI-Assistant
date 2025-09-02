"""
Unit Tests for Ollama Client Module
Tests API communication, connection testing, and request/response handling
"""

import unittest
import json
from unittest.mock import patch, Mock, MagicMock
import requests

# Mock the config module entirely to avoid any interactive behavior
with patch('src.config.load_config') as mock_load_config:
    mock_load_config.return_value = {
        'model': 'qwen2.5:3b',
        'ollama_host': 'localhost:11434'
    }
    from src.ollama_client import OllamaClient, get_default_client


class TestOllamaClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.default_config = {
            'model': 'qwen2.5:3b',
            'ollama_host': 'localhost:11434'
        }
    
    def test_client_initialization_with_config(self):
        """Test client initialization with provided config"""
        config = {
            'model': 'llama3:8b',
            'ollama_host': 'remote-host:11434'
        }
        client = OllamaClient(config)
        
        self.assertEqual(client.model, 'llama3:8b')
        self.assertEqual(client.base_url, 'http://remote-host:11434')
        self.assertEqual(client.config, config)
    
    @patch('src.ollama_client.load_config')
    def test_client_initialization_without_config(self, mock_load_config):
        """Test client initialization without provided config"""
        mock_load_config.return_value = self.default_config
        
        client = OllamaClient()
        
        self.assertEqual(client.model, 'qwen2.5:3b')
        self.assertEqual(client.base_url, 'http://localhost:11434')
        mock_load_config.assert_called_once()
    
    @patch('src.ollama_client.load_config')
    def test_client_initialization_with_none_config(self, mock_load_config):
        """Test client initialization with None config"""
        mock_load_config.return_value = self.default_config
        
        client = OllamaClient(None)
        
        self.assertEqual(client.model, 'qwen2.5:3b')
        mock_load_config.assert_called_once()
    
    @patch('src.ollama_client.CONSTANTS', {'MODEL': 'default-model', 'API_TIMEOUT': 30, 'API_MAX_RETRIES': 3})
    def test_client_initialization_with_defaults(self):
        """Test client initialization with default constants"""
        client = OllamaClient({})
        
        self.assertEqual(client.model, 'default-model')
        self.assertEqual(client.base_url, 'http://localhost:11434')
        self.assertEqual(client.timeout, 30)
        self.assertEqual(client.max_retries, 3)


class TestOllamaClientConnection(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = OllamaClient({
            'model': 'qwen2.5:3b',
            'ollama_host': 'localhost:11434'
        })
    
    @patch('src.ollama_client.requests.get')
    @patch('builtins.print')
    def test_connection_successful_model_available(self, mock_print, mock_get):
        """Test successful connection with model available"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "qwen2.5:3b"},
                {"name": "llama3:8b"}
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.client.test_connection()
        
        self.assertTrue(result)
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)
        mock_print.assert_called_with("✅ Connected to Ollama - qwen2.5:3b is available")
    
    @patch('src.ollama_client.requests.get')
    @patch('builtins.print')
    def test_connection_successful_model_not_available(self, mock_print, mock_get):
        """Test successful connection but model not available"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3:8b"},
                {"name": "codellama:7b"}
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.client.test_connection()
        
        self.assertFalse(result)
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)
        mock_print.assert_any_call("⚠️ Connected to Ollama but qwen2.5:3b not found")
        mock_print.assert_any_call("Available models: llama3:8b, codellama:7b")
        mock_print.assert_any_call("Run: ollama pull qwen2.5:3b")
    
    @patch('src.ollama_client.requests.get')
    @patch('builtins.print')
    def test_connection_successful_no_models(self, mock_print, mock_get):
        """Test successful connection but no models available"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        result = self.client.test_connection()
        
        self.assertFalse(result)
        mock_print.assert_any_call("Available models: none")
    
    @patch('src.ollama_client.requests.get')
    @patch('builtins.print')
    def test_connection_server_error(self, mock_print, mock_get):
        """Test connection with server error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.client.test_connection()
        
        self.assertFalse(result)
        mock_print.assert_called_with("❌ Ollama responded with status 500")
    
    @patch('src.ollama_client.requests.get')
    @patch('builtins.print')
    def test_connection_request_exception(self, mock_print, mock_get):
        """Test connection with request exception"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = self.client.test_connection()
        
        self.assertFalse(result)
        # Check that both error messages are printed
        mock_print.assert_any_call("❌ Cannot connect to Ollama")
        mock_print.assert_any_call("Make sure Ollama is running: ollama serve")
    
    @patch('src.ollama_client.requests.get')
    @patch('builtins.print')
    def test_connection_timeout_exception(self, mock_print, mock_get):
        """Test connection with timeout exception"""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
        
        result = self.client.test_connection()
        
        self.assertFalse(result)
        mock_print.assert_called_with("❌ Ollama connection timeout")


class TestOllamaClientRequests(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = OllamaClient({
            'model': 'qwen2.5:3b',
            'ollama_host': 'localhost:11434'
        })
    
    @patch('src.ollama_client.requests.post')
    def test_make_request_successful(self, mock_post):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        result = self.client.make_request("/api/test", {"test": "data"})
        
        self.assertEqual(result, mock_response)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "http://localhost:11434/api/test")
        self.assertIn("json", call_args[1])
        self.assertEqual(call_args[1]["json"], {"test": "data"})
    
    @patch('src.ollama_client.requests.post')
    @patch('src.ollama_client.time.sleep')
    def test_make_request_with_retries(self, mock_sleep, mock_post):
        """Test request with retries on timeout"""
        # First call times out, second call succeeds
        mock_post.side_effect = [
            requests.exceptions.Timeout("Request timed out"),
            Mock(status_code=200)
        ]
        
        result = self.client.make_request("/api/test", {"test": "data"})
        
        self.assertIsNotNone(result)
        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once_with(1)
    
    @patch('src.ollama_client.requests.post')
    @patch('src.ollama_client.time.sleep')
    def test_make_request_max_retries_exceeded(self, mock_sleep, mock_post):
        """Test request failing after max retries"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = self.client.make_request("/api/test", {"test": "data"})
        
        self.assertIsNone(result)
        # Should try initial + max_retries times
        expected_calls = 1 + self.client.max_retries
        self.assertEqual(mock_post.call_count, expected_calls)
    
    @patch('src.ollama_client.requests.post')
    def test_make_request_connection_error(self, mock_post):
        """Test request with connection error"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = self.client.make_request("/api/test", {"test": "data"})
        
        self.assertIsNone(result)
        # Should try initial + max_retries times
        expected_calls = 1 + self.client.max_retries
        self.assertEqual(mock_post.call_count, expected_calls)
    
    @patch('src.ollama_client.requests.post')
    def test_make_request_http_error(self, mock_post):
        """Test request with HTTP error"""
        mock_post.side_effect = requests.exceptions.HTTPError("HTTP error")
        
        result = self.client.make_request("/api/test", {"test": "data"})
        
        self.assertIsNone(result)
        mock_post.assert_called_once()
    
    @patch('src.ollama_client.requests.post')
    def test_make_request_unexpected_error(self, mock_post):
        """Test request with unexpected error"""
        mock_post.side_effect = Exception("Unexpected error")
        
        result = self.client.make_request("/api/test", {"test": "data"})
        
        self.assertIsNone(result)
        mock_post.assert_called_once()


class TestOllamaClientChatCompletion(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = OllamaClient({
            'model': 'qwen2.5:3b',
            'ollama_host': 'localhost:11434'
        })
    
    @patch.object(OllamaClient, 'make_request')
    def test_chat_completion_successful(self, mock_make_request):
        """Test successful chat completion"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Hello! How can I help you?"},
            "done": True
        }
        mock_make_request.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = self.client.chat_completion(messages)
        
        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["message"]["content"], "Hello! How can I help you?")
        
        # Verify the request was made with correct data
        call_args = mock_make_request.call_args
        self.assertEqual(call_args[0][0], "/api/chat")
        request_data = call_args[0][1]
        self.assertEqual(request_data["model"], "qwen2.5:3b")
        self.assertEqual(request_data["messages"], messages)
        self.assertEqual(request_data["stream"], False)
    
    @patch.object(OllamaClient, 'make_request')
    def test_chat_completion_with_tools(self, mock_make_request):
        """Test chat completion with tools"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "Response"}}
        mock_make_request.return_value = mock_response
        
        messages = [{"role": "user", "content": "Use a tool"}]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]
        
        result = self.client.chat_completion(messages, tools=tools)
        
        self.assertIsNotNone(result)
        
        # Verify tools were included in request
        call_args = mock_make_request.call_args
        request_data = call_args[0][1]
        self.assertEqual(request_data["tools"], tools)
    
    @patch.object(OllamaClient, 'make_request')
    def test_chat_completion_with_streaming(self, mock_make_request):
        """Test chat completion with streaming enabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "Response"}}
        mock_make_request.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        
        result = self.client.chat_completion(messages, stream=True)
        
        self.assertIsNotNone(result)
        
        # Verify streaming was enabled in request
        call_args = mock_make_request.call_args
        request_data = call_args[0][1]
        self.assertEqual(request_data["stream"], True)
    
    @patch.object(OllamaClient, 'make_request')
    def test_chat_completion_request_failed(self, mock_make_request):
        """Test chat completion when request fails"""
        mock_make_request.return_value = None
        
        messages = [{"role": "user", "content": "Hello"}]
        result = self.client.chat_completion(messages)
        
        self.assertIsNone(result)
    
    @patch.object(OllamaClient, 'make_request')
    def test_chat_completion_invalid_response_status(self, mock_make_request):
        """Test chat completion with invalid response status"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_make_request.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = self.client.chat_completion(messages)
        
        self.assertIsNone(result)
    
    @patch.object(OllamaClient, 'make_request')
    def test_chat_completion_json_decode_error(self, mock_make_request):
        """Test chat completion with JSON decode error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_make_request.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = self.client.chat_completion(messages)
        
        self.assertIsNone(result)


class TestOllamaClientSimpleChat(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = OllamaClient({
            'model': 'qwen2.5:3b',
            'ollama_host': 'localhost:11434'
        })
    
    @patch.object(OllamaClient, 'chat_completion')
    def test_simple_chat_successful(self, mock_chat_completion):
        """Test successful simple chat"""
        mock_chat_completion.return_value = {
            "message": {"content": "Hello! How can I help you?"}
        }
        
        result = self.client.simple_chat("Hello")
        
        self.assertEqual(result, "Hello! How can I help you?")
        
        # Verify chat_completion was called with correct messages
        call_args = mock_chat_completion.call_args
        messages = call_args[0][0]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "Hello")
    
    @patch.object(OllamaClient, 'chat_completion')
    def test_simple_chat_no_response(self, mock_chat_completion):
        """Test simple chat with no response"""
        mock_chat_completion.return_value = None
        
        result = self.client.simple_chat("Hello")
        
        self.assertIsNone(result)
    
    @patch.object(OllamaClient, 'chat_completion')
    def test_simple_chat_no_message_in_response(self, mock_chat_completion):
        """Test simple chat with response missing message"""
        mock_chat_completion.return_value = {"done": True}
        
        result = self.client.simple_chat("Hello")
        
        self.assertIsNone(result)
    
    @patch.object(OllamaClient, 'chat_completion')
    def test_simple_chat_empty_content(self, mock_chat_completion):
        """Test simple chat with empty content"""
        mock_chat_completion.return_value = {
            "message": {"content": ""}
        }
        
        result = self.client.simple_chat("Hello")
        
        self.assertEqual(result, "")
    
    @patch.object(OllamaClient, 'chat_completion')
    def test_simple_chat_missing_content(self, mock_chat_completion):
        """Test simple chat with missing content field"""
        mock_chat_completion.return_value = {
            "message": {"role": "assistant"}
        }
        
        result = self.client.simple_chat("Hello")
        
        self.assertEqual(result, "")


class TestDefaultClient(unittest.TestCase):
    
    def tearDown(self):
        """Clean up after each test"""
        # Reset the global client
        import src.ollama_client
        src.ollama_client._default_client = None
    
    def test_get_default_client_creates_new_client(self):
        """Test that get_default_client creates a new client when none exists"""
        result = get_default_client()
        
        self.assertIsInstance(result, OllamaClient)
        self.assertIsNotNone(result)
    
    @patch('src.ollama_client.OllamaClient')
    def test_get_default_client_returns_existing_client(self, mock_ollama_client):
        """Test that get_default_client returns existing client on subsequent calls"""
        mock_instance = Mock()
        mock_ollama_client.return_value = mock_instance
        
        # First call creates client
        result1 = get_default_client()
        # Second call should return same instance
        result2 = get_default_client()
        
        self.assertEqual(result1, result2)
        self.assertEqual(result1, mock_instance)
        # Should only create client once
        mock_ollama_client.assert_called_once_with()


class TestOllamaClientEdgeCases(unittest.TestCase):
    
    def test_client_with_empty_config(self):
        """Test client initialization with empty config"""
        client = OllamaClient({})
        
        # Should use defaults
        self.assertEqual(client.base_url, "http://localhost:11434")
        self.assertIsNotNone(client.model)
    
    @patch('src.ollama_client.requests.get')
    def test_connection_with_malformed_response(self, mock_get):
        """Test connection with malformed JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        client = OllamaClient({'model': 'qwen2.5:3b', 'ollama_host': 'localhost:11434'})
        result = client.test_connection()
        
        self.assertFalse(result)
    
    def test_client_string_representation(self):
        """Test that client can be represented as string without errors"""
        client = OllamaClient({'model': 'test-model'})
        
        # Should not raise an exception
        str_repr = str(client)
        self.assertIsInstance(str_repr, str)


if __name__ == '__main__':
    unittest.main()
