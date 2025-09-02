#!/usr/bin/env python3
"""
Quick Tool Detection Testing Script

Easy way to test tool vs chat detection accuracy.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def quick_test():
    """Run quick tool detection test"""
    print("🎯 Quick Tool vs Chat Detection Test")
    print("=" * 50)
    
    # Import the function
    try:
        from src.app import detect_file_intent
        print("✅ Bot system loaded")
    except Exception as e:
        print(f"❌ Failed to load bot system: {e}")
        return
    
    # Quick test cases
    test_cases = [
        ("Create a file called test.txt", True, "File creation"),
        ("What's the weather today?", False, "Weather question"),
        ("List all files here", True, "File listing"),
        ("How do I learn Python?", False, "Learning question"),
        ("Delete old_file.txt", True, "File deletion"),
        ("Tell me a joke", False, "Entertainment"),
        ("Copy data.csv to backup.csv", True, "File copying"),
        ("What time is it?", False, "Time question"),
        ("Search for config files", True, "File searching"),
        ("Explain machine learning", False, "Educational")
    ]
    
    print(f"\nTesting {len(test_cases)} scenarios...")
    print("-" * 50)
    
    correct = 0
    total = len(test_cases)
    
    for i, (input_text, expected_tools, description) in enumerate(test_cases, 1):
        detected_tools = detect_file_intent(input_text)
        is_correct = detected_tools == expected_tools
        correct += is_correct
        
        expected_str = "tools" if expected_tools else "chat"
        detected_str = "tools" if detected_tools else "chat"
        status = "✅" if is_correct else "❌"
        
        print(f"[{i:2d}] {status} '{input_text[:35]}...'")
        print(f"     Expected: {expected_str} | Detected: {detected_str} | {description}")
        
        if not is_correct:
            print(f"     ⚠️  MISMATCH - needs attention!")
        print()
    
    accuracy = (correct / total) * 100
    print("=" * 50)
    print(f"📊 RESULTS: {correct}/{total} correct ({accuracy:.1f}%)")
    
    if accuracy >= 90:
        print("🎯 Excellent! Tool detection is working very well.")
    elif accuracy >= 80:
        print("✅ Good accuracy. Minor improvements possible.")
    elif accuracy >= 70:
        print("⚠️  Moderate accuracy. Some improvements needed.")
    else:
        print("❌ Low accuracy. Tool detection needs significant work.")
    
    print("\n🔧 For interactive testing, run:")
    print("python tests/interactive_tool_detection.py")

def main():
    quick_test()

if __name__ == "__main__":
    main()
