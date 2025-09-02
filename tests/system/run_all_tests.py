"""
Comprehensive Test Suite Runner for WorkspaceAI
Organizes and runs tests by category with detailed reporting
"""

import unittest
import sys
import os
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def discover_and_run_tests(test_directory: str, pattern: str = "test_*.py", verbosity: int = 2):
    """Discover and run tests in a specific directory"""
    loader = unittest.TestLoader()
    suite = loader.discover(test_directory, pattern=pattern)
    
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time
    
    return result, elapsed_time


def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running Unit Tests")
    print("=" * 50)
    
    # Run core unit tests
    print("\n📦 Core Module Tests:")
    core_result, core_time = discover_and_run_tests("tests/unit", "test_*.py")
    
    # Run bot logic enhancement unit tests
    print("\n🤖 Bot Logic Enhancement Unit Tests:")
    ble_result, ble_time = discover_and_run_tests("tests/unit/bot_logic_enhancement", "test_*.py")
    
    return {
        "core": (core_result, core_time),
        "bot_logic_enhancement": (ble_result, ble_time)
    }


def run_integration_tests():
    """Run all integration tests"""
    print("\n🔗 Running Integration Tests")
    print("=" * 50)
    
    # Run general integration tests
    print("\n🔧 General Integration Tests:")
    general_result, general_time = discover_and_run_tests("tests/integration", "test_*.py")
    
    # Run bot logic enhancement integration tests
    print("\n🤖 Bot Logic Enhancement Integration Tests:")
    ble_result, ble_time = discover_and_run_tests("tests/integration/bot_logic_enhancement", "test_*.py")
    
    return {
        "general": (general_result, general_time),
        "bot_logic_enhancement": (ble_result, ble_time)
    }


def run_production_tests():
    """Run production readiness tests"""
    print("\n🚀 Running Production Tests")
    print("=" * 50)
    
    production_result, production_time = discover_and_run_tests("tests/production", "test_*.py")
    
    return {"production": (production_result, production_time)}


def run_security_tests():
    """Run security tests"""
    print("\n🔒 Running Security Tests")
    print("=" * 50)
    
    security_result, security_time = discover_and_run_tests("tests/security", "test_*.py")
    
    return {"security": (security_result, security_time)}


