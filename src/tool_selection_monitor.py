"""
Tool Selection Monitor for WorkspaceAI

Tracks tool usage patterns, success rates, and provides insights
for improving tool selection accuracy.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class ToolSelectionMonitor:
    """Monitor and analyze tool selection patterns"""
    
    def __init__(self, log_file: str = "tool_selection_log.json"):
        self.log_file = log_file
        self.session_data = []
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical tool usage data"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.historical_data = json.load(f)
            except:
                self.historical_data = []
        else:
            self.historical_data = []
    
    def log_tool_call(self, 
                     user_prompt: str,
                     tool_name: str, 
                     tool_args: Dict,
                     success: bool,
                     execution_time: float,
                     error_message: Optional[str] = None):
        """Log a tool call for analysis"""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_prompt": user_prompt,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "success": success,
            "execution_time": execution_time,
            "error_message": error_message,
            "prompt_length": len(user_prompt),
            "prompt_words": len(user_prompt.split()),
            "session_id": id(self)  # Simple session identifier
        }
        
        self.session_data.append(entry)
        self.historical_data.append(entry)
    
    def save_data(self):
        """Save data to disk"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.historical_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save tool usage data: {e}")
    
    def analyze_tool_usage(self, days: int = 7) -> Dict:
        """Analyze tool usage patterns over the last N days"""
        
        # Filter data by date range
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        recent_data = [
            entry for entry in self.historical_data 
            if datetime.fromisoformat(entry['timestamp']).timestamp() > cutoff_time
        ]
        
        if not recent_data:
            return {"message": "No recent data available"}
        
        # Basic statistics
        total_calls = len(recent_data)
        successful_calls = sum(1 for entry in recent_data if entry['success'])
        success_rate = successful_calls / total_calls if total_calls > 0 else 0
        
        # Tool usage frequency
        tool_counter = Counter(entry['tool_name'] for entry in recent_data)
        
        # Success rates by tool
        tool_success = defaultdict(lambda: {'total': 0, 'successful': 0})
        for entry in recent_data:
            tool = entry['tool_name']
            tool_success[tool]['total'] += 1
            if entry['success']:
                tool_success[tool]['successful'] += 1
        
        # Calculate success rates
        tool_success_rates = {
            tool: stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            for tool, stats in tool_success.items()
        }
        
        # Average execution times
        tool_times = defaultdict(list)
        for entry in recent_data:
            tool_times[entry['tool_name']].append(entry['execution_time'])
        
        avg_execution_times = {
            tool: sum(times) / len(times) if times else 0
            for tool, times in tool_times.items()
        }
        
        # Common failure patterns
        failed_calls = [entry for entry in recent_data if not entry['success']]
        failure_patterns = self._analyze_failure_patterns(failed_calls)
        
        # Prompt analysis
        prompt_analysis = self._analyze_prompts(recent_data)
        
        return {
            "analysis_period_days": days,
            "total_tool_calls": total_calls,
            "overall_success_rate": success_rate,
            "tool_usage_frequency": dict(tool_counter),
            "tool_success_rates": tool_success_rates,
            "average_execution_times": avg_execution_times,
            "failure_patterns": failure_patterns,
            "prompt_analysis": prompt_analysis,
            "recommendations": self._generate_recommendations(tool_success_rates, failure_patterns)
        }
    
    def _analyze_failure_patterns(self, failed_calls: List[Dict]) -> Dict:
        """Analyze patterns in failed tool calls"""
        if not failed_calls:
            return {}
        
        # Common error types
        error_types = Counter()
        for call in failed_calls:
            error_msg = call.get('error_message', 'Unknown error')
            # Categorize errors
            if 'file not found' in error_msg.lower():
                error_types['file_not_found'] += 1
            elif 'permission' in error_msg.lower():
                error_types['permission_error'] += 1
            elif 'invalid' in error_msg.lower():
                error_types['invalid_parameters'] += 1
            elif 'timeout' in error_msg.lower():
                error_types['timeout'] += 1
            else:
                error_types['other'] += 1
        
        # Failed tools
        failed_tools = Counter(call['tool_name'] for call in failed_calls)
        
        # Common failure prompt patterns
        failure_prompt_words = []
        for call in failed_calls:
            failure_prompt_words.extend(call['user_prompt'].lower().split())
        
        common_failure_words = Counter(failure_prompt_words).most_common(10)
        
        return {
            "error_type_distribution": dict(error_types),
            "most_failed_tools": dict(failed_tools),
            "common_words_in_failed_prompts": common_failure_words
        }
    
    def _analyze_prompts(self, data: List[Dict]) -> Dict:
        """Analyze prompt patterns for successful vs failed calls"""
        successful_prompts = [entry['user_prompt'] for entry in data if entry['success']]
        failed_prompts = [entry['user_prompt'] for entry in data if not entry['success']]
        
        # Average prompt lengths
        avg_successful_length = sum(len(p) for p in successful_prompts) / len(successful_prompts) if successful_prompts else 0
        avg_failed_length = sum(len(p) for p in failed_prompts) / len(failed_prompts) if failed_prompts else 0
        
        # Common words in successful prompts
        successful_words = []
        for prompt in successful_prompts:
            successful_words.extend(prompt.lower().split())
        
        common_successful_words = Counter(successful_words).most_common(10)
        
        return {
            "avg_successful_prompt_length": avg_successful_length,
            "avg_failed_prompt_length": avg_failed_length,
            "common_words_in_successful_prompts": common_successful_words,
            "total_successful_prompts": len(successful_prompts),
            "total_failed_prompts": len(failed_prompts)
        }
    
    def _generate_recommendations(self, tool_success_rates: Dict, failure_patterns: Dict) -> List[str]:
        """Generate recommendations for improving tool selection"""
        recommendations = []
        
        # Low success rate tools
        low_success_tools = [
            tool for tool, rate in tool_success_rates.items() 
            if rate < 0.7 and rate > 0  # Exclude tools with 0% (might be new)
        ]
        
        if low_success_tools:
            recommendations.append(
                f"Consider improving instructions for tools with low success rates: {', '.join(low_success_tools)}"
            )
        
        # Common error patterns
        error_dist = failure_patterns.get('error_type_distribution', {})
        if error_dist.get('invalid_parameters', 0) > 5:
            recommendations.append(
                "High rate of invalid parameter errors - consider improving parameter validation and examples"
            )
        
        if error_dist.get('file_not_found', 0) > 3:
            recommendations.append(
                "Multiple file not found errors - consider adding file existence checks or better path guidance"
            )
        
        # Tool usage patterns
        if not recommendations:
            recommendations.append("Tool selection performance looks good - continue current approach")
        
        return recommendations
    
    def get_session_summary(self) -> Dict:
        """Get summary of current session"""
        if not self.session_data:
            return {"message": "No tool calls in current session"}
        
        total_calls = len(self.session_data)
        successful_calls = sum(1 for entry in self.session_data if entry['success'])
        success_rate = successful_calls / total_calls
        
        tool_usage = Counter(entry['tool_name'] for entry in self.session_data)
        avg_execution_time = sum(entry['execution_time'] for entry in self.session_data) / total_calls
        
        return {
            "session_tool_calls": total_calls,
            "session_success_rate": success_rate,
            "session_tool_usage": dict(tool_usage),
            "session_avg_execution_time": avg_execution_time
        }
    
    def print_analysis_report(self, days: int = 7):
        """Print a formatted analysis report"""
        analysis = self.analyze_tool_usage(days)
        
        print("🔍 TOOL SELECTION ANALYSIS REPORT")
        print("=" * 50)
        
        print(f"📊 Period: Last {days} days")
        print(f"📈 Total tool calls: {analysis.get('total_tool_calls', 0)}")
        print(f"✅ Overall success rate: {analysis.get('overall_success_rate', 0):.1%}")
        
        print(f"\n🛠️ Tool Usage Frequency:")
        for tool, count in analysis.get('tool_usage_frequency', {}).items():
            success_rate = analysis.get('tool_success_rates', {}).get(tool, 0)
            avg_time = analysis.get('average_execution_times', {}).get(tool, 0)
            print(f"  {tool}: {count} calls, {success_rate:.1%} success, {avg_time:.2f}s avg")
        
        print(f"\n💡 Recommendations:")
        for rec in analysis.get('recommendations', []):
            print(f"  • {rec}")


# Global monitor instance
monitor = ToolSelectionMonitor()
