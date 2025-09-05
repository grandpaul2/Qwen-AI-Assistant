#!/usr/bin/env python3
"""
Session 3 Integration Test

Tests the integration of the new unified memory system with ollama_universal_interface.py
"""

import sys
import os
import tempfile
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_memory_interface_integration():
    """Test that the memory interface integration works"""
    print("=== Session 3 Integration Test ===")
    
    try:
        # Test import and initialization
        print("1. Testing imports...")
        from src.ollama_universal_interface import _get_memory_interface
        from src.memory import unified_memory
        
        if unified_memory is not None:
            print("✅ Unified memory system available")
        else:
            print("❌ Unified memory system not available")
            return False
        
        # Test memory interface selection
        print("\n2. Testing memory interface selection...")
        memory_interface, model = _get_memory_interface("test-model")
        
        if memory_interface is not None:
            print(f"✅ Got memory interface: {type(memory_interface).__name__}")
            print(f"✅ Model: {model}")
        else:
            print("❌ No memory interface returned")
            return False
        
        # Test basic memory operations
        print("\n3. Testing basic memory operations...")
        
        # Test add_message
        try:
            memory_interface.add_message("user", "Hello, test!", model=model)
            memory_interface.add_message("assistant", "Hello! How can I help you?", model=model)
            print("✅ add_message works")
        except Exception as e:
            print(f"❌ add_message failed: {e}")
            return False
        
        # Test get_context_messages
        try:
            context = memory_interface.get_context_messages(
                model=model,
                user_input="Test query",
                interaction_mode="chat",
                context_window=32768
            )
            print(f"✅ get_context_messages works: {len(context)} messages")
        except Exception as e:
            print(f"❌ get_context_messages failed: {e}")
            return False
        
        # Test save_memory_async
        try:
            memory_interface.save_memory_async()
            print("✅ save_memory_async works")
        except Exception as e:
            print(f"❌ save_memory_async failed: {e}")
            return False
        
        print("\n🎉 All Session 3 integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Session 3 integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interface_compatibility():
    """Test that the interface maintains backward compatibility"""
    print("\n=== Interface Compatibility Test ===")
    
    try:
        from src.memory import memory, unified_memory
        
        # Test that both interfaces have the same methods
        required_methods = ['add_message', 'get_context_messages', 'save_memory_async']
        
        print("Testing legacy memory interface...")
        for method in required_methods:
            if hasattr(memory, method):
                print(f"✅ Legacy memory has {method}")
            else:
                print(f"❌ Legacy memory missing {method}")
                return False
        
        if unified_memory:
            print("Testing unified memory interface...")
            for method in required_methods:
                if hasattr(unified_memory, method):
                    print(f"✅ Unified memory has {method}")
                else:
                    print(f"❌ Unified memory missing {method}")
                    return False
        
        print("✅ Interface compatibility verified")
        return True
        
    except Exception as e:
        print(f"❌ Interface compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting Session 3 Integration Tests...")
    
    test1_result = test_memory_interface_integration()
    test2_result = test_interface_compatibility()
    
    if test1_result and test2_result:
        print("\n🚀 ALL SESSION 3 TESTS PASSED!")
        print("Memory system integration is ready for production use.")
        sys.exit(0)
    else:
        print("\n❌ Some Session 3 tests failed")
        sys.exit(1)
