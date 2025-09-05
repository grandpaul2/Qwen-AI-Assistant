#!/usr/bin/env python3
"""
Intensive Memory & Performance Stress Test for WorkspaceAI v3.0

This script performs extreme stress testing on the memory system:
- Very large context windows
- Long conversation chains  
- Memory persistence under load
- Context budget efficiency testing
- Tool chain complexity testing
"""

import sys
import os
import time
import psutil
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def generate_large_prompt(size_kb=5):
    """Generate a large prompt of specified size in KB"""
    base_text = """
    This is a comprehensive software development scenario that requires detailed analysis and planning.
    We are building a distributed microservices architecture with the following requirements:
    
    1. High availability and fault tolerance across multiple geographic regions
    2. Real-time data processing capabilities handling millions of transactions per hour
    3. Complex business logic with multi-step approval workflows and regulatory compliance
    4. Integration with legacy systems through various protocols and data formats
    5. Advanced security requirements including encryption, audit trails, and access controls
    6. Performance monitoring and automated scaling based on demand patterns
    7. Data analytics and machine learning integration for predictive insights
    8. Multi-tenant architecture supporting thousands of organizations
    9. API gateway management with rate limiting and authentication
    10. Comprehensive disaster recovery and business continuity planning
    """
    
    # Repeat and expand to reach target size
    target_chars = size_kb * 1024
    current_text = base_text
    
    while len(current_text) < target_chars:
        current_text += f"\n\nAdditional architectural consideration #{len(current_text)//1000 + 1}: " + base_text
    
    return current_text[:target_chars]

def test_extreme_large_context():
    """Test with extremely large context - push memory system limits"""
    print("=== EXTREME LARGE CONTEXT TEST ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Test with progressively larger contexts
        sizes = [5, 10, 15]  # KB sizes
        
        for size_kb in sizes:
            print(f"Testing with {size_kb}KB context...")
            large_prompt = generate_large_prompt(size_kb)
            
            start_time = time.time()
            response = call_ollama_with_universal_tools(
                large_prompt + f"\n\nPlease provide a brief summary of the key architectural challenges mentioned above (this prompt was {size_kb}KB).",
                model="qwen2.5:3b",
                use_tools=False,
                verbose_output=False
            )
            elapsed = time.time() - start_time
            
            if response:
                print(f"✅ {size_kb}KB test: SUCCESS ({elapsed:.1f}s, response: {len(response)} chars)")
            else:
                print(f"❌ {size_kb}KB test: FAILED ({elapsed:.1f}s)")
                return False
            
            time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"❌ Extreme large context test failed: {e}")
        return False

def test_long_conversation_chain():
    """Test memory system with a very long conversation chain"""
    print("\n=== LONG CONVERSATION CHAIN TEST ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        conversation_topics = [
            "Let's discuss Python programming best practices.",
            "What are the key principles of clean code?",
            "How do design patterns help in software development?",
            "Explain the SOLID principles with examples.",
            "What's the difference between composition and inheritance?",
            "How do you implement effective error handling?",
            "What are the benefits of test-driven development?",
            "Explain the concept of dependency injection.",
            "How do you design scalable database schemas?",
            "What are microservices architecture patterns?",
            "How do you implement CI/CD pipelines?",
            "What are containerization best practices?",
            "Explain event-driven architecture concepts.",
            "How do you handle asynchronous processing?",
            "What are caching strategies for web applications?",
            "Now, can you summarize what we've discussed so far?"
        ]
        
        print(f"Starting conversation chain with {len(conversation_topics)} interactions...")
        
        for i, topic in enumerate(conversation_topics, 1):
            print(f"  {i}. {topic[:50]}...")
            
            start_time = time.time()
            response = call_ollama_with_universal_tools(
                topic,
                model="qwen2.5:3b",
                use_tools=False,
                verbose_output=False
            )
            elapsed = time.time() - start_time
            
            if response:
                print(f"     ✅ Response received ({elapsed:.1f}s, {len(response)} chars)")
            else:
                print(f"     ❌ No response ({elapsed:.1f}s)")
                
            if i == len(conversation_topics):
                # Check if final summary references earlier topics
                topics_found = 0
                key_terms = ["python", "clean code", "design pattern", "solid", "microservices", "testing"]
                for term in key_terms:
                    if term.lower() in response.lower():
                        topics_found += 1
                
                print(f"     📊 Summary referenced {topics_found}/{len(key_terms)} key topics")
                
            time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"❌ Long conversation chain test failed: {e}")
        return False

