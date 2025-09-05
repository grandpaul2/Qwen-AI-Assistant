#!/usr/bin/env python3
"""
Context Contamination Detective - Find what's breaking tool calling in user experience
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def capture_user_experience_context():
    """Capture the exact context sent in user experience vs working test"""
    print("=== CONTEXT CONTAMINATION DETECTIVE ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_tools
        from src.ollama_client import OllamaClient
        from src.enhanced_tool_instructions import (
            get_context_aware_tool_schemas, 
            build_context_aware_instruction,
            build_enhanced_tool_instruction
        )
        
        # Test 1: Capture the user experience context
        print("1. Testing user experience path (call_ollama_with_tools)...")
        
        # Monkey patch the client to capture the context
        original_chat_completion = OllamaClient.chat_completion
        captured_context = {}
        
        def capture_chat_completion(self, messages, tools=None, stream=False):
            captured_context['user_experience'] = {
                'messages': messages,
                'tools': tools,
                'message_count': len(messages) if messages else 0,
                'has_system': any(msg.get('role') == 'system' for msg in messages) if messages else False,
                'system_content': next((msg.get('content', '') for msg in messages if msg.get('role') == 'system'), '') if messages else '',
                'user_messages': [msg for msg in messages if msg.get('role') == 'user'] if messages else []
            }
            # Don't actually make the request, just capture the context
            return None
        
        OllamaClient.chat_completion = capture_chat_completion
        
        # This goes through the full user experience path
        call_ollama_with_tools(
            "create a file called user_test.txt with content 'user test'", 
            model="qwen2.5:3b",
            use_tools=True
        )
        
        # Restore original method
        OllamaClient.chat_completion = original_chat_completion
        
        print("2. Testing working direct path...")
        
        # Test 2: Capture the working direct context  
        client = OllamaClient()
        client.model = "qwen2.5:3b"
        tools = get_context_aware_tool_schemas()
        
        working_messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with file operation tools. Use the file_operations tool to create files when requested."
            },
            {
                "role": "user",
                "content": "create a file called user_test.txt with content 'user test'"
            }
        ]
        
        captured_context['working'] = {
            'messages': working_messages,
            'tools': tools,
            'message_count': len(working_messages),
            'has_system': True,
            'system_content': working_messages[0]['content'],
            'user_messages': [working_messages[1]]
        }
        
        print("3. COMPARISON ANALYSIS:")
        print("=" * 50)
        
        if 'user_experience' not in captured_context:
            print("❌ Failed to capture user experience context")
            return False
            
        ux = captured_context['user_experience']
        working = captured_context['working']
        
        print(f"Message count - UX: {ux['message_count']}, Working: {working['message_count']}")
        print(f"Has system - UX: {ux['has_system']}, Working: {working['has_system']}")
        
        print("\n=== USER EXPERIENCE SYSTEM PROMPT ===")
        print(ux['system_content'][:500] + "..." if len(ux['system_content']) > 500 else ux['system_content'])
        
        print("\n=== WORKING SYSTEM PROMPT ===")  
        print(working['system_content'])
        
        print(f"\n=== USER MESSAGES ===")
        print(f"UX user messages: {len(ux['user_messages'])}")
        for i, msg in enumerate(ux['user_messages']):
            print(f"  {i+1}: {msg.get('content', '')[:100]}...")
            
        print(f"Working user messages: {len(working['user_messages'])}")
        for i, msg in enumerate(working['user_messages']):
            print(f"  {i+1}: {msg.get('content', '')[:100]}...")
        
        # Key differences analysis
        print("\n=== CONTAMINATION ANALYSIS ===")
        
        if ux['message_count'] > working['message_count']:
            print(f"🔍 ISSUE: UX has {ux['message_count'] - working['message_count']} extra messages")
            
        if len(ux['system_content']) > len(working['system_content']) * 2:
            print(f"🔍 ISSUE: UX system prompt is {len(ux['system_content'])} chars vs {len(working['system_content'])} chars (much longer)")
            
        if len(ux['user_messages']) > 1:
            print(f"🔍 ISSUE: UX has {len(ux['user_messages'])} user messages (conversation history)")
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_prompt_impact():
    """Test if the system prompt is causing issues"""
    print("\n=== SYSTEM PROMPT IMPACT TEST ===")
    
    try:
        from src.ollama_client import OllamaClient
        from src.enhanced_tool_instructions import (
            get_context_aware_tool_schemas,
            build_enhanced_tool_instruction
        )
        
        client = OllamaClient()
        client.model = "qwen2.5:3b"
        tools = get_context_aware_tool_schemas()
        
        # Test with the complex system prompt that user experience uses
        complex_system_prompt = build_enhanced_tool_instruction()
        
        messages_complex = [
            {"role": "system", "content": complex_system_prompt},
            {"role": "user", "content": "create a file called system_test.txt with content 'system test'"}
        ]
        
        print("Testing with complex system prompt...")
        response = client.chat_completion(messages_complex, tools)
        
        if response and "message" in response and "tool_calls" in response["message"]:
            print("✅ Complex system prompt: WORKS")
            return True
        else:
            print("❌ Complex system prompt: BROKEN")
            if response:
                content = response.get("message", {}).get("content", "")
                print(f"Response: {content[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Investigating Context Contamination")
    print("=" * 40)
    
    capture_user_experience_context()
    test_system_prompt_impact()
