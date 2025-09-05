"""
Model capability detection for dynamic memory management
"""

import requests
import json
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class ModelCapabilityDetector:
    """Detects and caches model capabilities from Ollama API"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.base_url = ollama_base_url
        self._model_cache = {}
    
    def get_model_capabilities(self, model_name: str) -> Optional[Dict]:
        """
        Get model capabilities including context window size
        
        Returns:
            Dict with keys: context_length, parameter_size, quantization, family
        """
        if model_name in self._model_cache:
            return self._model_cache[model_name]
        
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model_name},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                model_info = data.get("model_info", {})
                details = data.get("details", {})
                
                # Extract capabilities
                capabilities = {
                    "context_length": model_info.get("qwen2.context_length", 4096),  # Default fallback
                    "parameter_size": details.get("parameter_size", "unknown"),
                    "quantization": details.get("quantization_level", "unknown"),
                    "family": details.get("family", "unknown"),
                    "format": details.get("format", "unknown")
                }
                
                # Cache the result
                self._model_cache[model_name] = capabilities
                logger.info(f"Detected {model_name}: {capabilities['context_length']} tokens context")
                return capabilities
            
            else:
                logger.warning(f"Failed to get model info for {model_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting model capabilities for {model_name}: {e}")
            return None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            else:
                logger.warning(f"Failed to get model list: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    def get_context_window_size(self, model_name: str) -> int:
        """Get context window size for a specific model"""
        capabilities = self.get_model_capabilities(model_name)
        if capabilities:
            return capabilities["context_length"]
        
        # Fallback defaults based on common model names
        if "3b" in model_name.lower():
            return 4096  # Conservative default for smaller models
        elif "7b" in model_name.lower():
            return 8192  # Conservative default for 7B models
        else:
            return 2048  # Very conservative default
    
    def suggest_memory_budget(self, model_name: str, operation_type: str = "tools") -> Dict[str, int]:
        """
        Suggest memory budget based on model capabilities and operation type
        
        Args:
            model_name: Name of the model
            operation_type: "tools" or "chat"
            
        Returns:
            Dict with suggested token budgets for different components
        """
        context_window = self.get_context_window_size(model_name)
        
        if operation_type == "tools":
            # Tools mode needs more tokens for system prompt and tool definitions
            system_budget = min(1000, context_window * 0.1)  # 10% or 1000 tokens max
            tool_budget = min(2000, context_window * 0.15)   # 15% or 2000 tokens max
            memory_budget = context_window * 0.6             # 60% for conversation history
            response_budget = context_window * 0.15          # 15% for response generation
        else:
            # Chat mode can allocate more to conversation history
            system_budget = min(200, context_window * 0.05)  # 5% or 200 tokens max
            tool_budget = 0                                  # No tools in chat mode
            memory_budget = context_window * 0.8             # 80% for conversation history
            response_budget = context_window * 0.15          # 15% for response generation
        
        return {
            "context_window": context_window,
            "system_prompt": int(system_budget),
            "tool_definitions": int(tool_budget),
            "conversation_memory": int(memory_budget),
            "response_generation": int(response_budget),
            "safety_margin": int(context_window * 0.05)  # 5% safety margin
        }
    
    def clear_cache(self):
        """Clear the model capability cache"""
        self._model_cache.clear()


# Global instance for easy access
_detector = None

def get_model_detector() -> ModelCapabilityDetector:
    """Get global model capability detector instance"""
    global _detector
    if _detector is None:
        _detector = ModelCapabilityDetector()
    return _detector


# Convenience functions
def get_context_window_size(model_name: str) -> int:
    """Get context window size for a model"""
    return get_model_detector().get_context_window_size(model_name)

def get_memory_budget(model_name: str, operation_type: str = "tools") -> Dict[str, int]:
    """Get suggested memory budget for a model and operation type"""
    return get_model_detector().suggest_memory_budget(model_name, operation_type)

def get_model_capabilities(model_name: str) -> Optional[Dict]:
    """Get full model capabilities"""
    return get_model_detector().get_model_capabilities(model_name)


if __name__ == "__main__":
    # Test the detector
    detector = ModelCapabilityDetector()
    
    models = detector.get_available_models()
    print(f"Available models: {models}")
    
    for model in models:
        print(f"\n=== {model} ===")
        capabilities = detector.get_model_capabilities(model)
        if capabilities:
            print(f"Context Length: {capabilities['context_length']} tokens")
            print(f"Parameter Size: {capabilities['parameter_size']}")
            print(f"Family: {capabilities['family']}")
            
            # Test budget suggestions
            tools_budget = detector.suggest_memory_budget(model, "tools")
            chat_budget = detector.suggest_memory_budget(model, "chat")
            
            print(f"\nTools mode budget:")
            for key, value in tools_budget.items():
                print(f"  {key}: {value} tokens")
                
            print(f"\nChat mode budget:")
            for key, value in chat_budget.items():
                print(f"  {key}: {value} tokens")