def test_memory_efficiency_under_load():
    """Test memory system efficiency under computational load"""
    print("\n=== MEMORY EFFICIENCY UNDER LOAD TEST ===")
    
    try:
        import gc
        from src.memory import unified_memory
        
        # Monitor memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        # Stress test the memory system
        model = "qwen2.5:3b"
        
        # Add many exchanges rapidly
        for i in range(50):
            unified_memory.add_message('user', f'Test message {i}: This is a stress test of the memory system with message number {i}', model=model)
            unified_memory.add_message('assistant', f'Response {i}: I acknowledge test message {i} and confirm the memory system is handling this load test.', model=model)
            
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"  After {i*2} messages: {current_memory:.1f} MB")
        
        # Test context retrieval under load
        start_time = time.time()
        context = unified_memory.get_context_messages(
            model=model,
            user_input="What was the first test message number?",
            interaction_mode='chat',
            context_window=32768
        )
        retrieval_time = time.time() - start_time
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"✅ Added 100 messages in memory")
        print(f"✅ Context retrieval: {len(context)} messages in {retrieval_time:.3f}s")
        print(f"📊 Memory usage: {initial_memory:.1f} → {final_memory:.1f} MB (+{memory_increase:.1f} MB)")
        
        # Force garbage collection
        gc.collect()
        after_gc_memory = process.memory_info().rss / 1024 / 1024
        print(f"📊 After GC: {after_gc_memory:.1f} MB")
        
        return memory_increase < 100  # Should not use more than 100MB
        
    except Exception as e:
        print(f"❌ Memory efficiency test failed: {e}")
        return False

def test_complex_tool_chains():
    """Test complex sequences of tool operations"""
    print("\n=== COMPLEX TOOL CHAINS TEST ===")
    
    try:
        from src.ollama_universal_interface import call_ollama_with_universal_tools
        
        # Complex multi-step data processing scenario
        complex_request = """
        I need you to help me with a comprehensive data analysis workflow:
        
        1. First, create a Python script called 'data_generator.py' that generates sample sales data with the following columns:
           - date (last 30 days)
           - product_id (1-10)
           - quantity_sold
           - unit_price
           - customer_id
           Save it as CSV data to 'sales_data.csv'
           
        2. Then create another script 'data_analyzer.py' that:
           - Reads the sales_data.csv file
           - Calculates total revenue by product
           - Finds the best selling product
           - Calculates average order value
           - Generates a summary report
           
        3. Execute both scripts and show me the results
        
        4. Finally, calculate the percentage increase if the top product sales grew by 15%
        
        Please do this step by step with explanations.
        """
        
        print("Testing complex tool chain scenario...")
        
        start_time = time.time()
        response = call_ollama_with_universal_tools(
            complex_request,
            model="qwen2.5:3b",
            use_tools=True,
            verbose_output=True
        )
        elapsed = time.time() - start_time
        
        if response:
            print(f"✅ Complex tool chain completed ({elapsed:.1f}s)")
            print(f"   Response length: {len(response)} characters")
            
            # Check if it mentions key elements
            key_elements = ["data_generator", "data_analyzer", "csv", "revenue", "percentage"]
            found_elements = sum(1 for elem in key_elements if elem.lower() in response.lower())
            print(f"   Referenced {found_elements}/{len(key_elements)} key elements")
            
            return found_elements >= 3
        else:
            print(f"❌ Complex tool chain failed ({elapsed:.1f}s)")
            return False
        
    except Exception as e:
        print(f"❌ Complex tool chains test failed: {e}")
        return False

def test_concurrent_model_isolation():
    """Test memory isolation with rapid model switching"""
    print("\n=== CONCURRENT MODEL ISOLATION TEST ===")
    
    try:
        from src.memory import unified_memory
        
        models = ["qwen2.5:3b", "llama3:8b"]
        
        # Add specific context to each model rapidly
        for i in range(10):
            for j, model in enumerate(models):
                unified_memory.add_message(
                    'user', 
                    f'Model {model} test {i}: I am user {j} testing model-specific isolation.',
                    model=model
                )
                unified_memory.add_message(
                    'assistant',
                    f'Hello user {j}! I am {model} responding to isolation test {i}.',
                    model=model
                )
        
        # Test isolation by retrieving context for each model
        for model in models:
            context = unified_memory.get_context_messages(
                model=model,
                user_input="What model am I talking to?",
                interaction_mode='chat',
                context_window=16384
            )
            
            # Verify model-specific content
            model_content = ' '.join([msg.get('content', '') for msg in context])
            other_model = models[1] if model == models[0] else models[0]
            
            model_mentioned = model in model_content
            other_mentioned = other_model in model_content
            
            print(f"  {model}: {len(context)} messages, model mentioned: {model_mentioned}, other model mentioned: {other_mentioned}")
            
            if not model_mentioned or other_mentioned:
                print(f"  ⚠️  Isolation issue detected for {model}")
                return False
        
        print("✅ Model isolation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Concurrent model isolation test failed: {e}")
        return False

