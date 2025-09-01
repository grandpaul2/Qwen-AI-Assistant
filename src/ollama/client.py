"""
Core Ollama API client for WorkspaceAI

Handles basic API communication, connection testing, and request/response cycles.
"""

import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any
import threading

from ..config import APP_CONFIG, CONSTANTS, load_config

logger = logging.getLogger(__name__)


class OllamaClient:
    """Core Ollama API client with connection management and retry logic"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Ollama client with configuration"""
        if config is None:
            config = load_config()
        
        self.config = config or {}
        self.model = self.config.get('model', CONSTANTS['MODEL'])
        self.base_url = f"http://{self.config.get('ollama_host', 'localhost:11434')}"
        self.timeout = CONSTANTS['API_TIMEOUT']
        self.max_retries = CONSTANTS['API_MAX_RETRIES']
        
    def test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                if self.model in model_names:
                    print(f"✅ Connected to Ollama - {self.model} is available")
                    logger.info(f"Ollama connection successful, model {self.model} available")
                    return True
                else:
                    available = ", ".join(model_names) if model_names else "none"
                    print(f"⚠️ Connected to Ollama but {self.model} not found")
                    print(f"Available models: {available}")
                    print(f"Run: ollama pull {self.model}")
                    logger.warning(f"Model {self.model} not available. Available: {available}")
                    return False
            else:
                print(f"❌ Ollama responded with status {response.status_code}")
                logger.error(f"Ollama connection failed with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama")
            print("Make sure Ollama is running: ollama serve")
            logger.error("Cannot connect to Ollama - connection refused")
            return False
        except requests.exceptions.Timeout:
            print("❌ Ollama connection timeout")
            logger.error("Ollama connection timeout")
            return False
        except Exception as e:
            print(f"❌ Ollama connection error: {e}")
            logger.error(f"Unexpected Ollama connection error: {e}")
            return False
    
    def make_request(self, endpoint: str, data: Dict, retry_count: int = 0) -> Optional[requests.Response]:
        """Make HTTP request to Ollama with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self.make_request(endpoint, data, retry_count + 1)
            else:
                logger.error("Request failed after maximum retries due to timeout")
                return None
                
        except requests.exceptions.ConnectionError:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count
                logger.warning(f"Connection error, retrying in {wait_time}s (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self.make_request(endpoint, data, retry_count + 1)
            else:
                logger.error("Request failed after maximum retries due to connection error")
                return None
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error in request: {e}")
            return None
    
    def chat_completion(self, messages: List[Dict], tools: Optional[List[Dict]] = None, stream: bool = False) -> Optional[Dict]:
        """Perform chat completion with optional tools"""
        data = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        if tools:
            data["tools"] = tools
            
        response = self.make_request("/api/chat", data)
        
        if response and response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return None
        
        return None
    
    def simple_chat(self, prompt: str) -> Optional[str]:
        """Simple chat without tools or memory"""
        messages = [{"role": "user", "content": prompt}]
        result = self.chat_completion(messages)
        
        if result and "message" in result:
            return result["message"].get("content", "")
        
        return None


# Global client instance for backward compatibility
_default_client = None

def get_default_client() -> OllamaClient:
    """Get or create the default Ollama client"""
    global _default_client
    if _default_client is None:
        _default_client = OllamaClient()
    return _default_client
