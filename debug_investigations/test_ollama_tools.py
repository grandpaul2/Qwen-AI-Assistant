#!/usr/bin/env python3
"""
Test Ollama Tool Calling Directly - Test if qwen2.5:3b supports tools at the API level
"""

import requests
import json

def test_ollama_tools_directly():
    """Test tool calling directly with Ollama API"""
    print("=== TESTING OLLAMA TOOL CALLING DIRECTLY ===")
    
    url = "http://localhost:11434/api/chat"
    
    # Simple tool schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a new file with specified content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to create"
                        },
                        "content": {
                            "type": "string", 
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["filename", "content"]
                }
            }
        }
    ]
    
    payload = {
        "model": "qwen2.5:3b",
        "messages": [
            {
                "role": "user", 
                "content": "Please create a file called 'hello.txt' with the content 'Hello World'"
            }
        ],
        "tools": tools,
        "stream": False
    }
    
    try:
        print("Sending request to Ollama...")
        print(f"Tools: {len(tools)} tool(s)")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("=== RESPONSE ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check for tool calls
            if "message" in result and "tool_calls" in result["message"]:
                tool_calls = result["message"]["tool_calls"]
                print(f"\n✅ SUCCESS: Found {len(tool_calls)} tool call(s)")
                return True
            else:
                print(f"\n❌ NO TOOL CALLS: Model gave text response instead")
                return False
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_without_tools():
    """Test the same request without tools for comparison"""
    print("\n=== TESTING WITHOUT TOOLS FOR COMPARISON ===")
    
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "qwen2.5:3b",
        "messages": [
            {
                "role": "user",
                "content": "Please create a file called 'hello.txt' with the content 'Hello World'"
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            print(f"Response without tools: {content[:200]}...")
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing qwen2.5:3b Tool Calling Support")
    print("=" * 50)
    
    # Test with tools
    with_tools = test_ollama_tools_directly()
    
    # Test without tools  
    without_tools = test_without_tools()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"With tools: {'✅ Works' if with_tools else '❌ Failed'}")
    print(f"Without tools: {'✅ Works' if without_tools else '❌ Failed'}")
    
    if not with_tools and without_tools:
        print("\n🔍 CONCLUSION: qwen2.5:3b doesn't support tool calling")
        print("   The model responds normally but ignores tool schemas")
    elif with_tools:
        print("\n🎉 CONCLUSION: qwen2.5:3b supports tool calling!")
        print("   The issue must be in our implementation")
    else:
        print("\n❓ CONCLUSION: Unable to determine - both tests failed")
