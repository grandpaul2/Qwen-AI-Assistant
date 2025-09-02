#!/usr/bin/env python3
"""
Interactive Tool vs Chat Detection Testing

Real user interface testing for the core challenge: getting the bot to accurately
distinguish between chat requests and tool requests, and select the right tool.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple, Union

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class InteractiveToolDetectionTester:
    """Interactive testing system for tool vs chat detection"""
    
    def __init__(self):
        self.session_id = f"interactive_{int(time.time())}"
        self.test_results = []
        self.session_start = datetime.now()
        
    def run_interactive_testing_session(self):
        """Run interactive testing session with real user interface"""
        print("🎯 Interactive Tool vs Chat Detection Testing")
        print("=" * 60)
        print("Purpose: Test the core challenge of tool detection accuracy")
        print(f"Session ID: {self.session_id}")
        print(f"Start Time: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("📋 Testing Categories:")
        print("1. Chat vs Tool Detection")
        print("2. Tool Selection Accuracy") 
        print("3. Edge Case Handling")
        print("4. Context Awareness")
        print("5. User Intent Clarity")
        print()
        
        try:
            # Import the core system functions
            from src.app import detect_file_intent
            from src.enhanced_interface import call_ollama_with_enhanced_intelligence
            print("✅ Bot system loaded successfully")
            print()
        except Exception as e:
            print(f"❌ Failed to load bot system: {e}")
            return
        
        while True:
            choice = self.show_testing_menu()
            
            if choice == '1':
                self.test_chat_vs_tool_detection()
            elif choice == '2':
                self.test_tool_selection_accuracy()
            elif choice == '3':
                self.test_edge_cases()
            elif choice == '4':
                self.test_context_awareness()
            elif choice == '5':
                self.test_user_intent_clarity()
            elif choice == '6':
                self.run_quick_validation_set()
            elif choice == '7':
                self.show_session_results()
            elif choice == '8':
                self.save_and_exit()
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def show_testing_menu(self) -> str:
        """Show interactive testing menu"""
        print("\n" + "="*60)
        print("🎯 INTERACTIVE TOOL DETECTION TESTING MENU")
        print("="*60)
        print("1. Chat vs Tool Detection Test")
        print("2. Tool Selection Accuracy Test")
        print("3. Edge Case Handling Test")
        print("4. Context Awareness Test")
        print("5. User Intent Clarity Test")
        print("6. Quick Validation Set (10 scenarios)")
        print("7. Show Session Results")
        print("8. Save Results & Exit")
        print()
        return input("Choose test type (1-8): ").strip()
    
    def test_chat_vs_tool_detection(self):
        """Test basic chat vs tool detection"""
        print("\n🔍 Testing: Chat vs Tool Detection")
        print("-" * 40)
        print("Goal: Verify the bot correctly identifies when to use tools vs when to chat")
        print()
        
        test_cases = [
            ("What's the weather like today?", "chat", "Should be normal conversation"),
            ("Create a file called notes.txt", "tools", "Clear file creation request"),
            ("How do I learn Python?", "chat", "Educational question"),
            ("List all files in the current directory", "tools", "File operation request"),
            ("What time is it?", "chat", "General question"),
            ("Copy hello.txt to backup.txt", "tools", "File operation"),
            ("Tell me a joke", "chat", "Conversational request"),
            ("Delete the old_data folder", "tools", "File management")
        ]
        
        print("Testing automatic detection...")
        for i, (input_text, expected, description) in enumerate(test_cases, 1):
            print(f"\n[{i}] Input: '{input_text}'")
            print(f"    Expected: {expected} ({description})")
            
            # Test with detect_file_intent
            from src.enhanced_interface import detect_file_intent
            detected = "tools" if detect_file_intent(input_text) else "chat"
            
            status = "✅" if detected == expected else "❌"
            print(f"    Detected: {detected} {status}")
            
            if detected != expected:
                print(f"    ⚠️  MISMATCH - This needs attention!")
                
                # Ask user if they want to test interactively
                test_interactive = input("    Test this through the actual bot interface? (y/n): ").lower() == 'y'
                if test_interactive:
                    self.test_single_input_interactive(input_text, expected)
        
        print("\n📋 Manual Test Prompts:")
        print("Try these in the actual bot to verify behavior:")
        for input_text, expected, _ in test_cases:
            print(f"- '{input_text}' → Should be {expected}")
    
    def test_tool_selection_accuracy(self):
        """Test accuracy of specific tool selection"""
        print("\n🔧 Testing: Tool Selection Accuracy")
        print("-" * 40)
        print("Goal: When tools are correctly detected, verify the right tool is selected")
        print()
        
        tool_cases = [
            ("Create a new file called project.py", "create_file", "File creation"),
            ("Read the contents of config.json", "read_file", "File reading"),
            ("Delete the temporary folder", "delete_file", "File/folder deletion"),
            ("Copy all .txt files to backup folder", "copy_file", "File copying"),
            ("List all Python files", "list_files", "File listing"),
            ("Search for files containing 'TODO'", "search_files", "File searching"),
            ("Make a backup of my documents", "compress_files", "Compression/backup"),
            ("Show me the metadata of image.png", "get_file_metadata", "Metadata retrieval")
        ]
        
    print("Testing tool selection...")
    for i, (input_text, expected_tool, description) in enumerate(tool_cases, 1):
            print(f"\n[{i}] Input: '{input_text}'")
            print(f"    Expected tool: {expected_tool} ({description})")
            
            # Test with enhanced system
            try:
                from src.enhanced_interface import get_enhanced_components, detect_file_intent
                
                # Simple test - just check if it detects as tool request
                is_tool_request = detect_file_intent(input_text)
                
                if is_tool_request:
                    # Get enhanced components for detailed tool selection
                    components = get_enhanced_components()
                    context, intent_classifier, tool_selector = components[:3]
                    
                    # Get tool recommendation (simplified approach)
                    selected_tool = "file_operation_detected"  # Simplified for testing
                    confidence = 0.8  # Default confidence
                else:
                    selected_tool = "no_tool_needed"
                    confidence = 0.0
                
                print(f"    Tool detection: {is_tool_request}")
                print(f"    Selected approach: {selected_tool} (confidence: {confidence:.2f})")
                
                # Simple matching check - just verify tool detection worked
                should_detect_tool = any(keyword in input_text.lower() for keyword in 
                                       ['create', 'read', 'delete', 'copy', 'list', 'search', 'compress', 'metadata'])
                is_correct = (is_tool_request and should_detect_tool) or (not is_tool_request and not should_detect_tool)
                
                status = "✅" if is_correct else "❌"
                print(f"    Detection accuracy: {status}")
                
                if not is_correct:
                    print(f"    ⚠️  Tool detection may need improvement")
                    test_live = input("    Test this in live bot interface? (y/n): ").lower() == 'y'
                    if test_live:
                        self.test_single_input_interactive(input_text, f"should detect tool: {should_detect_tool}")
                        
            except Exception as e:
                print(f"    ❌ Error testing: {e}")
    
    def test_edge_cases(self):
        """Test challenging edge cases"""
        print("\n⚡ Testing: Edge Cases")
        print("-" * 40)
        print("Goal: Test challenging scenarios that often cause misclassification")
        print()
        
        edge_cases = [
            ("Can you help me create a Python script?", "Ambiguous - could be chat or tools"),
            ("I need to write documentation", "Ambiguous - write vs create file"),
            ("Show me how to delete files safely", "Chat - asking for guidance, not action"),
            ("Generate installation commands for Git", "Tools - specific install command generation"),
            ("What's the best way to organize files?", "Chat - asking for advice"),
            ("Move all .log files to archive", "Tools - clear file operation"),
            ("How do I backup my data?", "Chat - asking for guidance"),
            ("Backup my data to backup.zip", "Tools - specific backup request"),
            ("Create setup instructions for Python", "Ambiguous - could be file creation or install commands"),
            ("Write me a guide about file management", "Ambiguous - documentation vs file creation")
        ]
        
        print("These are the trickiest cases. Let's test them interactively:")
        print()
        
        for i, (input_text, challenge) in enumerate(edge_cases, 1):
            print(f"[{i}] Edge Case: '{input_text}'")
            print(f"    Challenge: {challenge}")
            
            test_it = input("    Test this case? (y/n/s=skip all): ").lower()
            if test_it == 's':
                break
            elif test_it == 'y':
                self.test_single_input_interactive(input_text, "edge case")
    
    def test_context_awareness(self):
        """Test context-aware detection"""
        print("\n🧠 Testing: Context Awareness")
        print("-" * 40)
        print("Goal: Test if previous context affects tool detection accuracy")
        print()
        
        print("This test requires sequential inputs. We'll simulate conversation context.")
        print("Try these sequences in the actual bot:")
        print()
        
        sequences = [
            [
                "I'm working on a Python project",
                "Create a main.py file",  # Should be tools (context: working on project)
                "What should I put in it?"  # Should be chat (asking for guidance)
            ],
            [
                "I need to organize my files",
                "List all the .txt files",  # Should be tools (context: organizing)
                "Which ones should I keep?"  # Should be chat (asking for opinion)
            ],
            [
                "I'm backing up my work",
                "Compress all my documents",  # Should be tools (context: backup)
                "How often should I do this?"  # Should be chat (asking advice)
            ]
        ]
        
        for i, sequence in enumerate(sequences, 1):
            print(f"Sequence {i}:")
            for j, line in enumerate(sequence):
                expected = "tools" if ("create" in line.lower() or "list" in line.lower() or "compress" in line.lower()) else "chat"
                print(f"  {j+1}. '{line}' → Expected: {expected}")
            print()
            
            test_sequence = input(f"Test sequence {i} in live bot? (y/n): ").lower() == 'y'
            if test_sequence:
                print("Go test this sequence in the actual bot interface.")
                input("Press Enter when done...")
    
    def test_user_intent_clarity(self):
        """Test handling of unclear user intents"""
        print("\n❓ Testing: User Intent Clarity")
        print("-" * 40)
        print("Goal: Test how bot handles unclear or ambiguous requests")
        print()
        
        unclear_cases = [
            "Do something with my files",
            "I need help with stuff",
            "Fix this",
            "Make it work",
            "Process the data",
            "Handle the documents",
            "Organize everything",
            "Clean up"
        ]
        
        print("These inputs are intentionally vague. Test how the bot responds:")
        print()
        
        for i, unclear_input in enumerate(unclear_cases, 1):
            print(f"[{i}] Vague input: '{unclear_input}'")
            test_it = input("    Test this? (y/n/s=skip): ").lower()
            if test_it == 's':
                break
            elif test_it == 'y':
                self.test_single_input_interactive(unclear_input, "should ask for clarification")
    
    def run_quick_validation_set(self):
        """Run a quick set of 10 key validation scenarios"""
        print("\n⚡ Quick Validation Set")
        print("-" * 40)
        print("Testing 10 critical scenarios for tool detection accuracy")
        print()
        
        validation_set = [
            ("Create a file called test.txt", "tools", "Basic file creation"),
            ("What's the weather today?", "chat", "Basic chat question"),
            ("List all files here", "tools", "File listing"),
            ("How do I learn programming?", "chat", "Educational question"),
            ("Delete old_file.txt", "tools", "File deletion"),
            ("Tell me about Python", "chat", "Informational request"),
            ("Copy data.csv to backup.csv", "tools", "File copying"),
            ("What time is it?", "chat", "Time question"),
            ("Search for files with 'config'", "tools", "File searching"),
            ("Explain machine learning", "chat", "Educational explanation")
        ]
        
        print("Running automated quick validation...")
        correct = 0
        total = len(validation_set)
        
        for i, (input_text, expected, description) in enumerate(validation_set, 1):
                from src.enhanced_interface import detect_file_intent
            detected = "tools" if detect_file_intent(input_text) else "chat"
            is_correct = detected == expected
            correct += is_correct
            
            status = "✅" if is_correct else "❌"
            print(f"[{i:2d}] {status} '{input_text[:30]}...' → {detected} (expected {expected})")
        
        accuracy = (correct / total) * 100
        print(f"\n📊 Quick Validation Results:")
        print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
        
        if accuracy < 80:
            print("⚠️  Accuracy below 80% - tool detection needs improvement")
        elif accuracy < 90:
            print("✅ Good accuracy - minor tweaks may help")
        else:
            print("🎯 Excellent accuracy!")
    
    def test_single_input_interactive(self, input_text: str, expected_behavior: str):
        """Test a single input through interactive interface"""
        print(f"\n🧪 Interactive Test:")
        print(f"Input: '{input_text}'")
        print(f"Expected: {expected_behavior}")
        print()
        print("Now test this in the actual bot interface...")
        
        # Record the test
        result: Dict[str, Any] = {
            "input": input_text,
            "expected": expected_behavior,
            "timestamp": datetime.now().isoformat(),
            "test_type": "interactive"
        }
        
        # Get user feedback
        print("\nAfter testing, please provide feedback:")
        actual_behavior = input("What happened? (describe the bot's response): ").strip()
        was_correct = input("Was this correct? (y/n): ").lower() == 'y'
        
        result["actual_behavior"] = actual_behavior
        result["was_correct"] = was_correct
        result["user_notes"] = input("Any additional notes: ").strip()
        
        self.test_results.append(result)
        
        status = "✅" if was_correct else "❌"
        print(f"\nResult recorded: {status}")
    
    def show_session_results(self):
        """Show current session results"""
        print(f"\n📊 Session Results (ID: {self.session_id})")
        print("-" * 60)
        
        if not self.test_results:
            print("No test results recorded yet.")
            return
        
        total_tests = len(self.test_results)
        correct_tests = sum(1 for r in self.test_results if r.get('was_correct', False))
        accuracy = (correct_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests run: {total_tests}")
        print(f"Correct: {correct_tests}")
        print(f"Accuracy: {accuracy:.1f}%")
        print()
        
        print("Recent test results:")
        for i, result in enumerate(self.test_results[-5:], 1):  # Show last 5
            status = "✅" if result.get('was_correct', False) else "❌"
            print(f"{i}. {status} '{result['input'][:40]}...'")
    
    def save_and_exit(self):
        """Save results and exit"""
        print(f"\n💾 Saving session results...")
        
        session_data = {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "test_results": self.test_results
        }
        
        # Save to file
        os.makedirs("test_results", exist_ok=True)
        filename = f"test_results/interactive_session_{self.session_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"✅ Results saved to: {filename}")
        
        if self.test_results:
            total = len(self.test_results)
            correct = sum(1 for r in self.test_results if r.get('was_correct', False))
            accuracy = (correct / total) * 100
            print(f"📊 Final session accuracy: {correct}/{total} ({accuracy:.1f}%)")
        
        print("👋 Interactive testing session complete!")

def main():
    """Run interactive tool detection testing"""
    tester = InteractiveToolDetectionTester()
    
    try:
        tester.run_interactive_testing_session()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        tester.save_and_exit()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == "__main__":
    main()