def print_category_summary(category_name: str, results: dict):
    """Print summary for a test category"""
    print(f"\n📊 {category_name.upper()} TEST SUMMARY:")
    print("-" * 40)
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_time = 0.0
    
    for subcategory, (result, elapsed_time) in results.items():
        tests_run = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        successes = tests_run - failures - errors
        
        total_tests += tests_run
        total_failures += failures
        total_errors += errors
        total_time += elapsed_time
        
        print(f"  {subcategory.replace('_', ' ').title()}:")
        print(f"    ✅ Tests: {tests_run} | ✅ Pass: {successes} | ❌ Fail: {failures} | ⚠️ Error: {errors}")
        print(f"    ⏱️ Time: {elapsed_time:.2f}s")
        
        if failures > 0:
            print(f"    💥 Failures:")
            for test, traceback in result.failures:
                print(f"      • {test}")
        
        if errors > 0:
            print(f"    ⚠️ Errors:")
            for test, traceback in result.errors:
                print(f"      • {test}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"\n  🎯 Overall: {total_tests} tests, {success_rate:.1f}% success rate, {total_time:.2f}s")
    
    return total_tests, total_failures, total_errors, total_time, success_rate


def run_all_tests():
    """Run all test categories and provide comprehensive summary"""
    print("🧪 WorkspaceAI Comprehensive Test Suite")
    print("=" * 60)
    print("Running all test categories with detailed reporting...")
    
    overall_start = time.time()
    
    # Run all test categories
    try:
        unit_results = run_unit_tests()
    except Exception as e:
        print(f"❌ Unit tests failed: {e}")
        unit_results = {}
    
    try:
        integration_results = run_integration_tests()
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        integration_results = {}
    
    try:
        production_results = run_production_tests()
    except Exception as e:
        print(f"❌ Production tests failed: {e}")
        production_results = {}
    
    try:
        security_results = run_security_tests()
    except Exception as e:
        print(f"❌ Security tests failed: {e}")
        security_results = {}
    
    overall_elapsed = time.time() - overall_start
    
    # Print comprehensive summary
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    all_results = [
        ("Unit Tests", unit_results),
        ("Integration Tests", integration_results),
        ("Production Tests", production_results),
        ("Security Tests", security_results)
    ]
    
    grand_total_tests = 0
    grand_total_failures = 0
    grand_total_errors = 0
    grand_total_time = 0.0
    
    for category_name, category_results in all_results:
        if category_results:
            tests, failures, errors, time_taken, success_rate = print_category_summary(category_name, category_results)
            grand_total_tests += tests
            grand_total_failures += failures
            grand_total_errors += errors
            grand_total_time += time_taken
    
    # Overall summary
    print("\n" + "=" * 60)
    print("🎯 FINAL SUMMARY")
    print("=" * 60)
    
    grand_success_rate = ((grand_total_tests - grand_total_failures - grand_total_errors) / grand_total_tests * 100) if grand_total_tests > 0 else 0
    
    print(f"📊 Total Tests Run: {grand_total_tests}")
    print(f"✅ Total Successes: {grand_total_tests - grand_total_failures - grand_total_errors}")
    print(f"❌ Total Failures: {grand_total_failures}")
    print(f"⚠️ Total Errors: {grand_total_errors}")
    print(f"🎯 Overall Success Rate: {grand_success_rate:.1f}%")
    print(f"⏱️ Total Execution Time: {grand_total_time:.2f}s")
    print(f"⏱️ Overall Runtime: {overall_elapsed:.2f}s")
    
    # Final assessment
    if grand_success_rate == 100:
        print("\n🎉 ALL TESTS PASSED - SYSTEM IS PRODUCTION READY! 🎉")
        status = "PRODUCTION_READY"
    elif grand_success_rate >= 95:
        print("\n✅ Excellent test coverage - Minor issues to address")
        status = "MOSTLY_READY"
    elif grand_success_rate >= 85:
        print("\n⚠️ Good test coverage - Some issues need attention")
        status = "NEEDS_REVIEW"
    else:
        print("\n❌ Significant test failures - Review and fixes needed")
        status = "NEEDS_WORK"
    
    print(f"\n🏷️ System Status: {status}")
    
    return grand_success_rate == 100


def run_specific_category(category: str):
    """Run tests for a specific category"""
    category = category.lower()
    
    if category == "unit":
        results = run_unit_tests()
        print_category_summary("Unit Tests", results)
    elif category == "integration":
        results = run_integration_tests()
        print_category_summary("Integration Tests", results)
    elif category == "production":
        results = run_production_tests()
        print_category_summary("Production Tests", results)
    elif category == "security":
        results = run_security_tests()
        print_category_summary("Security Tests", results)
    elif category == "bot_logic" or category == "ble":
        # Run just bot logic enhancement tests
        print("🤖 Bot Logic Enhancement Test Suite")
        print("=" * 50)
        
        unit_ble = discover_and_run_tests("tests/unit/bot_logic_enhancement", "test_*.py")
        integration_ble = discover_and_run_tests("tests/integration/bot_logic_enhancement", "test_*.py")
        
        results = {
            "unit_bot_logic": unit_ble,
            "integration_bot_logic": integration_ble
        }
        print_category_summary("Bot Logic Enhancement", results)
    else:
        print(f"❌ Unknown category: {category}")
        print("Available categories: unit, integration, production, security, bot_logic")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        category = sys.argv[1]
        run_specific_category(category)
    else:
        success = run_all_tests()
        if not success:
            sys.exit(1)
