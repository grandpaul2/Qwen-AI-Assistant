#!/usr/bin/env python3
"""
Real-World Bot Testing Interface

This script provides an interactive way to test the enhanced bot logic
with real-world scenarios through the actual chat interface.
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BotTester:
    """Interactive bot testing interface"""
    
    def __init__(self):
        self.test_results = []
        self.session_start = datetime.now()
    
    def run_interactive_test(self):
        """Run interactive testing session"""
        print("🤖 Enhanced Bot Logic - Real World Testing")
        print("=" * 50)
        print("This will test your bot through realistic user scenarios.")
        print("You'll see what a real user might type, then you can test it yourself.\n")
        
        scenarios = self.get_test_scenarios()
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 Test Scenario {i}: {scenario['name']}")
            print(f"👤 User Type: {scenario['user_type']}")
            print(f"🎯 Tests: {', '.join(scenario['tests'])}")
            print("-" * 40)
            
            if scenario.get('sequence'):
                print("📝 Multi-step scenario - Use these in order:")
                for step, input_text in enumerate(scenario['sequence'], 1):
                    print(f"   {step}. \"{input_text}\"")
            else:
                print(f"💬 Try this input: \"{scenario['input']}\"")
            
            print(f"\n🔍 Look for: {scenario['expected']}")
            
            # Wait for user to test
            response = input("\n⏩ Press Enter after testing (or 'skip' to skip): ").strip().lower()
            if response == 'skip':
                continue
            
            # Get feedback
            self.collect_feedback(scenario['name'])
        
        self.show_results()
    
    def get_test_scenarios(self):
        """Get all test scenarios"""
        return [
            {
                "name": "Beginner User",
                "user_type": "First-time user, unfamiliar with system",
                "input": "Hi, I'm new here. I need to create some files for my Python project but I don't know how this works.",
                "tests": ["Conversational tone", "Beginner guidance", "Proactive help"],
                "expected": "Friendly tone, helpful suggestions, context building"
            },
            {
                "name": "Context Building",
                "user_type": "Progressive workflow user",
                "sequence": [
                    "Create a file called project_notes.md",
                    "Add some content about Python best practices to that file",
                    "Now create a folder structure for my project",
                    "List everything we've created so far"
                ],
                "tests": ["Context awareness", "File references", "Session memory"],
                "expected": "References previous files, builds context over time"
            },
            {
                "name": "Frustrated User",
                "user_type": "Encountered problems, needs help",
                "input": "This isn't working! I tried to edit my config file but it keeps giving me errors. I'm getting really frustrated.",
                "tests": ["Emotional detection", "Empathetic response", "Error help"],
                "expected": "Calming tone, troubleshooting help, emotional support"
            },
            {
                "name": "Power User",
                "user_type": "Experienced, wants efficiency",
                "input": "Create a complete Python project structure with src/, tests/, docs/, and all the standard config files. Make it ready for git.",
                "tests": ["Complex requests", "Multi-tool coordination", "Efficiency"],
                "expected": "Handles complexity, efficient execution, professional output"
            },
            {
                "name": "Vague Request",
                "user_type": "Unclear about requirements",
                "input": "Fix my files",
                "tests": ["Clarification", "Smart questions", "Problem solving"],
                "expected": "Asks clarifying questions, provides smart suggestions"
            },
            {
                "name": "File References",
                "user_type": "Implicit file reference user",
                "sequence": [
                    "Create a Python script called data_processor.py",
                    "Add error handling to that script",
                    "Create a test file for it",
                    "Show me both files"
                ],
                "tests": ["Implicit references", "Context resolution", "File tracking"],
                "expected": "Understands 'that script', 'it', 'both files' references"
            },
            {
                "name": "Crisis Mode",
                "user_type": "Overwhelmed user needing support",
                "input": "Everything is broken and I don't know what to do. My project is a mess and nothing works. Help!",
                "tests": ["Crisis response", "Systematic help", "Emotional support"],
                "expected": "Calm response, breaks down problems, systematic assistance"
            },
            {
                "name": "Workflow Intelligence",
                "user_type": "Project setup workflow",
                "sequence": [
                    "I want to start a new Python project",
                    "Create the main folders I'll need",
                    "Add a README file with basic information",
                    "Show me what the project structure looks like now"
                ],
                "tests": ["Workflow detection", "Smart defaults", "Project understanding"],
                "expected": "Understands project context, suggests appropriate structure"
            }
        ]
    
    def collect_feedback(self, scenario_name):
        """Collect user feedback on test results"""
        print(f"\n📊 How did the bot perform for '{scenario_name}'?")
        
        # Context awareness
        context_aware = input("🧠 Context awareness (0-10): ").strip()
        conversational = input("💬 Conversational tone (0-10): ").strip()
        helpful = input("🤝 Helpfulness (0-10): ").strip()
        
        try:
            context_score = int(context_aware) if context_aware.isdigit() else 5
            conv_score = int(conversational) if conversational.isdigit() else 5
            help_score = int(helpful) if helpful.isdigit() else 5
        except:
            context_score = conv_score = help_score = 5
        
        overall = (context_score + conv_score + help_score) / 3
        
        self.test_results.append({
            "scenario": scenario_name,
            "context_awareness": context_score,
            "conversational": conv_score,
            "helpfulness": help_score,
            "overall": overall
        })
        
        print(f"✅ Recorded: {overall:.1f}/10 overall")
    
    def show_results(self):
        """Show final test results"""
        print("\n" + "=" * 50)
        print("🎯 TESTING RESULTS SUMMARY")
        print("=" * 50)
        
        if not self.test_results:
            print("No tests completed.")
            return
        
        total_context = sum(r["context_awareness"] for r in self.test_results)
        total_conv = sum(r["conversational"] for r in self.test_results)
        total_help = sum(r["helpfulness"] for r in self.test_results)
        total_overall = sum(r["overall"] for r in self.test_results)
        count = len(self.test_results)
        
        print(f"📊 Test Results ({count} scenarios):")
        print("-" * 30)
        for result in self.test_results:
            print(f"{result['scenario']:<20} {result['overall']:.1f}/10")
        
        print("\n📈 Average Scores:")
        print(f"🧠 Context Awareness: {total_context/count:.1f}/10")
        print(f"💬 Conversational:    {total_conv/count:.1f}/10")
        print(f"🤝 Helpfulness:       {total_help/count:.1f}/10")
        print(f"🎯 Overall:           {total_overall/count:.1f}/10")
        
        # Enhancement assessment
        avg_score = total_overall / count
        if avg_score >= 8:
            print("\n🌟 EXCELLENT: Enhanced bot logic is working very well!")
        elif avg_score >= 6:
            print("\n✅ GOOD: Enhanced features are working, room for improvement")
        elif avg_score >= 4:
            print("\n⚠️  PARTIAL: Some enhancements working, needs development")
        else:
            print("\n❌ NEEDS WORK: Enhanced features need significant improvement")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(f"Bot Enhancement Test Results - {timestamp}\n")
                f.write("=" * 50 + "\n\n")
                for result in self.test_results:
                    f.write(f"{result['scenario']}: {result['overall']:.1f}/10\n")
                f.write(f"\nOverall Average: {total_overall/count:.1f}/10\n")
            print(f"\n💾 Results saved to: {filename}")
        except:
            print("\n⚠️ Could not save results file")


def main():
    """Main testing interface"""
    print("🧪 Real-World Bot Testing")
    print("This will help you test the enhanced bot logic with realistic scenarios.\n")
    
    choice = input("Choose testing mode:\n1. Interactive testing\n2. Show scenarios only\n\nChoice (1-2): ").strip()
    
    tester = BotTester()
    
    if choice == "2":
        scenarios = tester.get_test_scenarios()
        print("\n📋 All Test Scenarios:")
        print("=" * 30)
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. {scenario['name']}")
            if scenario.get('sequence'):
                for step, text in enumerate(scenario['sequence'], 1):
                    print(f"   {step}. \"{text}\"")
            else:
                print(f"   \"{scenario['input']}\"")
    else:
        tester.run_interactive_test()


if __name__ == "__main__":
    main()
