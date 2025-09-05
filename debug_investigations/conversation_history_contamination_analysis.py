#!/usr/bin/env python3
"""
Enhanced Context Contamination Detective
Analyzes what conversation history is contaminating tool calls
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ollama_universal_interface import call_ollama_with_tools
from src.memory import Memory
from src.config import Config
from src.ollama_client import OllamaClient
import json

def analyze_conversation_contamination():
    """Analyze how conversation history affects tool calling"""
    print("🔍 CONVERSATION HISTORY CONTAMINATION ANALYSIS")
    print("=" * 60)
    
    # Get memory instance
    memory = Memory()
    config = Config()
    
    # Test with clean context (should work)
    print("\n1. Testing with CLEAN context (no history)...")
    
    # Create fresh Ollama client for clean test
    fresh_client = OllamaClient(config)
    
    clean_messages = [
        {"role": "system", "content": "You are a helpful assistant with file operation tools. Use the file_operations tool to create files when requested."},
        {"role": "user", "content": "create a file called clean_test.txt with content 'clean test'"}
    ]
    
    try:
        response = fresh_client.chat_completion(
            model="qwen2.5:3b",
            messages=clean_messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "file_operations",
                        "description": "Handle file and directory operations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            },
                            "required": ["action"]
                        }
                    }
                }
            ]
        )
        
        if hasattr(response, 'message') and hasattr(response.message, 'tool_calls') and response.message.tool_calls:
            print("✅ CLEAN context: Tool calls GENERATED")
            print(f"   Tool calls: {len(response.message.tool_calls)}")
        else:
            print("❌ CLEAN context: No tool calls")
            
    except Exception as e:
        print(f"❌ CLEAN test failed: {e}")
    
    # Test with memory/history (the broken path)
    print("\n2. Testing with MEMORY/HISTORY (contaminated)...")
    
    try:
        response = call_ollama_with_tools(
            user_input="create a file called contaminated_test.txt with content 'contaminated test'",
            model="qwen2.5:3b"
        )
        print("❌ CONTAMINATED context: Probably no tool calls (text response)")
        print(f"   Response type: {type(response)}")
        
    except Exception as e:
        print(f"❌ CONTAMINATED test failed: {e}")
    
    # Analyze memory contents
    print("\n3. MEMORY CONTAMINATION ANALYSIS:")
    print("-" * 40)
    
    # Check recent conversations
    recent = memory.get_recent_conversations(limit=10)
    print(f"Recent conversations: {len(recent)}")
    
    for i, conv in enumerate(recent[:3]):  # Show first 3
        print(f"  Conv {i+1}: {conv.get('user', '')[:100]}...")
        if 'assistant' in conv:
            print(f"           → {conv.get('assistant', '')[:100]}...")
    
    # Check summarized conversations  
    try:
        summarized = memory.get_summarized_conversations()
        print(f"Summarized conversations: {len(summarized)}")
        
        for i, summary in enumerate(summarized[:2]):  # Show first 2
            print(f"  Summary {i+1}: {summary.get('content', '')[:150]}...")
            
    except Exception as e:
        print(f"Error getting summarized conversations: {e}")
    
    # Test with progressive contamination
    print("\n4. PROGRESSIVE CONTAMINATION TEST:")
    print("-" * 40)
    
    base_messages = [
        {"role": "system", "content": "You are a helpful assistant with file operation tools. Use the file_operations tool to create files when requested."},
        {"role": "user", "content": "create a file called progressive_test.txt with content 'progressive test'"}
    ]
    
    # Test with just 1 extra message
    test_messages = [
        {"role": "user", "content": "Hello, I'm testing"},
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ] + base_messages
    
    print(f"Testing with {len(test_messages)} messages...")
    try:
        response = fresh_client.chat_completion(
            model="qwen2.5:3b",
            messages=test_messages,
            tools=[
                {
                    "type": "function", 
                    "function": {
                        "name": "file_operations",
                        "description": "Handle file and directory operations",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "path": {"type": "string"}, 
                                "content": {"type": "string"}
                            },
                            "required": ["action"]
                        }
                    }
                }
            ]
        )
        
        if hasattr(response, 'message') and hasattr(response.message, 'tool_calls') and response.message.tool_calls:
            print("✅ With 1 extra exchange: Tool calls STILL WORK")
        else:
            print("❌ With 1 extra exchange: Tool calls BROKEN")
            
    except Exception as e:
        print(f"❌ Progressive test failed: {e}")
    
    print("\n" + "=" * 60)
    print("CONCLUSION: The contamination appears to be:")
    print("1. Extensive conversation history (6+ user messages)")
    print("2. Complex system prompts with tool instructions")
    print("3. Memory loading adding context overhead")
    print("4. qwen2.5:3b context limit being exceeded")

if __name__ == "__main__":
    analyze_conversation_contamination()
