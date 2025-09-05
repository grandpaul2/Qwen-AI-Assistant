#!/usr/bin/env python3
"""
Test script to extract model context window and other metadata from Ollama API
"""

import json
import requests
import sys

def get_model_info(model_name):
    """Get detailed model information from Ollama API"""
    try:
        response = requests.post(
            "http://localhost:11434/api/show",
            json={"name": model_name},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            context_length = data.get("model_info", {}).get("qwen2.context_length")
            parameter_size = data.get("details", {}).get("parameter_size")
            quantization = data.get("details", {}).get("quantization_level")
            
            print(f"Model: {model_name}")
            print(f"Context Length: {context_length} tokens")
            print(f"Parameter Size: {parameter_size}")
            print(f"Quantization: {quantization}")
            print("-" * 40)
            
            return {
                "model": model_name,
                "context_length": context_length,
                "parameter_size": parameter_size,
                "quantization": quantization
            }
        else:
            print(f"Error getting info for {model_name}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_available_models():
    """Get list of available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        else:
            print(f"Error getting models: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("=== Ollama Model Information ===")
    
    # Get all available models
    models = get_available_models()
    print(f"Available models: {models}")
    print()
    
    # Get detailed info for each model
    model_info = {}
    for model in models:
        info = get_model_info(model)
        if info:
            model_info[model] = info
    
    # Summary
    print("\n=== Summary ===")
    for model, info in model_info.items():
        print(f"{model}: {info['context_length']} tokens, {info['parameter_size']}")
