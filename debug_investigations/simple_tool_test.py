#!/usr/bin/env python3
"""
Simple Tool Test - Direct simple test with fresh context
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simple_tool_test():
    """Simple test with minimal context"""
    print("=== SIMPLE TOOL TEST ===")
    
    try:
        from src.ollama_client import OllamaClient
        from src.enhanced_tool_instructions import get_context_aware_tool_schemas
        
        client = OllamaClient()
        client.model = "qwen2.5:3b"
        
        tools = get_context_aware_tool_schemas()
        
        # Very simple, direct message
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with file operation tools. When the user asks you to create a file, use the file_operations tool with action='create'."
            },
            {
                "role": "user", 
                "content": "Create a file named simple_test.txt with the content 'This is a simple test'"
            }
        ]
        
        print("Making simple request...")
        response = client.chat_completion(messages, tools)
        
        if response:
            print("=== RESPONSE ===")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
            if "message" in response and "tool_calls" in response["message"]:
                print("✅ SUCCESS: Tool calls found!")
                return True
            else:
                print("❌ FAILURE: No tool calls")
                return False
        else:
            print("❌ No response")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simple_tool_test()
