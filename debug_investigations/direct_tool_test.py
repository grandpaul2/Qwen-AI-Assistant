#!/usr/bin/env python3
"""
Direct Tool Testing - Test tool functionality directly through the interface

This bypasses the subprocess approach and tests the tools directly
through the same code path users take.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_tool_call():
    """Test tool calling directly through the app interface"""
    print("=== DIRECT TOOL CALL TEST ===")
    
    try:
        # Import the same function the interactive app uses
        from src.ollama_universal_interface import call_ollama_with_tools
        
        print("Testing file creation through user interface path...")
        
        # This is exactly what happens when user types "t: create a file..."
        response = call_ollama_with_tools(
            "create a file called direct_test.txt with content 'Hello from direct test'",
            model="qwen2.5:3b",
            use_tools=True
        )
        
        print(f"Response received: {bool(response)}")
        if response:
            print(f"Response type: {type(response)}")
            if hasattr(response, 'get'):
                print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        # Check if file was created
        workspace_path = os.path.join("WorkspaceAI", "workspace", "direct_test.txt")
        if os.path.exists(workspace_path):
            print("✅ SUCCESS: File was created!")
            with open(workspace_path, 'r') as f:
                content = f.read()
                print(f"   Content: {content}")
            return True
        else:
            print("❌ FAILURE: File was not created")
            print(f"   Expected at: {workspace_path}")
            # Check if it was created somewhere else
            if os.path.exists("direct_test.txt"):
                print(f"   Found in current directory instead")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_detection():
    """Test if the system detects tool requests properly"""
    print("\n=== TOOL DETECTION TEST ===")
    
    try:
        from src.app import needs_tools
        
        test_cases = [
            ("create a file", True),
            ("make a new file called test.txt", True), 
            ("what's 2+2?", False),
            ("hello how are you?", False),
            ("list the files", True),
            ("write some content to a file", True)
        ]
        
        passed = 0
        for prompt, expected in test_cases:
            result = needs_tools(prompt)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{prompt}' -> {result} (expected {expected})")
            if result == expected:
                passed += 1
                
        print(f"Tool detection: {passed}/{len(test_cases)} correct")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ ERROR in tool detection test: {e}")
        return False

def test_verbose_output():
    """Test if verbose output is working"""
    print("\n=== VERBOSE OUTPUT TEST ===")
    
    try:
        from src.config import load_config, save_config
        
        # Enable verbose output
        config = load_config()
        original_verbose = config.get('verbose_output', False)
        config['verbose_output'] = True
        save_config(config)
        
        print("Enabled verbose output, testing tool call...")
        
        from src.ollama_universal_interface import call_ollama_with_tools
        
        # Capture stdout to see verbose output
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            response = call_ollama_with_tools(
                "calculate 15 * 23",
                model="qwen2.5:3b", 
                use_tools=True
            )
        
        output = f.getvalue()
        print(f"Captured output: {output}")
        
        # Restore config
        config['verbose_output'] = original_verbose
        save_config(config)
        
        # Check if verbose messages appeared
        if "🔧" in output or "tool" in output.lower():
            print("✅ SUCCESS: Verbose output is working")
            return True
        else:
            print("❌ FAILURE: No verbose output detected")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_direct_tests():
    """Run direct tool tests"""
    print("🔬 DIRECT TOOL TESTING")
    print("Testing tools through the exact same code path users take")
    print("=" * 60)
    
    tests = [
        ("Tool Detection", test_tool_detection),
        ("Verbose Output", test_verbose_output), 
        ("Direct Tool Call", test_direct_tool_call)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
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
    
    print("\n" + "="*60)
    print(f"🎯 DIRECT TOOL TEST RESULTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100) if (passed+failed) > 0 else 0:.1f}%")
    
    if failed > 0:
        print("🚨 CRITICAL: Real tool usage has issues!")
        print("   This explains why users experience problems.")
    else:
        print("🎉 Direct tool usage is working!")
    
    return failed == 0

if __name__ == "__main__":
    print("WorkspaceAI v3.0 - Direct Tool Testing")
    print("Testing the real code paths that users experience")
    print()
    
    success = run_direct_tests()
    sys.exit(0 if success else 1)
