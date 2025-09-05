#!/usr/bin/env python3
"""
Real User Experience Test - Tests the EXACT path users take

This test simulates exactly what happens when a user types commands
in the interactive interface, not bypassing any code paths.
"""

import sys
import os
import subprocess
import time
import tempfile
import threading
from io import StringIO

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_interactive_experience():
    """Test the exact user experience through the interactive interface"""
    print("=== REAL USER EXPERIENCE TEST ===")
    print("Testing the exact path users take through main.py interactive mode")
    
    # Test commands that a real user would type
    test_commands = [
        "t: create a file called real_test.txt with content 'Hello from real test'",
        "t: list the files in the current directory", 
        "t: read the real_test.txt file",
        "exit"
    ]
    
    # Create a temporary input file
    input_text = "\n".join(test_commands)
    
    try:
        # Run the actual main.py with our input
        print("Starting main.py with real user commands...")
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Send our commands and get output
        stdout, stderr = process.communicate(input=input_text, timeout=60)
        
        print("=== STDOUT ===")
        print(stdout)
        
        if stderr:
            print("=== STDERR ===") 
            print(stderr)
            
        # Check if the file was actually created
        test_file_path = os.path.join("WorkspaceAI", "workspace", "real_test.txt")
        if os.path.exists(test_file_path):
            print("✅ SUCCESS: File was actually created!")
            with open(test_file_path, 'r') as f:
                content = f.read()
                print(f"   File content: {content}")
            return True
        else:
            print("❌ FAILURE: File was not created")
            print(f"   Expected file at: {test_file_path}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: Test took too long")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_memory_between_commands():
    """Test if memory works between commands in interactive mode"""
    print("\n=== MEMORY PERSISTENCE TEST ===")
    
    test_commands = [
        "Hello, my name is TestUser and I'm testing memory",
        "t: create a file called memory_test.txt with my name in it", 
        "What was my name that I told you?",
        "exit"
    ]
    
    input_text = "\n".join(test_commands)
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        stdout, stderr = process.communicate(input=input_text, timeout=60)
        
        print("=== MEMORY TEST OUTPUT ===")
        print(stdout[-1000:])  # Last 1000 chars
        
        # Check if it remembered the name
        if "TestUser" in stdout:
            print("✅ SUCCESS: Model remembered information across commands")
            return True
        else:
            print("❌ FAILURE: Model did not remember information")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def run_real_user_tests():
    """Run all real user experience tests"""
    print("🔬 REAL USER EXPERIENCE TESTING")
    print("Testing the ACTUAL user path, not test shortcuts")
    print("=" * 60)
    
    tests = [
        ("Interactive Tool Usage", test_real_interactive_experience),
        ("Memory Between Commands", test_memory_between_commands)
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
    
    print("\n" + "="*60)
    print(f"🎯 REAL USER EXPERIENCE TEST RESULTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100) if (passed+failed) > 0 else 0:.1f}%")
    
    if failed > 0:
        print("🚨 CRITICAL: The user experience has serious issues!")
        print("   Our previous testing was flawed - it didn't test the real user path.")
    else:
        print("🎉 User experience is working correctly!")
    
    return failed == 0

if __name__ == "__main__":
    print("WorkspaceAI v3.0 - REAL User Experience Testing")
    print("This tests what users actually experience, not test shortcuts")
    print()
    
    success = run_real_user_tests()
    sys.exit(0 if success else 1)
