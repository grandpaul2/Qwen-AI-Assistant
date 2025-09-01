#!/usr/bin/env python3
"""
Automated Bot Logic Enhancement Testing

This script runs real-world scenarios through the enhanced bot system
and automatically records performance data and results.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AutomatedBotTester:
    """Automated testing system for bot logic enhancements"""
    
    def __init__(self):
        self.results = []
        self.session_start = datetime.now()
        self.test_session_id = f"auto_test_{int(time.time())}"
        
    def run_automated_tests(self) -> Dict[str, Any]:
        """Run all automated test scenarios and collect data"""
        print("🤖 Automated Bot Logic Enhancement Testing")
        print("=" * 60)
        print(f"Session ID: {self.test_session_id}")
        print(f"Start Time: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Import the enhanced system
        try:
            from src.ollama.enhanced_interface import (
                get_enhanced_components,
                enhanced_context_aware_pipeline,
                get_conversation_stats,
                reset_conversation_context
            )
            print("✅ Enhanced bot system loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load enhanced bot system: {e}")
            return {"error": str(e)}
        
        # Get enhanced components
        components = get_enhanced_components()
        context, intent_classifier, tool_selector = components[:3]
        
        # Test scenarios
        test_scenarios = self.get_automated_test_scenarios()
        
        print(f"\n🧪 Running {len(test_scenarios)} automated test scenarios...")
        print("-" * 60)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n[{i}/{len(test_scenarios)}] Testing: {scenario['name']}")
            result = self.run_single_scenario(scenario, context, intent_classifier, tool_selector)
            self.results.append(result)
            
            # Show quick summary
            enhancement_score = result.get('enhancement_score', 0)
            status = "✅" if enhancement_score >= 7 else "⚠️" if enhancement_score >= 5 else "❌"
            print(f"   {status} Score: {enhancement_score:.1f}/10 | Response time: {result.get('response_time', 0):.3f}s")
        
        # Generate final report
        final_report = self.generate_report()
        self.save_results(final_report)
        
        return final_report
    
    def run_single_scenario(self, scenario: Dict, context, intent_classifier, tool_selector) -> Dict[str, Any]:
        """Run a single test scenario and collect metrics"""
        start_time = time.time()
        
        result = {
            "scenario_name": scenario['name'],
            "scenario_type": scenario['type'],
            "test_input": scenario['input'],
            "timestamp": datetime.now().isoformat(),
            "enhancement_score": 0,
            "metrics": {},
            "enhanced_features": {},
            "errors": []
        }
        
        try:
            if scenario['type'] == 'single':
                result.update(self.test_single_input(scenario, context, intent_classifier, tool_selector))
            elif scenario['type'] == 'sequence':
                result.update(self.test_sequence_input(scenario, context, intent_classifier, tool_selector))
            
        except Exception as e:
            result['errors'].append(f"Test execution error: {str(e)}")
            print(f"   ❌ Error: {e}")
        
        result['response_time'] = time.time() - start_time
        return result
    
    def test_single_input(self, scenario: Dict, context, intent_classifier, tool_selector) -> Dict[str, Any]:
        """Test a single input scenario"""
        user_input = scenario['input']
        
        # Initialize default values
        intent = "general"
        confidence = 0.5
        context_info = {}
        
        # Test enhanced intent classification
        try:
            intent, confidence, context_info = intent_classifier.classify_with_context(user_input)
            
            intent_metrics = {
                "intent": intent,
                "confidence": confidence,
                "context_factors": len(context_info),
                "context_aware": len(context_info) > 0
            }
        except Exception as e:
            intent_metrics = {"error": str(e)}
        
        # Test smart tool selection
        try:
            tool_selection = tool_selector.select_tools_with_context(
                intent, user_input, confidence, context_info
            )
            
            tool_metrics = {
                "primary_tool": tool_selection.get('primary_tool', 'none'),
                "confidence": tool_selection.get('confidence', 0),
                "is_multi_step": tool_selection.get('is_multi_step', False),
                "suggested_parameters": len(tool_selection.get('suggested_parameters', {}))
            }
        except Exception as e:
            tool_metrics = {"error": str(e)}
        
        # Test enhanced pipeline (if available)
        try:
            # Try to import and use enhanced pipeline
            from src.ollama.enhanced_interface import enhanced_context_aware_pipeline
            pipeline_result, debug_info = enhanced_context_aware_pipeline(
                user_input, context, intent_classifier, tool_selector, verbose_output=False
            )
            
            pipeline_metrics = {
                "pipeline_success": True,
                "enhanced_confidence": pipeline_result.get('enhanced_confidence', 0),
                "context_used": len(debug_info.get('context_info', {}))
            }
        except Exception as e:
            pipeline_metrics = {"error": str(e), "pipeline_success": False}
        
        # Calculate enhancement score
        enhancement_score = self.calculate_enhancement_score(
            scenario, intent_metrics, tool_metrics, pipeline_metrics
        )
        
        return {
            "metrics": {
                "intent_classification": intent_metrics,
                "tool_selection": tool_metrics,
                "pipeline": pipeline_metrics
            },
            "enhancement_score": enhancement_score,
            "enhanced_features": self.detect_enhanced_features(intent_metrics, tool_metrics, pipeline_metrics)
        }
    
    def test_sequence_input(self, scenario: Dict, context, intent_classifier, tool_selector) -> Dict[str, Any]:
        """Test a sequence of inputs to validate context building"""
        sequence_results = []
        cumulative_score = 0
        
        for step, user_input in enumerate(scenario['sequence'], 1):
            print(f"     Step {step}: Testing context awareness...")
            
            try:
                # Test context-aware classification
                intent, confidence, context_info = intent_classifier.classify_with_context(user_input)
                
                # Test tool selection with context
                tool_selection = tool_selector.select_tools_with_context(
                    intent, user_input, confidence, context_info
                )
                
                step_result = {
                    "step": step,
                    "input": user_input,
                    "intent": intent,
                    "confidence": confidence,
                    "context_factors": len(context_info),
                    "context_aware": len(context_info) > 0,
                    "references_previous": self.check_context_references(context_info)
                }
                
                sequence_results.append(step_result)
                
                # Simulate operation for context building
                context.add_operation(
                    operation_type="automated_test",
                    tool_name=tool_selection.get('primary_tool', 'test_tool'),
                    parameters={"input": user_input, "step": step},
                    result=f"Test step {step} completed",
                    success=True,
                    context_tags=[f"step_{step}", "automated_test"]
                )
                
                # Score this step
                step_score = self.score_sequence_step(step_result, step)
                cumulative_score += step_score
                
            except Exception as e:
                sequence_results.append({
                    "step": step,
                    "input": user_input,
                    "error": str(e)
                })
        
        avg_score = cumulative_score / len(scenario['sequence']) if scenario['sequence'] else 0
        
        return {
            "metrics": {
                "sequence_steps": len(sequence_results),
                "context_building": self.analyze_context_building(sequence_results),
                "sequence_results": sequence_results
            },
            "enhancement_score": avg_score,
            "enhanced_features": {
                "context_building": any(r.get('context_aware', False) for r in sequence_results),
                "reference_resolution": any(r.get('references_previous', False) for r in sequence_results)
            }
        }
    
    def calculate_enhancement_score(self, scenario: Dict, intent_metrics: Dict, tool_metrics: Dict, pipeline_metrics: Dict) -> float:
        """Calculate overall enhancement score for scenario"""
        score = 0.0
        max_score = 10.0
        
        # Intent classification enhancements (3 points)
        if not intent_metrics.get('error'):
            score += 1.0  # Basic classification works
            if intent_metrics.get('context_aware', False):
                score += 1.0  # Context awareness
            if intent_metrics.get('confidence', 0) > 0.7:
                score += 1.0  # High confidence
        
        # Tool selection enhancements (3 points)
        if not tool_metrics.get('error'):
            score += 1.0  # Basic tool selection works
            if tool_metrics.get('confidence', 0) > 0.7:
                score += 1.0  # High confidence
            if tool_metrics.get('suggested_parameters', 0) > 0:
                score += 1.0  # Smart parameter suggestion
        
        # Pipeline enhancements (2 points)
        if pipeline_metrics.get('pipeline_success', False):
            score += 1.0  # Pipeline works
            if pipeline_metrics.get('context_used', 0) > 0:
                score += 1.0  # Uses context
        
        # Scenario-specific bonuses (2 points)
        scenario_type = scenario.get('expected_enhancements', [])
        if 'context_aware' in scenario_type and intent_metrics.get('context_aware', False):
            score += 1.0
        if 'multi_step' in scenario_type and tool_metrics.get('is_multi_step', False):
            score += 1.0
        
        return min(score, max_score)
    
    def score_sequence_step(self, step_result: Dict, step_number: int) -> float:
        """Score a single step in a sequence"""
        score = 5.0  # Base score
        
        # Context awareness bonus (increases with step number)
        if step_result.get('context_aware', False) and step_number > 1:
            score += 2.0
        
        # Reference resolution bonus
        if step_result.get('references_previous', False):
            score += 2.0
        
        # Confidence bonus
        if step_result.get('confidence', 0) > 0.7:
            score += 1.0
        
        return min(score, 10.0)
    
    def check_context_references(self, context_info: Dict) -> bool:
        """Check if context info indicates references to previous operations"""
        if not context_info:
            return False
        
        # Look for indicators of context awareness
        input_analysis = context_info.get('input_analysis', {})
        return input_analysis.get('references_previous', False)
    
    def analyze_context_building(self, sequence_results: List[Dict]) -> Dict[str, Any]:
        """Analyze how well context builds over the sequence"""
        if not sequence_results:
            return {}
        
        context_progression = []
        for result in sequence_results:
            context_progression.append(result.get('context_factors', 0))
        
        return {
            "context_progression": context_progression,
            "context_improves": len(context_progression) > 1 and context_progression[-1] > context_progression[0],
            "avg_context_factors": sum(context_progression) / len(context_progression),
            "max_context_factors": max(context_progression) if context_progression else 0
        }
    
    def detect_enhanced_features(self, intent_metrics: Dict, tool_metrics: Dict, pipeline_metrics: Dict) -> Dict[str, bool]:
        """Detect which enhanced features are working"""
        return {
            "context_aware_classification": intent_metrics.get('context_aware', False),
            "smart_tool_selection": tool_metrics.get('suggested_parameters', 0) > 0,
            "multi_step_detection": tool_metrics.get('is_multi_step', False),
            "enhanced_pipeline": pipeline_metrics.get('pipeline_success', False),
            "context_utilization": pipeline_metrics.get('context_used', 0) > 0
        }
    
    def get_automated_test_scenarios(self) -> List[Dict[str, Any]]:
        """Get all automated test scenarios"""
        return [
            {
                "name": "Beginner User Guidance",
                "type": "single",
                "input": "Hi, I'm new here. I need to create some files for my Python project but I don't know how this works.",
                "expected_enhancements": ["context_aware", "helpful_tone"],
                "tests": ["conversational_detection", "guidance_provision"]
            },
            {
                "name": "Context Building Sequence",
                "type": "sequence",
                "sequence": [
                    "Create a file called project_notes.md",
                    "Add some content about Python best practices to that file",
                    "Now create a folder structure for my project",
                    "List everything we've created so far"
                ],
                "expected_enhancements": ["context_aware", "reference_resolution"],
                "tests": ["context_accumulation", "file_references"]
            },
            {
                "name": "Frustrated User Detection",
                "type": "single",
                "input": "This isn't working! I tried to edit my config file but it keeps giving me errors. I'm getting really frustrated.",
                "expected_enhancements": ["emotional_detection", "supportive_response"],
                "tests": ["tone_detection", "error_assistance"]
            },
            {
                "name": "Complex Multi-Tool Request",
                "type": "single",
                "input": "Create a complete Python project structure with src/, tests/, docs/, and all the standard config files. Make it ready for git.",
                "expected_enhancements": ["multi_step", "complex_parsing"],
                "tests": ["multi_tool_coordination", "parameter_extraction"]
            },
            {
                "name": "Vague Request Clarification",
                "type": "single",
                "input": "Fix my files",
                "expected_enhancements": ["clarification_seeking", "smart_questions"],
                "tests": ["ambiguity_detection", "helpful_prompting"]
            },
            {
                "name": "File Reference Resolution",
                "type": "sequence",
                "sequence": [
                    "Create a Python script called data_processor.py",
                    "Add error handling to that script",
                    "Create a test file for it",
                    "Show me both files"
                ],
                "expected_enhancements": ["context_aware", "reference_resolution"],
                "tests": ["implicit_references", "file_tracking"]
            },
            {
                "name": "Crisis Mode Support",
                "type": "single",
                "input": "Everything is broken and I don't know what to do. My project is a mess and nothing works. Help!",
                "expected_enhancements": ["emotional_support", "systematic_help"],
                "tests": ["crisis_detection", "calming_response"]
            },
            {
                "name": "Technical User Efficiency",
                "type": "single",
                "input": "Generate install commands for pandas, numpy, and matplotlib, then create a data analysis script template.",
                "expected_enhancements": ["technical_detection", "multi_step"],
                "tests": ["expertise_recognition", "efficient_execution"]
            },
            {
                "name": "Workflow Intelligence",
                "type": "sequence",
                "sequence": [
                    "I want to start a new Python project",
                    "Create the main folders I'll need",
                    "Add a README file with basic information",
                    "Show me what the project structure looks like now"
                ],
                "expected_enhancements": ["workflow_detection", "project_understanding"],
                "tests": ["workflow_pattern", "intelligent_defaults"]
            },
            {
                "name": "Learning Pattern Recognition",
                "type": "sequence",
                "sequence": [
                    "Create a Python module for data processing",
                    "Create another Python module for file handling",
                    "Create one more Python module for configuration"
                ],
                "expected_enhancements": ["pattern_learning", "template_reuse"],
                "tests": ["pattern_detection", "adaptation"]
            }
        ]
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Calculate overall metrics
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if not r.get('errors')])
        avg_score = sum(r.get('enhancement_score', 0) for r in self.results) / total_tests
        avg_response_time = sum(r.get('response_time', 0) for r in self.results) / total_tests
        
        # Feature analysis
        feature_analysis = self.analyze_enhanced_features()
        
        # Performance by category
        category_performance = self.analyze_by_category()
        
        return {
            "test_session": {
                "session_id": self.test_session_id,
                "start_time": self.session_start.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.session_start).total_seconds()
            },
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests * 100,
                "average_enhancement_score": avg_score,
                "average_response_time": avg_response_time,
                "enhancement_level": self.get_enhancement_level(avg_score)
            },
            "feature_analysis": feature_analysis,
            "category_performance": category_performance,
            "detailed_results": self.results,
            "recommendations": self.generate_recommendations(avg_score, feature_analysis)
        }
    
    def analyze_enhanced_features(self) -> Dict[str, Dict]:
        """Analyze which enhanced features are working across all tests"""
        features = {
            "context_aware_classification": [],
            "smart_tool_selection": [],
            "multi_step_detection": [],
            "enhanced_pipeline": [],
            "context_utilization": []
        }
        
        for result in self.results:
            enhanced_features = result.get('enhanced_features', {})
            for feature, working in enhanced_features.items():
                if feature in features:
                    features[feature].append(working)
        
        feature_summary = {}
        for feature, results in features.items():
            if results:
                feature_summary[feature] = {
                    "success_rate": sum(results) / len(results) * 100,
                    "total_tests": len(results),
                    "working": sum(results)
                }
        
        return feature_summary
    
    def analyze_by_category(self) -> Dict[str, Dict]:
        """Analyze performance by test category"""
        categories = {}
        
        for result in self.results:
            scenario_type = result.get('scenario_type', 'unknown')
            if scenario_type not in categories:
                categories[scenario_type] = []
            categories[scenario_type].append(result.get('enhancement_score', 0))
        
        category_summary = {}
        for category, scores in categories.items():
            if scores:
                category_summary[category] = {
                    "average_score": sum(scores) / len(scores),
                    "test_count": len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores)
                }
        
        return category_summary
    
    def get_enhancement_level(self, avg_score: float) -> str:
        """Determine enhancement level based on average score"""
        if avg_score >= 8.0:
            return "Excellent - Full enhancement working"
        elif avg_score >= 6.0:
            return "Good - Most enhancements working"
        elif avg_score >= 4.0:
            return "Partial - Some enhancements working"
        else:
            return "Needs Work - Limited enhancements"
    
    def generate_recommendations(self, avg_score: float, feature_analysis: Dict) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if avg_score < 6.0:
            recommendations.append("Overall enhancement score is low - review core enhancement implementation")
        
        for feature, analysis in feature_analysis.items():
            success_rate = analysis.get('success_rate', 0)
            if success_rate < 50:
                recommendations.append(f"Improve {feature} - only {success_rate:.1f}% success rate")
        
        if not recommendations:
            recommendations.append("Excellent performance! Consider advanced optimization and edge case handling")
        
        return recommendations
    
    def save_results(self, report: Dict[str, Any]) -> str:
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"automated_test_results_{timestamp}.json"
        filepath = os.path.join("test_results", filename)
        
        # Create directory if it doesn't exist
        os.makedirs("test_results", exist_ok=True)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Results saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"\n⚠️ Could not save results: {e}")
            return ""


def main():
    """Main automated testing function"""
    print("🤖 Starting Automated Bot Logic Enhancement Testing...")
    
    tester = AutomatedBotTester()
    report = tester.run_automated_tests()
    
    if "error" in report:
        print(f"\n❌ Testing failed: {report['error']}")
        return False
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 AUTOMATED TESTING SUMMARY")
    print("=" * 60)
    
    summary = report['summary']
    print(f"Tests Run: {summary['total_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Average Enhancement Score: {summary['average_enhancement_score']:.2f}/10")
    print(f"Average Response Time: {summary['average_response_time']:.3f}s")
    print(f"Enhancement Level: {summary['enhancement_level']}")
    
    # Feature analysis
    print(f"\n🔧 Enhanced Features Performance:")
    for feature, analysis in report['feature_analysis'].items():
        success_rate = analysis['success_rate']
        status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
        print(f"  {status} {feature}: {success_rate:.1f}%")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
