"""
Context-Aware Tool Selection Module

This module analyzes the current workspace context, conversation history, and user intent
to provide more intelligent tool selection recommendations.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re

class ContextAnalyzer:
    """Analyzes workspace and conversation context for better tool selection."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.file_cache = {}
        self.project_context = self._analyze_project_type()
    
    def _analyze_project_type(self) -> Dict[str, Any]:
        """Analyze the project type and characteristics."""
        context = {
            'languages': set(),
            'frameworks': set(),
            'project_type': 'unknown',
            'has_tests': False,
            'has_docs': False,
            'has_config': False,
            'file_count': 0,
            'main_files': []
        }
        
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                context['file_count'] += len(files)
                
                for file in files:
                    file_path = Path(root) / file
                    ext = file_path.suffix.lower()
                    
                    # Language detection
                    if ext in ['.py']:
                        context['languages'].add('python')
                    elif ext in ['.js', '.ts']:
                        context['languages'].add('javascript/typescript')
                    elif ext in ['.java']:
                        context['languages'].add('java')
                    elif ext in ['.cpp', '.c', '.h']:
                        context['languages'].add('c/cpp')
                    
                    # Framework detection
                    if file in ['package.json', 'yarn.lock']:
                        context['frameworks'].add('node.js')
                    elif file in ['requirements.txt', 'setup.py', 'pyproject.toml']:
                        context['frameworks'].add('python-project')
                    elif file in ['pom.xml', 'build.gradle']:
                        context['frameworks'].add('java-project')
                    
                    # Project characteristics
                    if 'test' in file.lower() or 'test' in root.lower():
                        context['has_tests'] = True
                    if 'doc' in file.lower() or 'readme' in file.lower():
                        context['has_docs'] = True
                    if file in ['config.json', '.env', 'settings.py']:
                        context['has_config'] = True
                    if file in ['main.py', 'app.py', 'index.js', 'main.js']:
                        context['main_files'].append(str(file_path))
        
        except Exception as e:
            print(f"Error analyzing project: {e}")
        
        # Determine project type
        if 'python-project' in context['frameworks']:
            context['project_type'] = 'python'
        elif 'node.js' in context['frameworks']:
            context['project_type'] = 'javascript'
        elif 'java-project' in context['frameworks']:
            context['project_type'] = 'java'
        
        return context
    
    def analyze_user_intent(self, user_message: str, conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze user intent from message and conversation context."""
        intent = {
            'primary_action': 'unknown',
            'target_files': [],
            'requires_execution': False,
            'requires_analysis': False,
            'requires_creation': False,
            'complexity': 'simple',
            'domain': 'general'
        }
        
        message_lower = user_message.lower()
        
        # Primary action detection
        if any(word in message_lower for word in ['create', 'make', 'build', 'generate']):
            intent['primary_action'] = 'create'
            intent['requires_creation'] = True
        elif any(word in message_lower for word in ['run', 'execute', 'test', 'compile']):
            intent['primary_action'] = 'execute'
            intent['requires_execution'] = True
        elif any(word in message_lower for word in ['read', 'show', 'display', 'view', 'check']):
            intent['primary_action'] = 'read'
            intent['requires_analysis'] = True
        elif any(word in message_lower for word in ['edit', 'modify', 'change', 'update', 'fix']):
            intent['primary_action'] = 'modify'
            intent['requires_analysis'] = True
        elif any(word in message_lower for word in ['search', 'find', 'locate']):
            intent['primary_action'] = 'search'
            intent['requires_analysis'] = True
        
        # File detection
        file_patterns = re.findall(r'[\w/\\.-]+\.[a-zA-Z]{1,4}', user_message)
        intent['target_files'] = file_patterns
        
        # Complexity assessment
        complexity_indicators = {
            'simple': ['show', 'display', 'read', 'view'],
            'medium': ['create', 'modify', 'test', 'run'],
            'complex': ['analyze', 'implement', 'integrate', 'optimize', 'debug']
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                intent['complexity'] = complexity
                break
        
        # Domain detection
        if any(word in message_lower for word in ['test', 'testing', 'unittest']):
            intent['domain'] = 'testing'
        elif any(word in message_lower for word in ['api', 'web', 'http', 'request']):
            intent['domain'] = 'web'
        elif any(word in message_lower for word in ['data', 'csv', 'json', 'database']):
            intent['domain'] = 'data'
        elif any(word in message_lower for word in ['config', 'settings', 'environment']):
            intent['domain'] = 'configuration'
        
        return intent
    
    def get_relevant_context(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant workspace context based on user intent."""
        context = {
            'suggested_tools': [],
            'relevant_files': [],
            'execution_context': {},
            'constraints': []
        }
        
        # Tool suggestions based on intent and project context
        if intent['primary_action'] == 'create':
            if intent['domain'] == 'testing':
                context['suggested_tools'] = ['create_file', 'run_command']
            else:
                context['suggested_tools'] = ['create_file', 'create_directory']
        
        elif intent['primary_action'] == 'execute':
            if 'python' in self.project_context['languages']:
                context['suggested_tools'] = ['run_command', 'execute_code']
                context['execution_context'] = {
                    'interpreter': 'python',
                    'main_files': self.project_context['main_files']
                }
            else:
                context['suggested_tools'] = ['run_command']
        
        elif intent['primary_action'] == 'read':
            context['suggested_tools'] = ['read_file', 'list_files']
            
        elif intent['primary_action'] == 'search':
            context['suggested_tools'] = ['search_files', 'grep_search']
            
        elif intent['primary_action'] == 'modify':
            context['suggested_tools'] = ['read_file', 'write_file']
        
        # Add file constraints
        if intent['target_files']:
            context['constraints'].append(f"Target files: {', '.join(intent['target_files'])}")
        
        # Add complexity-based suggestions
        if intent['complexity'] == 'complex':
            context['suggested_tools'].extend(['search_files', 'list_files'])
            context['constraints'].append("Complex task - may require multiple tools")
        
        return context

class ContextAwareToolSelector:
    """Enhanced tool selector that uses context awareness."""
    
    def __init__(self, workspace_path: str):
        self.context_analyzer = ContextAnalyzer(workspace_path)
        self.tool_usage_history = []
    
    def select_tools_with_context(self, user_message: str, available_tools: List[Dict], 
                                conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """Select tools using context awareness."""
        
        # Analyze intent and context
        intent = self.context_analyzer.analyze_user_intent(user_message, conversation_history)
        context = self.context_analyzer.get_relevant_context(intent)
        
        # Score tools based on context
        tool_scores = {}
        for tool in available_tools:
            tool_name = tool['function']['name']
            score = self._score_tool_for_context(tool, intent, context)
            tool_scores[tool_name] = score
        
        # Sort tools by score
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare enhanced selection result
        result = {
            'recommended_tools': [tool[0] for tool in sorted_tools[:5]],
            'tool_scores': dict(sorted_tools),
            'context_analysis': {
                'intent': intent,
                'project_context': self.context_analyzer.project_context,
                'suggestions': context['suggested_tools'],
                'constraints': context['constraints']
            },
            'execution_plan': self._create_execution_plan(intent, context, sorted_tools[:3])
        }
        
        return result
    
    def _score_tool_for_context(self, tool: Dict, intent: Dict, context: Dict) -> float:
        """Score a tool based on how well it fits the current context."""
        tool_name = tool['function']['name']
        score = 0.0
        
        # Base score from suggested tools
        if tool_name in context['suggested_tools']:
            score += 10.0
        
        # Intent-based scoring
        if intent['primary_action'] == 'create':
            if 'create' in tool_name or 'write' in tool_name:
                score += 8.0
        elif intent['primary_action'] == 'execute':
            if 'run' in tool_name or 'execute' in tool_name or 'command' in tool_name:
                score += 8.0
        elif intent['primary_action'] == 'read':
            if 'read' in tool_name or 'list' in tool_name or 'show' in tool_name:
                score += 8.0
        elif intent['primary_action'] == 'search':
            if 'search' in tool_name or 'find' in tool_name or 'grep' in tool_name:
                score += 8.0
        elif intent['primary_action'] == 'modify':
            if 'write' in tool_name or 'edit' in tool_name or 'modify' in tool_name:
                score += 8.0
        
        # Domain-specific scoring
        if intent['domain'] == 'web' and 'web' in tool_name:
            score += 5.0
        elif intent['domain'] == 'testing' and 'test' in tool_name:
            score += 5.0
        elif intent['domain'] == 'data' and ('json' in tool_name or 'csv' in tool_name):
            score += 5.0
        
        # Complexity-based scoring
        if intent['complexity'] == 'complex':
            if 'search' in tool_name or 'analyze' in tool_name:
                score += 3.0
        
        # Project context scoring
        project_type = self.context_analyzer.project_context['project_type']
        if project_type == 'python' and 'python' in tool_name:
            score += 3.0
        
        # File-specific scoring
        if intent['target_files']:
            if any('file' in tool_name for _ in intent['target_files']):
                score += 2.0
        
        return score
    
    def _create_execution_plan(self, intent: Dict, context: Dict, top_tools: List[Tuple]) -> List[Dict]:
        """Create a suggested execution plan based on context."""
        plan = []
        
        if intent['complexity'] == 'complex':
            # For complex tasks, suggest exploration first
            plan.append({
                'step': 1,
                'action': 'explore',
                'tools': ['search_files', 'list_files'],
                'purpose': 'Understand the workspace structure'
            })
            
            plan.append({
                'step': 2,
                'action': 'analyze',
                'tools': ['read_file'],
                'purpose': 'Read relevant files for context'
            })
            
            plan.append({
                'step': 3,
                'action': 'execute',
                'tools': [tool[0] for tool in top_tools[:2]],
                'purpose': 'Perform the main task'
            })
        
        else:
            # For simple tasks, direct execution
            plan.append({
                'step': 1,
                'action': 'execute',
                'tools': [tool[0] for tool in top_tools[:2]],
                'purpose': f'Perform {intent["primary_action"]} operation'
            })
        
        return plan

def enhance_tool_selection_with_context(workspace_path: str, user_message: str, 
                                      available_tools: List[Dict], 
                                      conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Main function to enhance tool selection with context awareness.
    
    Args:
        workspace_path: Path to the current workspace
        user_message: The user's request
        available_tools: List of available tool schemas
        conversation_history: Previous conversation messages
    
    Returns:
        Dictionary with enhanced tool selection and context analysis
    """
    selector = ContextAwareToolSelector(workspace_path)
    return selector.select_tools_with_context(user_message, available_tools, conversation_history)

# Example usage and testing
if __name__ == "__main__":
    # Test with the current workspace
    workspace = "c:\\Users\\Grandpaul\\Desktop\\AI Work\\WorkspaceAI_project"
    
    # Mock some available tools for testing
    mock_tools = [
        {"function": {"name": "create_file", "description": "Create a new file"}},
        {"function": {"name": "read_file", "description": "Read file contents"}},
        {"function": {"name": "run_command", "description": "Execute system command"}},
        {"function": {"name": "search_files", "description": "Search for files"}},
        {"function": {"name": "write_file", "description": "Write to a file"}},
    ]
    
    # Test different scenarios
    test_scenarios = [
        "Create a new test file for the main.py module",
        "Run the main application and show me the output",
        "Find all Python files in the project",
        "Debug the error in the tool selection system"
    ]
    
    for scenario in test_scenarios:
        print(f"\n=== Testing: {scenario} ===")
        result = enhance_tool_selection_with_context(workspace, scenario, mock_tools)
        print(f"Recommended tools: {result['recommended_tools'][:3]}")
        print(f"Intent: {result['context_analysis']['intent']['primary_action']}")
        print(f"Complexity: {result['context_analysis']['intent']['complexity']}")
