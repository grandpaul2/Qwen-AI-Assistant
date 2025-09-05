"""
Test Suite for Session 1 Memory System Components

Comprehensive tests to validate token counting, model-specific memory,
adaptive budget management, and safety validation components.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import modules directly to avoid package-level dependencies
import importlib.util

def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import our modules directly
token_counter_module = import_module_from_file("token_counter", os.path.join(src_path, "token_counter.py"))
memory_module = import_module_from_file("model_specific_memory", os.path.join(src_path, "model_specific_memory.py"))
budget_module = import_module_from_file("adaptive_budget_manager", os.path.join(src_path, "adaptive_budget_manager.py"))
validator_module = import_module_from_file("safety_validator", os.path.join(src_path, "safety_validator.py"))

SimpleTokenCounter = token_counter_module.SimpleTokenCounter
TokenBudgetManager = token_counter_module.TokenBudgetManager
ModelSpecificMemory = memory_module.ModelSpecificMemory
AdaptiveBudgetManager = budget_module.AdaptiveBudgetManager
SafetyValidator = validator_module.SafetyValidator


def test_token_counter_edge_cases():
    """Test token counter with all the problematic patterns we identified"""
    print("\n=== Token Counter Edge Case Tests ===")
    
    counter = SimpleTokenCounter()
    
    # Test cases from the landmine analysis
    test_cases = [
        # (text, min_expected, max_expected, description)
        ("Hello world", 2, 6, "Simple English"),
        ("🚀🎯✅" * 10, 60, 120, "Emoji heavy text"),  
        ("(){}[]<>=!@#$%^&*" * 5, 15, 40, "Special characters"),
        ("a" * 1000, 250, 500, "Very long single word"),
        ("你好世界", 3, 8, "Chinese unicode text"),
        ("", 0, 1, "Empty string"),
        ("thisissuperlongwordwithoutspaces" * 10, 80, 200, "Long words without spaces"),
        ("Multiple\nlines\nof\ntext\nwith\nbreaks", 8, 20, "Multi-line text"),
        ("def function_name(param1, param2):\n    return param1 + param2", 12, 30, "Code snippet"),
        ("    # This is a comment\n    if condition:\n        print('hello')", 8, 25, "Indented code"),
        ("https://example.com/very/long/url/path?param=value&other=data", 15, 35, "URL with parameters")
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for text, min_exp, max_exp, desc in test_cases:
        try:
            estimated = counter.estimate_tokens(text)
            passed = min_exp <= estimated <= max_exp
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {desc}: {estimated} tokens (expected {min_exp}-{max_exp})")
            
            if not passed:
                print(f"   Text: {text[:50]}{'...' if len(text) > 50 else ''}")
            else:
                passed_tests += 1
                
        except Exception as e:
            print(f"❌ ERROR {desc}: {str(e)}")
    
    print(f"\nToken Counter Edge Cases: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


def test_token_counter_validation():
    """Test validation features of token counter"""
    print("\n=== Token Counter Validation Tests ===")
    
    counter = SimpleTokenCounter()
    tests_passed = 0
    
    try:
        # Test validation without actual tokens
        result = counter.validate_estimation_accuracy("Hello world test")
        print(f"✅ Validation without actual: characters_per_token={result.get('characters_per_token', 0):.2f}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Validation without actual failed: {e}")
    
    try:
        # Test validation with mock actual tokens
        result = counter.validate_estimation_accuracy("Hello world", actual_tokens=3)
        ratio = result.get('estimation_ratio', 0)
        print(f"✅ Validation with actual: estimation_ratio={ratio:.2f}")
        if 0.5 <= ratio <= 2.0:  # Reasonable range
            tests_passed += 1
        else:
            print(f"❌ Estimation ratio outside reasonable range: {ratio}")
    except Exception as e:
        print(f"❌ Validation with actual failed: {e}")
    
    try:
        # Test conversation token counting
        conversation = [
            {
                "user": {"content": "Hello, how are you?"},
                "assistant": {"content": "I'm doing well, thank you for asking!"}
            },
            {
                "user": {"content": "Can you help me with coding?"},
                "assistant": {"content": "Of course! I'd be happy to help with any coding questions."}
            }
        ]
        
        total_tokens = counter.estimate_conversation_tokens(conversation)
        print(f"✅ Conversation tokens: {total_tokens} (expected ~20-40)")
        if 15 <= total_tokens <= 50:  # Reasonable range
            tests_passed += 1
        else:
            print(f"❌ Conversation token count outside expected range: {total_tokens}")
    except Exception as e:
        print(f"❌ Conversation token counting failed: {e}")
    
    try:
        # Test batch processing
        texts = ["Hello", "World", "Test batch processing"]
        batch_results = counter.estimate_tokens_batch(texts)
        print(f"✅ Batch processing: {batch_results} tokens")
        if len(batch_results) == len(texts) and all(isinstance(x, int) and x > 0 for x in batch_results):
            tests_passed += 1
        else:
            print(f"❌ Batch processing returned invalid results: {batch_results}")
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
    
    print(f"\nToken Counter Validation: {tests_passed}/4 tests passed")
    return tests_passed == 4


def test_budget_manager():
    """Test budget allocation and validation"""
    print("\n=== Budget Manager Tests ===")
    
    counter = SimpleTokenCounter()
    budget_manager = TokenBudgetManager(counter)
    tests_passed = 0
    
    try:
        # Test normal allocation
        context_window = 32768
        percentages = {
            "conversation_memory": 60,
            "response_generation": 25,
            "tool_context": 10,
            "reserved": 5
        }
        
        budgets = budget_manager.calculate_percentage_budget(context_window, percentages)
        validation = budget_manager.validate_budget_allocation(budgets, context_window)
        
        print(f"✅ Budget allocation: {sum(budgets.values())} total tokens")
        print(f"✅ Validation: {validation['utilization_percent']:.1f}% utilization")
        
        if validation['is_valid'] and validation['utilization_percent'] <= 100:
            tests_passed += 1
        else:
            print(f"❌ Budget allocation invalid: {validation}")
            
    except Exception as e:
        print(f"❌ Budget allocation failed: {e}")
    
    try:
        # Test edge case: over-allocation
        bad_percentages = {
            "conversation_memory": 80,
            "response_generation": 40,
            "tool_context": 20,
            "reserved": 10  # Total = 150%
        }
        
        bad_budgets = budget_manager.calculate_percentage_budget(context_window, bad_percentages)
        bad_validation = budget_manager.validate_budget_allocation(bad_budgets, context_window)
        
        print(f"✅ Over-allocation test: {len(bad_validation.get('warnings', []))} warnings detected")
        
        if not bad_validation['is_valid'] or len(bad_validation.get('warnings', [])) > 0:
            tests_passed += 1
        else:
            print(f"❌ Over-allocation not detected properly")
            
    except Exception as e:
        print(f"❌ Over-allocation test failed: {e}")
    
    print(f"\nBudget Manager: {tests_passed}/2 tests passed")
    return tests_passed == 2


def test_model_specific_memory_safety():
    """Test model-specific memory with file safety and edge cases"""
    print("\n=== Model-Specific Memory Safety Tests ===")
    
    tests_passed = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            memory = ModelSpecificMemory(temp_dir)
            
            # Test problematic model names (collision testing)
            problematic_models = [
                "qwen2.5:7b",
                "qwen2-5:7b",  # Similar but different
                "model.v1:2b",
                "model-v1.2b",
                "llama3:8b-instruct-q4_0",
                "deepseek-coder:6.7b",
                "test/model:latest",
                "model with spaces:1b"
            ]
            
            filenames = []
            for model in problematic_models:
                filename = memory._model_to_filename(model)
                filenames.append(filename)
                print(f"✅ {model} → {filename}")
            
            # Check for collisions
            unique_filenames = set(filenames)
            if len(unique_filenames) == len(filenames):
                print("✅ No filename collisions detected")
                tests_passed += 1
            else:
                print(f"❌ Collision detected: {len(filenames)} models → {len(unique_filenames)} unique filenames")
            
        except Exception as e:
            print(f"❌ Model name conversion failed: {e}")
    
        try:
            # Test atomic operations
            test_model = "test-model:1b"
            
            # Add some exchanges
            success1 = memory.add_exchange(test_model, "Hello", "Hi there!", user_tokens=2, assistant_tokens=3)
            success2 = memory.add_exchange(test_model, "How are you?", "I'm good!", user_tokens=4, assistant_tokens=4)
            
            if success1 and success2:
                print("✅ Exchange addition successful")
                tests_passed += 1
            else:
                print("❌ Exchange addition failed")
            
        except Exception as e:
            print(f"❌ Exchange addition failed: {e}")
        
        try:
            # Load and verify
            loaded_memory = memory.load_memory(test_model)
            conversation_count = len(loaded_memory.get('current_conversation', []))
            print(f"✅ Memory loaded: {conversation_count} exchanges")
            
            if conversation_count >= 2:
                tests_passed += 1
            else:
                print(f"❌ Expected at least 2 exchanges, got {conversation_count}")
                
        except Exception as e:
            print(f"❌ Memory loading failed: {e}")
        
        try:
            # Test conversation history retrieval
            history = memory.get_conversation_history(test_model, max_exchanges=1)
            print(f"✅ History retrieval: {len(history)} exchanges (max 1)")
            
            if len(history) == 1:
                tests_passed += 1
            else:
                print(f"❌ Expected 1 exchange, got {len(history)}")
                
        except Exception as e:
            print(f"❌ History retrieval failed: {e}")
        
        try:
            # Test memory validation
            loaded_memory = memory.load_memory(test_model)
            is_valid = memory._validate_memory_structure(loaded_memory, test_model)
            print(f"✅ Memory validation: {is_valid}")
            
            if is_valid:
                tests_passed += 1
            else:
                print("❌ Memory validation failed")
                
        except Exception as e:
            print(f"❌ Memory validation failed: {e}")
        
        try:
            # Test corrupted memory handling
            corrupted_path = memory._get_memory_path(test_model)
            with open(corrupted_path, 'w') as f:
                f.write("invalid json content {")
            
            # Should gracefully handle corruption
            recovered_memory = memory.load_memory(test_model)
            recovered_count = len(recovered_memory.get('current_conversation', []))
            print(f"✅ Corruption recovery: {recovered_count} exchanges (new memory created)")
            
            if isinstance(recovered_memory, dict) and 'current_conversation' in recovered_memory:
                tests_passed += 1
            else:
                print("❌ Corruption recovery failed")
                
        except Exception as e:
            print(f"❌ Corruption recovery failed: {e}")
    
    print(f"\nModel-Specific Memory: {tests_passed}/6 tests passed")
    return tests_passed == 6


def test_adaptive_budget_complexity():
    """Test complexity analysis and anti-gaming measures"""
    print("\n=== Adaptive Budget Manager Tests ===")
    
    budget_manager = AdaptiveBudgetManager()
    tests_passed = 0
    
    # Test complexity scoring with different query types
    test_queries = [
        ("hi", 0.0, 0.3, "Simple greeting"),
        ("How are you doing today?", 0.1, 0.4, "Simple question"),
        ("analyze create implement code function write analyze", 0.3, 0.8, "Keyword stuffing attempt"),
        ("Can you help me debug this complex Python function that handles async database connections?", 0.4, 0.9, "Complex technical question"),
        ("def complex_function(data):\n    for item in data:\n        if item.valid:\n            process(item)", 0.3, 0.8, "Code snippet"),
        ("What is the meaning of life?" * 20, 0.2, 0.7, "Long repetitive query"),
        ("Please analyze the architectural patterns in microservices and implement a solution", 0.5, 1.0, "Complex multi-step request")
    ]
    
    print("\nComplexity Analysis Results:")
    complexity_tests_passed = 0
    
    for query, min_expected, max_expected, description in test_queries:
        try:
            complexity = budget_manager.analyze_complexity(query, "tools")
            breakdown = budget_manager.get_complexity_breakdown(query, "tools")
            
            passed = min_expected <= complexity <= max_expected
            status = "✅ PASS" if passed else "❌ FAIL"
            
            print(f"{status} {description}:")
            print(f"  Complexity: {complexity:.3f} (expected {min_expected:.1f}-{max_expected:.1f})")
            
            if passed:
                complexity_tests_passed += 1
            else:
                print(f"  Query: {query[:60]}{'...' if len(query) > 60 else ''}")
                
        except Exception as e:
            print(f"❌ ERROR {description}: {e}")
    
    if complexity_tests_passed >= len(test_queries) * 0.7:  # Allow 30% tolerance
        tests_passed += 1
        print(f"✅ Complexity analysis: {complexity_tests_passed}/{len(test_queries)} reasonable")
    else:
        print(f"❌ Complexity analysis: {complexity_tests_passed}/{len(test_queries)} reasonable")
    
    # Test budget allocation across complexity spectrum
    context_window = 32768
    
    print("\nBudget Allocation Tests:")
    try:
        simple_budgets = budget_manager.calculate_adaptive_budgets(context_window, "tools", "hi")
        complex_budgets = budget_manager.calculate_adaptive_budgets(context_window, "tools", "analyze and implement complex debugging solution")
        
        simple_response_pct = (simple_budgets.get('response_generation', 0) / context_window) * 100
        complex_response_pct = (complex_budgets.get('response_generation', 0) / context_window) * 100
        
        print(f"Simple query response allocation: {simple_response_pct:.1f}%")
        print(f"Complex query response allocation: {complex_response_pct:.1f}%")
        
        # Complex queries should get more response allocation
        if complex_response_pct > simple_response_pct:
            tests_passed += 1
            print("✅ Complex queries get higher response allocation")
        else:
            print("❌ Complex queries should get higher response allocation")
            
        # Test budget validation
        simple_validation = budget_manager.validate_budget_allocation(simple_budgets, context_window)
        complex_validation = budget_manager.validate_budget_allocation(complex_budgets, context_window)
        
        if simple_validation['is_valid'] and complex_validation['is_valid']:
            tests_passed += 1
            print("✅ Budget allocations are valid")
        else:
            print("❌ Budget allocations invalid")
            
    except Exception as e:
        print(f"❌ Budget allocation test failed: {e}")
    
    print(f"\nAdaptive Budget Manager: {tests_passed}/3 tests passed")
    return tests_passed == 3


def test_safety_validator():
    """Test safety validator with real component integration"""
    print("\n=== Safety Validator Tests ===")
    
    validator = SafetyValidator()
    tests_passed = 0
    
    # Test token budget validation
    context_window = 32768
    
    try:
        # Valid budget
        good_budgets = {
            "conversation_memory": 19660,  # 60%
            "response_generation": 8192,   # 25%
            "tool_context": 3277,          # 10%
            "reserved": 1639               # 5%
        }
        
        result = validator.validate_token_budgets(good_budgets, context_window)
        print(f"✅ Valid budget validation: {len(result.errors)} errors, {len(result.warnings)} warnings")
        
        if result.is_valid and len(result.errors) == 0:
            tests_passed += 1
        else:
            print(f"❌ Valid budget should pass validation")
            
    except Exception as e:
        print(f"❌ Valid budget validation failed: {e}")
    
    try:
        # Invalid budget (over-allocation)
        bad_budgets = {
            "conversation_memory": 26214,  # 80%
            "response_generation": 13107,  # 40% 
            "tool_context": 6553,          # 20%
            "reserved": 3277               # 10% (Total: 150%)
        }
        
        result = validator.validate_token_budgets(bad_budgets, context_window)
        print(f"✅ Invalid budget validation: {len(result.errors)} errors, {len(result.warnings)} warnings")
        
        if not result.is_valid or len(result.errors) > 0:
            tests_passed += 1
            print("✅ Over-allocation correctly detected")
        else:
            print("❌ Over-allocation should be detected")
            
    except Exception as e:
        print(f"❌ Invalid budget validation failed: {e}")
    
    try:
        # Test memory structure validation
        valid_memory = {
            "metadata": {
                "model": "test-model",
                "created_at": "2025-09-04T12:00:00Z",
                "last_modified": "2025-09-04T12:00:00Z",
                "version": "3.0",
                "total_exchanges": 1
            },
            "current_conversation": [
                {
                    "user": {"content": "Hello", "tokens": 2},
                    "assistant": {"content": "Hi there!", "tokens": 3}
                }
            ],
            "summarized_conversations": []
        }
        
        result = validator.validate_memory_structure(valid_memory, "test-model")
        print(f"✅ Memory structure validation: {len(result.errors)} errors, {len(result.warnings)} warnings")
        
        if result.is_valid:
            tests_passed += 1
        else:
            print(f"❌ Valid memory structure should pass validation")
            for error in result.errors:
                print(f"  Error: {error['message']}")
                
    except Exception as e:
        print(f"❌ Memory structure validation failed: {e}")
    
    try:
        # Test token estimation validation
        result = validator.validate_token_estimation_accuracy(10, 8, "Hello world")
        print(f"✅ Token estimation validation: ratio={10/8:.2f}")
        
        # Should be within reasonable bounds
        if result.is_valid or len(result.warnings) <= 1:  # Allow some warnings
            tests_passed += 1
        else:
            print(f"❌ Token estimation validation too strict")
            
    except Exception as e:
        print(f"❌ Token estimation validation failed: {e}")
    
    print(f"\nSafety Validator: {tests_passed}/4 tests passed")
    return tests_passed == 4


def test_integration():
    """Test integration between components"""
    print("\n=== Integration Tests ===")
    
    tests_passed = 0
    
    try:
        # Test full workflow
        counter = SimpleTokenCounter()
        budget_manager = AdaptiveBudgetManager()
        validator = SafetyValidator()
        
        # Simulate a complex query workflow
        user_query = "Please analyze this code and implement a better solution with error handling"
        context_window = 32768
        
        # Get complexity and budgets
        complexity = budget_manager.analyze_complexity(user_query, "tools")
        budgets = budget_manager.calculate_adaptive_budgets(context_window, "tools", user_query)
        
        # Validate the results
        budget_validation = validator.validate_token_budgets(budgets, context_window, complexity)
        
        print(f"✅ Integration workflow completed:")
        print(f"  Complexity: {complexity:.3f}")
        print(f"  Budget valid: {budget_validation.is_valid}")
        print(f"  Response allocation: {(budgets.get('response_generation', 0) / context_window) * 100:.1f}%")
        
        if budget_validation.is_valid and complexity > 0:
            tests_passed += 1
        else:
            print("❌ Integration workflow failed validation")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
    
    try:
        # Test memory integration
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = ModelSpecificMemory(temp_dir)
            
            # Add exchange and validate
            success = memory.add_exchange("test-model", "Hello", "Hi there!")
            loaded = memory.load_memory("test-model")
            
            # Validate memory structure
            memory_validation = validator.validate_memory_structure(loaded, "test-model")
            
            print(f"✅ Memory integration:")
            print(f"  Exchange added: {success}")
            print(f"  Memory valid: {memory_validation.is_valid}")
            
            if success and memory_validation.is_valid:
                tests_passed += 1
            else:
                print("❌ Memory integration failed")
                
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
    
    print(f"\nIntegration Tests: {tests_passed}/2 tests passed")
    return tests_passed == 2


def run_all_tests():
    """Run all Session 1 component tests"""
    print("=" * 70)
    print("WorkspaceAI Session 1 Component Tests")
    print("=" * 70)
    
    tests = [
        ("Token Counter Edge Cases", test_token_counter_edge_cases),
        ("Token Counter Validation", test_token_counter_validation),
        ("Budget Manager", test_budget_manager),
        ("Model-Specific Memory Safety", test_model_specific_memory_safety),
        ("Adaptive Budget Complexity", test_adaptive_budget_complexity),
        ("Safety Validator", test_safety_validator),
        ("Integration Tests", test_integration)
    ]
    
    passed_suites = 0
    failed_suites = 0
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 50}")
        print(f"Running: {test_name}")
        print(f"{'-' * 50}")
        
        try:
            result = test_func()
            if result:
                passed_suites += 1
                print(f"\n✅ {test_name} SUITE PASSED")
            else:
                failed_suites += 1
                print(f"\n❌ {test_name} SUITE FAILED")
        except Exception as e:
            failed_suites += 1
            print(f"\n❌ {test_name} SUITE ERROR: {str(e)}")
    
    print("\n" + "=" * 70)
    print("FINAL TEST RESULTS")
    print("=" * 70)
    print(f"Test Suites: {passed_suites} passed, {failed_suites} failed")
    
    if failed_suites == 0:
        print("🎉 ALL TESTS PASSED - Session 1 components are ready!")
    else:
        print("⚠️  Some tests failed - review issues before proceeding to Session 2")
    
    print("=" * 70)
    
    return failed_suites == 0


if __name__ == "__main__":
    # Fix import issue by catching missing re module in token_counter
    try:
        import re
        # Add re to token_counter if needed
        import src.token_counter as tc
        if not hasattr(tc, 're'):
            tc.re = re
    except ImportError:
        print("❌ Required modules not available")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