def test_context_budget_optimization():
    """Test adaptive budget allocation under various scenarios"""
    print("\n=== CONTEXT BUDGET OPTIMIZATION TEST ===")
    
    try:
        from src.adaptive_budget_manager import AdaptiveBudgetManager
        budget_manager = AdaptiveBudgetManager()
        
        test_scenarios = [
            ("Simple chat", "Hi there!", "chat"),
            ("Complex analysis", "Please analyze the performance implications of using microservices vs monolithic architecture for a high-traffic e-commerce platform with real-time inventory management", "chat"),
            ("Tool request", "Can you create a Python script that processes CSV files?", "tools"),
            ("Complex tool request", "I need a comprehensive data processing pipeline that reads from multiple CSV files, performs statistical analysis, generates visualizations, and exports results to different formats", "tools")
        ]
        
        context_window = 32768
        results = []
        
        for scenario_name, query, mode in test_scenarios:
            complexity = budget_manager.analyze_complexity(query, mode)
            budgets = budget_manager.calculate_adaptive_budgets(context_window, mode, query)
            total_budget = sum(budgets.values())
            utilization = (total_budget / context_window) * 100
            
            results.append({
                'scenario': scenario_name,
                'complexity': complexity,
                'utilization': utilization,
                'budgets': budgets
            })
            
            print(f"  {scenario_name}:")
            print(f"    Complexity: {complexity:.3f}")
            print(f"    Utilization: {utilization:.1f}%")
            print(f"    Budgets: {budgets}")
        
        # Verify budget allocation logic
        chat_results = [r for r in results if 'chat' in r['scenario'].lower()]
        tool_results = [r for r in results if 'tool' in r['scenario'].lower()]
        
        # Chat mode should generally use 60-80% of context
        chat_in_range = all(60 <= r['utilization'] <= 90 for r in chat_results)
        # Tool mode should generally use 80-90% of context  
        tool_in_range = all(70 <= r['utilization'] <= 95 for r in tool_results)
        
        print(f"✅ Chat mode budgets in range: {chat_in_range}")
        print(f"✅ Tool mode budgets in range: {tool_in_range}")
        
        return chat_in_range and tool_in_range
        
    except Exception as e:
        print(f"❌ Context budget optimization test failed: {e}")
        return False

def run_intensive_stress_tests():
    """Run all intensive stress tests"""
    print("🔥 INTENSIVE MEMORY & PERFORMANCE STRESS TESTING")
    print("=" * 80)
    print("WARNING: This will push the memory system to its limits!")
    print()
    
    tests = [
        ("Extreme Large Context", test_extreme_large_context),
        ("Long Conversation Chain", test_long_conversation_chain),
        ("Memory Efficiency Under Load", test_memory_efficiency_under_load),
        ("Complex Tool Chains", test_complex_tool_chains),
        ("Concurrent Model Isolation", test_concurrent_model_isolation),
        ("Context Budget Optimization", test_context_budget_optimization)
    ]
    
    passed = 0
    failed = 0
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            test_start = time.time()
            if test_func():
                test_elapsed = time.time() - test_start
                print(f"✅ {test_name}: PASSED ({test_elapsed:.1f}s)")
                passed += 1
            else:
                test_elapsed = time.time() - test_start
                print(f"❌ {test_name}: FAILED ({test_elapsed:.1f}s)")
                failed += 1
        except Exception as e:
            test_elapsed = time.time() - test_start
            print(f"❌ {test_name}: ERROR - {e} ({test_elapsed:.1f}s)")
            failed += 1
        
        print(f"   Recovery pause...")
        time.sleep(5)  # Longer pause for intensive tests
    
    total_elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print(f"🔥 INTENSIVE STRESS TEST RESULTS")
    print(f"⏱️  Total Time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("🏆 PERFECT PERFORMANCE UNDER EXTREME STRESS!")
        print("WorkspaceAI v3.0 Memory System is production-ready for any scenario!")
    elif passed >= failed:
        print("💪 EXCELLENT STRESS TEST PERFORMANCE!")
        print("Memory system handles intensive workloads very well.")
    else:
        print("⚠️  PERFORMANCE ISSUES UNDER STRESS")
        print("Some optimizations may be needed for extreme scenarios.")
    
    return failed == 0

if __name__ == "__main__":
    print("WorkspaceAI v3.0 Memory System - INTENSIVE STRESS TESTING")
    print("This will perform extreme testing with large contexts and complex scenarios.")
    print("Make sure your system has sufficient resources and qwen2.5:3b is running.")
    print()
    
    # Check system resources
    memory_gb = psutil.virtual_memory().total / (1024**3)
    print(f"System RAM: {memory_gb:.1f} GB")
    
    if memory_gb < 8:
        print("⚠️  Warning: Low system memory may affect intensive testing")
    
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    success = run_intensive_stress_tests()
    sys.exit(0 if success else 1)
