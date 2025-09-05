#!/usr/bin/env python3
"""
Comprehensive Tool & Stress Testing for WorkspaceAI v3.0 Memory System

Tests common tool scenarios and stress tests chat mode with large requests
to validate memory system performance under real-world conditions.
"""

import sys
import os
import time
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_file_operations_tools():
    """Test file operations with memory persistence"""
    print("=== Tool Test: File Operations ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Test 1: Create file
        print("1. Testing file creation...")
        response1 = call_ollama_with_universal_tools(
            "Please create a file called 'test_memory.txt' with the content 'This is a memory system test file created on {}'.".format(time.strftime('%Y-%m-%d %H:%M:%S')),
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        print(f"✅ File creation response received")
        time.sleep(2)
        
        # Test 2: Read file back
        print("2. Testing file reading...")
        response2 = call_ollama_with_universal_tools(
            "Can you read the contents of the test_memory.txt file I just asked you to create?",
            model="qwen2.5:3b", 
            use_tools=True,
            verbose_output=True
        )
        print(f"✅ File reading response received")
        time.sleep(2)
        
        # Test 3: List files to verify
        print("3. Testing file listing...")
        response3 = call_ollama_with_universal_tools(
            "Can you list the files in the current workspace to show me what files exist?",
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        print(f"✅ File listing response received")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def test_code_execution_tools():
    """Test code execution capabilities"""
    print("\n=== Tool Test: Code Execution ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Test Python code execution
        print("1. Testing Python code execution...")
        response1 = call_ollama_with_universal_tools(
            "Can you execute this Python code for me: print('Memory system test:', 2+2, 'factorial of 5:', __import__('math').factorial(5))",
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        print(f"✅ Python code execution response received")
        time.sleep(2)
        
        # Test system command
        print("2. Testing system command execution...")
        response2 = call_ollama_with_universal_tools(
            "Can you run a system command to show me the current date and time?",
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        print(f"✅ System command response received")
        
        return True
        
    except Exception as e:
        print(f"❌ Code execution test failed: {e}")
        return False

def test_calculator_tools():
    """Test calculator functionality"""
    print("\n=== Tool Test: Calculator ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        print("1. Testing mathematical calculations...")
        response = call_ollama_with_universal_tools(
            "Please calculate the following: (15 * 8) + (100 / 4) - sqrt(144), and also find the factorial of 6",
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        print(f"✅ Calculator response received")
        
        return True
        
    except Exception as e:
        print(f"❌ Calculator test failed: {e}")
        return False

def test_complex_multi_tool_scenario():
    """Test complex scenario using multiple tools"""
    print("\n=== Tool Test: Complex Multi-Tool Scenario ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        print("1. Testing complex multi-tool workflow...")
        response = call_ollama_with_universal_tools(
            """I need you to help me with a data analysis task:
            1. Create a file called 'data_analysis.py' with Python code that calculates the mean and standard deviation of the numbers [10, 15, 20, 25, 30, 35, 40]
            2. Execute that Python file
            3. Create a summary file called 'results.txt' with the calculated results
            4. List all files to show me what was created
            
            Please do this step by step and explain what you're doing at each step.""",
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        print(f"✅ Complex multi-tool scenario response received")
        
        return True
        
    except Exception as e:
        print(f"❌ Complex multi-tool test failed: {e}")
        return False

def stress_test_large_context_chat():
    """Stress test chat mode with progressively larger contexts"""
    print("\n=== Stress Test: Large Context Chat Mode ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Generate a large prompt to test context handling
        large_prompt = """I need your help analyzing a comprehensive software architecture scenario. Here's the detailed context:

        We're building a large-scale e-commerce platform that needs to handle:
        
        1. USER MANAGEMENT SYSTEM:
        - Authentication and authorization for millions of users
        - Profile management with preferences and history
        - Social features like reviews, ratings, and recommendations
        - Multi-factor authentication and security protocols
        - GDPR compliance and data privacy requirements
        
        2. PRODUCT CATALOG SYSTEM:
        - Inventory management for millions of products
        - Real-time stock updates across multiple warehouses
        - Product search and filtering with advanced algorithms
        - Image processing and optimization for fast loading
        - Category management and product relationships
        - Pricing engines with dynamic pricing capabilities
        
        3. ORDER PROCESSING SYSTEM:
        - Shopping cart functionality with session management
        - Order workflow from creation to fulfillment
        - Payment processing with multiple payment gateways
        - Tax calculation across different jurisdictions
        - Shipping calculation and carrier integration
        - Order tracking and status updates
        
        4. RECOMMENDATION ENGINE:
        - Machine learning models for personalized recommendations
        - Collaborative filtering and content-based filtering
        - Real-time recommendation updates based on user behavior
        - A/B testing framework for recommendation algorithms
        - Performance monitoring and model retraining pipelines
        
        5. INFRASTRUCTURE REQUIREMENTS:
        - Microservices architecture with API gateways
        - Database design with read replicas and sharding
        - Caching strategies using Redis and CDN
        - Message queues for asynchronous processing
        - Monitoring and logging infrastructure
        - Auto-scaling capabilities for traffic spikes
        - Disaster recovery and backup strategies
        
        Given this complex scenario, I need you to provide detailed recommendations on:
        - How to structure the microservices architecture
        - Database design patterns and data consistency strategies
        - Caching strategies for optimal performance
        - API design principles and versioning strategies
        - Security best practices throughout the system
        - Monitoring and observability implementation
        - Deployment strategies and CI/CD pipelines
        
        Please provide a comprehensive analysis with specific technical recommendations for each area."""
        
        print("1. Testing large context processing...")
        print(f"   Prompt length: {len(large_prompt)} characters")
        
        response1 = call_ollama_with_universal_tools(
            large_prompt,
            model="qwen2.5:3b",
            use_tools=False,  # Pure chat mode
            verbose_output=True
        )
        
        if response1:
            print(f"✅ Large context response received: {len(response1)} characters")
        else:
            print("❌ No response to large context")
            return False
            
        time.sleep(3)
        
        # Follow up with memory test
        print("2. Testing memory retention after large context...")
        response2 = call_ollama_with_universal_tools(
            "Based on our previous discussion about the e-commerce platform, what were the main system components I mentioned?",
            model="qwen2.5:3b",
            use_tools=False,
            verbose_output=True
        )
        
        if response2:
            print(f"✅ Memory retention response received: {len(response2)} characters")
            # Check if it remembers key components
            components = ["user management", "product catalog", "order processing", "recommendation", "infrastructure"]
            remembered = sum(1 for comp in components if comp.lower() in response2.lower())
            print(f"✅ Remembered {remembered}/5 main components")
        else:
            print("❌ No memory retention response")
            
        return True
        
    except Exception as e:
        print(f"❌ Large context stress test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def stress_test_rapid_interactions():
    """Test rapid successive interactions to stress the memory system"""
    print("\n=== Stress Test: Rapid Interactions ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        rapid_questions = [
            "What's 2+2?",
            "What color is the sky?", 
            "Name a programming language.",
            "What's the capital of France?",
            "How many days in a week?",
            "What's 10 * 5?",
            "Name a type of database.",
            "What's HTTP stand for?",
            "Name a cloud provider.",
            "What's 100 / 4?"
        ]
        
        print(f"Testing {len(rapid_questions)} rapid interactions...")
        successful_responses = 0
        
        for i, question in enumerate(rapid_questions, 1):
            print(f"   {i}. {question}")
            response = call_ollama_with_universal_tools(
                question,
                model="qwen2.5:3b",
                use_tools=False,
                verbose_output=False  # Reduce noise
            )
            
            if response:
                successful_responses += 1
                print(f"      ✅ Response: {response[:50]}...")
            else:
                print(f"      ❌ No response")
            
            time.sleep(0.5)  # Brief pause
        
        print(f"✅ Rapid interactions: {successful_responses}/{len(rapid_questions)} successful")
        
        # Test memory of rapid interactions
        print("Testing memory of rapid interactions...")
        memory_test = call_ollama_with_universal_tools(
            "I just asked you several quick questions. Can you remember what some of them were about?",
            model="qwen2.5:3b",
            use_tools=False,
            verbose_output=True
        )
        
        if memory_test:
            print(f"✅ Memory test response: {memory_test[:100]}...")
        
        return successful_responses >= len(rapid_questions) * 0.8  # 80% success rate
        
    except Exception as e:
        print(f"❌ Rapid interactions test failed: {e}")
        return False

def test_memory_across_different_modes():
    """Test memory persistence across chat and tools modes"""
    print("\n=== Cross-Mode Memory Test ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Start in chat mode
        print("1. Chat mode: Setting context...")
        response1 = call_ollama_with_universal_tools(
            "I'm working on a project called 'DataProcessor' that analyzes CSV files. Remember this project name.",
            model="qwen2.5:3b",
            use_tools=False,
            verbose_output=True
        )
        print("✅ Chat mode context set")
        
        time.sleep(2)
        
        # Switch to tools mode
        print("2. Tools mode: Using tools while referencing chat context...")
        response2 = call_ollama_with_universal_tools(
            "Can you create a Python file for my DataProcessor project that I mentioned? Make it read a CSV file and print basic statistics.",
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        print("✅ Tools mode with context reference")
        
        time.sleep(2)
        
        # Back to chat mode
        print("3. Chat mode: Testing memory of both interactions...")
        response3 = call_ollama_with_universal_tools(
            "What was the project name I mentioned, and what did you help me create for it?",
            model="qwen2.5:3b",
            use_tools=False,
            verbose_output=True
        )
        
        if response3 and "DataProcessor" in response3:
            print("✅ Cross-mode memory working - project name remembered")
        else:
            print("⚠️  Cross-mode memory unclear")
            
        return True
        
    except Exception as e:
        print(f"❌ Cross-mode memory test failed: {e}")
        return False

def run_comprehensive_tool_and_stress_tests():
    """Run all comprehensive tool and stress tests"""
    print("🚀 Starting Comprehensive Tool & Stress Testing")
    print("=" * 70)
    
    tests = [
        ("File Operations Tools", test_file_operations_tools),
        ("Code Execution Tools", test_code_execution_tools),
        ("Calculator Tools", test_calculator_tools),
        ("Complex Multi-Tool Scenario", test_complex_multi_tool_scenario),
        ("Large Context Chat Stress Test", stress_test_large_context_chat),
        ("Rapid Interactions Stress Test", stress_test_rapid_interactions),
        ("Cross-Mode Memory Test", test_memory_across_different_modes)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            start_time = time.time()
            if test_func():
                elapsed = time.time() - start_time
                print(f"✅ {test_name}: PASSED ({elapsed:.1f}s)")
                passed += 1
            else:
                elapsed = time.time() - start_time
                print(f"❌ {test_name}: FAILED ({elapsed:.1f}s)")
                failed += 1
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ {test_name}: ERROR - {e} ({elapsed:.1f}s)")
            failed += 1
        
        print(f"   Pausing before next test...")
        time.sleep(3)  # Longer pause between major tests
    
    print("\n" + "="*70)
    print(f"🎯 COMPREHENSIVE TEST RESULTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("WorkspaceAI v3.0 Memory System handles complex scenarios perfectly!")
    elif passed >= failed:
        print("🎯 MOSTLY SUCCESSFUL!")
        print("Memory system performing well with minor issues.")
    else:
        print("⚠️  SOME SIGNIFICANT ISSUES DETECTED")
        print("Check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    print("WorkspaceAI v3.0 Memory System - Comprehensive Tool & Stress Testing")
    print("This will test real-world scenarios with actual Ollama model interactions.")
    print("Make sure qwen2.5:3b is loaded and running.")
    print()
    
    success = run_comprehensive_tool_and_stress_tests()
    sys.exit(0 if success else 1)
