#!/usr/bin/env python3
"""
Quick Bot Testing Commands

Simple commands to quickly run and record bot enhancement testing data.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class QuickTestRunner:
    """Quick command-line test runner"""
    
    def __init__(self):
        self.test_results_dir = "test_results"
        os.makedirs(self.test_results_dir, exist_ok=True)
    
    def run_command(self, command: str) -> bool:
        """Run a specific test command"""
        commands = {
            "full": self.run_full_automated_test,
            "quick": self.run_quick_test,
            "context": self.run_context_test,
            "single": self.run_single_scenario_test,
            "benchmark": self.run_benchmark_test,
            "report": self.show_latest_report,
            "list": self.list_available_commands
        }
        
        if command in commands:
            return commands[command]()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: " + ", ".join(commands.keys()))
            return False
    
    def run_full_automated_test(self) -> bool:
        """Run complete automated test suite"""
        print("🤖 Running Full Automated Bot Enhancement Test Suite...")
        
        try:
            result = subprocess.run([
                sys.executable, "tests/automated_bot_testing.py"
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
                
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Failed to run automated tests: {e}")
            return False
    
    def run_quick_test(self) -> bool:
        """Run quick validation test"""
        print("⚡ Running Quick Enhancement Validation...")
        
        # Quick test scenarios
        quick_scenarios = [
            "Create a file called test.txt",
            "Add some content to that file", 
            "Create a Python project structure"
        ]
        
        try:
            # Import and test quickly
            sys.path.insert(0, os.getcwd())
            from src.ollama.enhanced_interface import get_enhanced_components
            
            context, intent_classifier, tool_selector = get_enhanced_components()[:3]
            
            results = []
            for i, scenario in enumerate(quick_scenarios, 1):
                print(f"  [{i}/3] Testing: {scenario}")
                
                # Test intent classification
                intent, confidence, context_info = intent_classifier.classify_with_context(scenario)
                
                # Test tool selection
                tool_selection = tool_selector.select_tools_with_context(
                    intent, scenario, confidence, context_info
                )
                
                score = self.quick_score(intent, confidence, len(context_info), tool_selection)
                results.append(score)
                print(f"      Score: {score:.1f}/10")
                
                # Add operation for context building
                if i < 3:  # Only for first two to build context
                    context.add_operation(
                        operation_type="quick_test",
                        tool_name=tool_selection.get('primary_tool', 'test'),
                        parameters={"input": scenario},
                        result="Quick test result",
                        success=True,
                        context_tags=["quick_test"]
                    )
            
            avg_score = sum(results) / len(results)
            print(f"\n✅ Quick Test Average: {avg_score:.1f}/10")
            
            # Save quick results
            self.save_quick_results(quick_scenarios, results, avg_score)
            
            return avg_score >= 5.0
            
        except Exception as e:
            print(f"❌ Quick test failed: {e}")
            return False
    
    def run_context_test(self) -> bool:
        """Test context awareness specifically"""
        print("🧠 Testing Context Awareness...")
        
        context_sequence = [
            "Create a Python script called data_processor.py",
            "Add error handling to that script",
            "Create a test file for it", 
            "Show me both files"
        ]
        
        try:
            sys.path.insert(0, os.getcwd())
            from src.ollama.enhanced_interface import get_enhanced_components
            
            context, intent_classifier, tool_selector = get_enhanced_components()[:3]
            
            context_scores = []
            for step, scenario in enumerate(context_sequence, 1):
                print(f"  Step {step}: {scenario}")
                
                intent, confidence, context_info = intent_classifier.classify_with_context(scenario)
                
                context_aware = len(context_info) > 0
                references_previous = step > 1 and ("that" in scenario.lower() or "it" in scenario.lower() or "both" in scenario.lower())
                
                step_score = 5.0  # Base
                if context_aware and step > 1:
                    step_score += 2.0
                if references_previous:
                    step_score += 2.0
                if confidence > 0.7:
                    step_score += 1.0
                
                context_scores.append(step_score)
                print(f"    Context aware: {context_aware}, References: {references_previous}, Score: {step_score:.1f}/10")
                
                # Build context
                context.add_operation(
                    operation_type="context_test",
                    tool_name="test_tool",
                    parameters={"input": scenario, "step": step},
                    result=f"Context test step {step}",
                    success=True,
                    context_tags=[f"step_{step}", "context_test"]
                )
            
            avg_context_score = sum(context_scores) / len(context_scores)
            print(f"\n🧠 Context Test Average: {avg_context_score:.1f}/10")
            
            self.save_context_results(context_sequence, context_scores, avg_context_score)
            
            return avg_context_score >= 6.0
            
        except Exception as e:
            print(f"❌ Context test failed: {e}")
            return False
    
    def run_single_scenario_test(self) -> bool:
        """Test a single complex scenario"""
        print("🎯 Testing Single Complex Scenario...")
        
        complex_scenario = "Create a complete Python project structure with src/, tests/, docs/, and all the standard config files. Make it ready for git."
        
        try:
            sys.path.insert(0, os.getcwd())
            from src.ollama.enhanced_interface import get_enhanced_components
            
            context, intent_classifier, tool_selector = get_enhanced_components()[:3]
            
            print(f"  Testing: {complex_scenario}")
            
            # Test classification
            intent, confidence, context_info = intent_classifier.classify_with_context(complex_scenario)
            
            # Test tool selection
            tool_selection = tool_selector.select_tools_with_context(
                intent, complex_scenario, confidence, context_info
            )
            
            # Score the response
            complexity_score = 0.0
            if tool_selection.get('is_multi_step', False):
                complexity_score += 3.0
            if len(tool_selection.get('suggested_parameters', {})) > 0:
                complexity_score += 2.0
            if confidence > 0.7:
                complexity_score += 2.0
            if tool_selection.get('primary_tool') != 'none':
                complexity_score += 2.0
            if tool_selection.get('confidence', 0) > 0.6:
                complexity_score += 1.0
            
            print(f"  Intent: {intent}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Multi-step: {tool_selection.get('is_multi_step', False)}")
            print(f"  Primary tool: {tool_selection.get('primary_tool', 'none')}")
            print(f"  Parameters suggested: {len(tool_selection.get('suggested_parameters', {}))}")
            print(f"  Complexity Score: {complexity_score:.1f}/10")
            
            self.save_single_results(complex_scenario, tool_selection, complexity_score)
            
            return complexity_score >= 6.0
            
        except Exception as e:
            print(f"❌ Single scenario test failed: {e}")
            return False
    
    def run_benchmark_test(self) -> bool:
        """Run performance benchmark"""
        print("⚡ Running Performance Benchmark...")
        
        import time
        
        benchmark_inputs = [
            "create file",
            "list files", 
            "edit config",
            "install package",
            "run tests"
        ]
        
        try:
            sys.path.insert(0, os.getcwd())
            from src.ollama.enhanced_interface import get_enhanced_components
            
            context, intent_classifier, tool_selector = get_enhanced_components()[:3]
            
            times = []
            for test_input in benchmark_inputs:
                start_time = time.time()
                
                intent, confidence, context_info = intent_classifier.classify_with_context(test_input)
                tool_selection = tool_selector.select_tools_with_context(
                    intent, test_input, confidence, context_info
                )
                
                elapsed = time.time() - start_time
                times.append(elapsed)
                print(f"  '{test_input}': {elapsed:.3f}s")
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            print(f"\n⚡ Benchmark Results:")
            print(f"  Average response time: {avg_time:.3f}s")
            print(f"  Maximum response time: {max_time:.3f}s")
            
            performance_good = avg_time < 0.5 and max_time < 1.0
            
            self.save_benchmark_results(benchmark_inputs, times, avg_time, max_time)
            
            return performance_good
            
        except Exception as e:
            print(f"❌ Benchmark test failed: {e}")
            return False
    
    def show_latest_report(self) -> bool:
        """Show the latest test report"""
        print("📊 Latest Test Report...")
        
        try:
            # Find latest result file
            result_files = [f for f in os.listdir(self.test_results_dir) if f.endswith('.json')]
            if not result_files:
                print("No test results found. Run tests first.")
                return False
            
            latest_file = max(result_files, key=lambda f: os.path.getctime(os.path.join(self.test_results_dir, f)))
            filepath = os.path.join(self.test_results_dir, latest_file)
            
            with open(filepath, 'r') as f:
                report = json.load(f)
            
            print(f"\nReport from: {latest_file}")
            print("-" * 40)
            
            if 'summary' in report:
                summary = report['summary']
                print(f"Tests: {summary.get('total_tests', 'N/A')}")
                print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
                print(f"Average Score: {summary.get('average_enhancement_score', 0):.1f}/10")
                print(f"Enhancement Level: {summary.get('enhancement_level', 'Unknown')}")
            else:
                # Quick test format
                print(f"Test Type: {report.get('test_type', 'Unknown')}")
                print(f"Average Score: {report.get('average_score', 0):.1f}/10")
                print(f"Timestamp: {report.get('timestamp', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to show report: {e}")
            return False
    
    def list_available_commands(self) -> bool:
        """List all available test commands"""
        print("📋 Available Test Commands:")
        print("-" * 30)
        print("full      - Run complete automated test suite")
        print("quick     - Run quick validation (3 scenarios)")
        print("context   - Test context awareness specifically")
        print("single    - Test one complex scenario")
        print("benchmark - Run performance benchmark")
        print("report    - Show latest test results")
        print("list      - Show this command list")
        print()
        print("Usage: python tests/quick_test_commands.py <command>")
        return True
    
    def quick_score(self, intent: str, confidence: float, context_factors: int, tool_selection: dict) -> float:
        """Calculate quick score"""
        score = 0.0
        
        if intent != "general":
            score += 2.0
        if confidence > 0.6:
            score += 2.0
        if context_factors > 0:
            score += 2.0
        if tool_selection.get('primary_tool', 'none') != 'none':
            score += 2.0
        if tool_selection.get('confidence', 0) > 0.5:
            score += 2.0
        
        return min(score, 10.0)
    
    def save_quick_results(self, scenarios: list, scores: list, avg_score: float):
        """Save quick test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quick_test_{timestamp}.json"
        filepath = os.path.join(self.test_results_dir, filename)
        
        data = {
            "test_type": "quick_validation",
            "timestamp": datetime.now().isoformat(),
            "scenarios": scenarios,
            "scores": scores,
            "average_score": avg_score,
            "status": "PASS" if avg_score >= 5.0 else "FAIL"
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Quick results saved: {filepath}")
    
    def save_context_results(self, sequence: list, scores: list, avg_score: float):
        """Save context test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"context_test_{timestamp}.json"
        filepath = os.path.join(self.test_results_dir, filename)
        
        data = {
            "test_type": "context_awareness",
            "timestamp": datetime.now().isoformat(),
            "sequence": sequence,
            "scores": scores,
            "average_score": avg_score,
            "status": "PASS" if avg_score >= 6.0 else "FAIL"
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Context results saved: {filepath}")
    
    def save_single_results(self, scenario: str, tool_selection: dict, score: float):
        """Save single scenario results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"single_test_{timestamp}.json"
        filepath = os.path.join(self.test_results_dir, filename)
        
        data = {
            "test_type": "single_complex_scenario",
            "timestamp": datetime.now().isoformat(),
            "scenario": scenario,
            "tool_selection": tool_selection,
            "score": score,
            "status": "PASS" if score >= 6.0 else "FAIL"
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Single test results saved: {filepath}")
    
    def save_benchmark_results(self, inputs: list, times: list, avg_time: float, max_time: float):
        """Save benchmark results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_{timestamp}.json"
        filepath = os.path.join(self.test_results_dir, filename)
        
        data = {
            "test_type": "performance_benchmark",
            "timestamp": datetime.now().isoformat(),
            "inputs": inputs,
            "response_times": times,
            "average_time": avg_time,
            "max_time": max_time,
            "status": "PASS" if avg_time < 0.5 and max_time < 1.0 else "FAIL"
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Benchmark results saved: {filepath}")


def main():
    """Main command runner"""
    if len(sys.argv) != 2:
        print("Usage: python tests/quick_test_commands.py <command>")
        print("Run 'python tests/quick_test_commands.py list' for available commands")
        return False
    
    command = sys.argv[1].lower()
    runner = QuickTestRunner()
    
    print(f"🧪 Running command: {command}")
    print("=" * 40)
    
    success = runner.run_command(command)
    
    if success:
        print(f"\n✅ Command '{command}' completed successfully!")
    else:
        print(f"\n❌ Command '{command}' failed!")
    
    return success


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
