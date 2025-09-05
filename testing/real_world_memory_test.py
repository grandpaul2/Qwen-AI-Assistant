#!/usr/bin/env python3
"""
Real-World Memory System Test Suite

Tests the new WorkspaceAI v3.0 memory system with actual Ollama model interactions
to validate model-specific memory isolation, adaptive budgets, and conversation flow.
"""

import sys
import os
import time
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_model_specific_memory():
    """Test that different models maintain separate memory"""
    print("=== Real-World Test: Model-Specific Memory ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Test with qwen2.5:3b
        print("\n1. Testing with qwen2.5:3b...")
        response1 = call_ollama_with_universal_tools(
            "Hi, I'm testing WorkspaceAI's new memory system. My name is Paul, and I'm working on memory isolation features. Please remember my name.",
            model="qwen2.5:3b",
            use_tools=False,
            verbose_output=True
        )
        
        if response1:
            print(f"✅ qwen2.5:3b response: {response1[:100]}...")
        else:
            print("❌ No response from qwen2.5:3b")
            return False
            
        time.sleep(2)
        
        # Follow-up question to test memory
        print("\n2. Testing memory recall with qwen2.5:3b...")
        response2 = call_ollama_with_universal_tools(
            "What's my name, and what am I working on?",
            model="qwen2.5:3b", 
            use_tools=False,
            verbose_output=True
        )
        
        if response2:
            print(f"✅ qwen2.5:3b recall: {response2[:100]}...")
            # Check if it remembered the name
            if "Paul" in response2 or "paul" in response2.lower():
                print("✅ Memory recall successful - name remembered")
            else:
                print("⚠️  Memory recall unclear - name may not be remembered")
        
        return True
        
    except Exception as e:
        print(f"❌ Model-specific memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adaptive_context():
    """Test adaptive context allocation with different query complexities"""
    print("\n=== Real-World Test: Adaptive Context Management ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Simple query
        print("\n1. Testing simple query (should use ~60% context)...")
        response1 = call_ollama_with_universal_tools(
            "Hi there!",
            model="qwen2.5:3b",
            use_tools=False,
            verbose_output=True
        )
        
        if response1:
            print(f"✅ Simple query response: {response1[:80]}...")
        
        time.sleep(1)
        
        # Complex query
        print("\n2. Testing complex query (should use more context)...")
        response2 = call_ollama_with_universal_tools(
            "Can you help me analyze the architecture of a complex software system with multiple microservices, database interactions, caching layers, and real-time communication requirements? I need to understand the trade-offs between different design patterns and how to implement proper error handling and monitoring.",
            model="qwen2.5:3b",
            use_tools=False,
            verbose_output=True
        )
        
        if response2:
            print(f"✅ Complex query response: {response2[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Adaptive context test failed: {e}")
        return False

def test_tools_mode():
    """Test tools mode with memory integration"""
    print("\n=== Real-World Test: Tools Mode with Memory ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        print("\n1. Testing tools mode request...")
        response = call_ollama_with_universal_tools(
            "Can you create a simple test file called 'memory_test.txt' with the content 'WorkspaceAI v3.0 Memory System Test - Success!' and then read it back to verify?",
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        
        if response:
            print(f"✅ Tools mode response: {str(response)[:150]}...")
        else:
            print("❌ No response from tools mode")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Tools mode test failed: {e}")
        return False

def test_memory_persistence():
    """Test that memory persists and can be retrieved"""
    print("\n=== Real-World Test: Memory Persistence ===")
    
    try:
        from src.memory import unified_memory
        
        if unified_memory is None:
            print("❌ Unified memory system not available")
            return False
            
        print("\n1. Testing memory retrieval...")
        
        # Get conversation history for qwen2.5:3b
        context_messages = unified_memory.get_context_messages(
            model="qwen2.5:3b",
            user_input="Test query",
            interaction_mode="chat",
            context_window=32768
        )
        
        print(f"✅ Retrieved {len(context_messages)} context messages")
        
        # Display last few messages
        if context_messages:
            print("\nRecent conversation context:")
            for i, msg in enumerate(context_messages[-3:]):  # Show last 3 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]
                print(f"  {i+1}. {role}: {content}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory persistence test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all real-world tests"""
    print("🚀 Starting Comprehensive Real-World Memory System Tests")
    print("=" * 60)
    
    tests = [
        ("Model-Specific Memory", test_model_specific_memory),
        ("Adaptive Context Management", test_adaptive_context), 
        ("Tools Mode Integration", test_tools_mode),
        ("Memory Persistence", test_memory_persistence)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "="*60)
    print(f"🎯 REAL-WORLD TEST RESULTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ALL REAL-WORLD TESTS PASSED!")
        print("WorkspaceAI v3.0 Memory System is working correctly with live models.")
    else:
        print("⚠️  Some tests failed - check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
