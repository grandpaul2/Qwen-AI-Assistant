#!/usr/bin/env python3
"""
Full End-to-End Tool Test - Test the complete pipeline
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def full_end_to_end_test():
    """Test the complete tool pipeline from call to execution"""
    print("=== FULL END-TO-END TOOL TEST ===")
    
    try:
        from src.ollama_client import OllamaClient
        from src.enhanced_tool_instructions import get_context_aware_tool_schemas
        from src.universal_tool_handler import handle_any_tool_call
        
        client = OllamaClient()
        client.model = "qwen2.5:3b"
        
        tools = get_context_aware_tool_schemas()
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with file operation tools. Use the file_operations tool to create files when requested."
            },
            {
                "role": "user", 
                "content": "Create a file named end_to_end_test.txt with the content 'End-to-end test successful!'"
            }
        ]
        
        print("1. Making request to model...")
        response = client.chat_completion(messages, tools)
        
        if not response or "message" not in response:
            print("❌ No response from model")
            return False
            
        if "tool_calls" not in response["message"]:
            print("❌ No tool calls in response")
            print(f"Response: {response['message'].get('content', '')}")
            return False
            
        tool_calls = response["message"]["tool_calls"]
        print(f"✅ Model made {len(tool_calls)} tool call(s)")
        
        for i, tool_call in enumerate(tool_calls):
            print(f"\n2. Processing tool call {i+1}...")
            print(f"Function: {tool_call['function']['name']}")
            print(f"Arguments: {tool_call['function']['arguments']}")
            
            print("3. Executing tool call...")
            result = handle_any_tool_call(tool_call)
            print(f"Tool result: {result}")
            
        print("\n4. Checking if file was created...")
        test_file = os.path.join("WorkspaceAI", "workspace", "end_to_end_test.txt")
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"✅ SUCCESS: File created with content: '{content}'")
            return True
        else:
            print(f"❌ FAILURE: File not found at {test_file}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    full_end_to_end_test()
