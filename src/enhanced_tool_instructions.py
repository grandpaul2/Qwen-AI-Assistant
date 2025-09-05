"""
Enhanced System Instructions for Improved Tool Selection

This module provides improved system prompts and instructions to help
the AI make better tool selection decisions with context awareness.
"""

import os
from typing import List, Dict, Any, Optional

def build_enhanced_tool_instruction() -> str:
    """
    Build enhanced instruction that guides the model to make better tool selections.
    """
    return """You are an AI assistant with access to a powerful universal tool system. Choose tools carefully and strategically.

🎯 TOOL SELECTION STRATEGY:
1. Analyze the user's request to identify the core action needed
2. Choose the most specific tool that matches the primary intent
3. Use appropriate parameters that directly address the request
4. For multi-step tasks, break them into logical tool sequences

🛠️ AVAILABLE TOOLS:

📁 FILE_OPERATIONS - Use for any file/directory tasks
   • Actions: create, read, write, delete, list, copy, move, search, mkdir
   • When to use: User wants to work with files, folders, or file content
   • Examples:
     - "Create a file" → file_operations(action="create", path="filename.txt", content="...")
     - "List files" → file_operations(action="list", path=".")
     - "Read a file" → file_operations(action="read", path="filename.txt")

💻 CODE_INTERPRETER - Use for executing code or system commands  
   • Languages: python, javascript, shell, cmd, powershell
   • When to use: User wants to run code, execute commands, or do programming
   • Examples:
     - "Calculate something" → code_interpreter(language="python", code="print(15 * 23)")
     - "Run a shell command" → code_interpreter(language="shell", code="ls -la")

🧮 CALCULATOR - Use for pure mathematical calculations
   • When to use: Simple math expressions, quick calculations
   • Examples:
     - "What's 2+2?" → calculator(expression="2 + 2")
     - "Calculate 15% of 200" → calculator(expression="200 * 0.15")

🌐 WEB_OPERATIONS - Use for internet-related tasks
   • Actions: http_get, http_post, download, scrape
   • When to use: Fetching web content, downloading files, API calls
   • Examples:
     - "Get data from a URL" → web_operations(action="http_get", url="https://...")
     - "Download a file" → web_operations(action="download", url="https://...")

⚙️ SYSTEM_OPERATIONS - Use for system information and management
   • Actions: info, processes, memory, cpu, disk, network
   • When to use: User wants system stats, process info, resource usage
   • Examples:
     - "Show system info" → system_operations(action="info")
     - "Check memory usage" → system_operations(action="memory")

🎯 SELECTION GUIDELINES:

✅ DO:
- Choose the most specific tool for the task
- Use descriptive action names that match the user's intent
- Include all necessary parameters
- For file operations, always specify the full path
- For code execution, choose the appropriate language

❌ DON'T:
- Use generic tool names when specific ones exist
- Miss required parameters like file paths or content
- Use file_operations for calculations (use calculator instead)
- Use code_interpreter for simple file creation (use file_operations)

🔄 MULTI-STEP TASKS:
If a task requires multiple steps:
1. Break it into logical sequences
2. Use appropriate tools for each step
3. Ensure each step has the information needed from previous steps

📝 EXAMPLES BY INTENT:

User: "Create a Python script that prints hello world"
→ file_operations(action="create", path="hello.py", content="print('Hello World')")

User: "What's the result of 15 * 23?"  
→ calculator(expression="15 * 23")

User: "Show me what files are in this directory"
→ file_operations(action="list", path=".")

User: "Run a Python script to generate fibonacci numbers"
→ code_interpreter(language="python", code="def fib(n): ...")

User: "Create a folder called 'data' and put a JSON file in it"
→ Step 1: file_operations(action="mkdir", path="data")
→ Step 2: file_operations(action="create", path="data/sample.json", content="{...}")

Choose tools that directly accomplish what the user is asking for."""

def get_context_aware_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get enhanced tool schemas with better descriptions and examples.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "file_operations",
                "description": "Perform file and directory operations like create, read, write, delete, list, copy, move, search files and folders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string", 
                            "description": "Operation: create, read, write, delete, list, copy, move, search, mkdir, rmdir",
                            "enum": ["create", "read", "write", "delete", "list", "copy", "move", "search", "mkdir", "rmdir"]
                        },
                        "path": {
                            "type": "string",
                            "description": "File or directory path relative to workspace (required for all operations). Use simple filenames like 'test.txt' or relative paths like 'folder/file.txt'. Do not use absolute paths."
                        },
                        "content": {
                            "type": "string",
                            "description": "Content for create/write operations, or search query for search operations"
                        },
                        "destination": {
                            "type": "string", 
                            "description": "Destination path for copy/move operations"
                        }
                    },
                    "required": ["action", "path"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "code_interpreter",
                "description": "Execute code in various programming languages or run system commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {
                            "type": "string",
                            "description": "Programming language or shell",
                            "enum": ["python", "javascript", "shell", "cmd", "powershell", "bash"]
                        },
                        "code": {
                            "type": "string", 
                            "description": "The code or command to execute"
                        }
                    },
                    "required": ["language", "code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Perform mathematical calculations and evaluate expressions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to calculate (e.g., '2 + 2 * 3', 'sqrt(16)', '15 * 23')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_operations", 
                "description": "Perform web-related operations like HTTP requests, downloads, and web scraping",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Web operation to perform",
                            "enum": ["http_get", "http_post", "download", "scrape", "search"]
                        },
                        "url": {
                            "type": "string",
                            "description": "URL for the web operation"
                        },
                        "data": {
                            "type": "object",
                            "description": "Data for POST requests"
                        },
                        "headers": {
                            "type": "object", 
                            "description": "HTTP headers"
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "system_operations",
                "description": "Get system information and manage system resources",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "System operation to perform",
                            "enum": ["info", "processes", "memory", "cpu", "disk", "network"]
                        },
                        "details": {
                            "type": "string",
                            "description": "Additional details or filters for the operation"
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    ]

def get_context_aware_tool_recommendations(user_message: str, workspace_path: str, 
                                         available_tools: List[Dict], 
                                         conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get context-aware tool recommendations for better selection.
    
    Args:
        user_message: The user's request
        workspace_path: Path to the current workspace
        available_tools: List of available tool schemas
        conversation_history: Previous conversation messages
    
    Returns:
        Dictionary with enhanced recommendations and context
    """
    try:
        # Scan workspace files for context
        workspace_files = []
        project_languages = set()
        
        try:
            if os.path.exists(workspace_path):
                for item in os.listdir(workspace_path):
                    item_path = os.path.join(workspace_path, item)
                    if os.path.isfile(item_path):
                        workspace_files.append(item)
                        # Detect language from file extension
                        if item.endswith('.py'):
                            project_languages.add('Python')
                        elif item.endswith(('.js', '.jsx')):
                            project_languages.add('JavaScript')
                        elif item.endswith(('.ts', '.tsx')):
                            project_languages.add('TypeScript')
                        elif item.endswith('.json'):
                            project_languages.add('JSON')
                        elif item.endswith(('.txt', '.md')):
                            project_languages.add('Text')
        except (PermissionError, OSError):
            # Handle permission errors gracefully
            workspace_files = []
            
        # Simple context analysis
        relevant_tools = []
        for tool in available_tools:
            tool_name = tool['function']['name'].lower()
            if any(keyword in user_message.lower() for keyword in ['file', 'create', 'write']):
                if 'file' in tool_name or 'create' in tool_name or 'write' in tool_name:
                    relevant_tools.append(tool['function']['name'])
            elif any(keyword in user_message.lower() for keyword in ['calculate', 'math', 'compute']):
                if 'calculator' in tool_name or 'math' in tool_name:
                    relevant_tools.append(tool['function']['name'])
            elif any(keyword in user_message.lower() for keyword in ['code', 'python', 'execute']):
                if 'code' in tool_name or 'interpreter' in tool_name:
                    relevant_tools.append(tool['function']['name'])
        
        # Fallback to first few tools if no specific matches
        if not relevant_tools:
            relevant_tools = [tool['function']['name'] for tool in available_tools[:3]]
            
        # Determine project type
        project_type = "unknown"
        if any(f.endswith('.py') for f in workspace_files):
            project_type = "Python project"
        elif any(f.endswith(('.js', '.jsx', '.ts', '.tsx')) for f in workspace_files):
            project_type = "JavaScript/TypeScript project"
        elif any(f.endswith('.json') for f in workspace_files):
            project_type = "Data/Configuration project"
            
        # Generate execution plan for complex messages
        execution_plan = []
        message_lower = user_message.lower()
        
        # Detect multi-step tasks
        if any(indicator in message_lower for indicator in ['1.', '2.', '3.', 'step', 'then', 'after', 'next']):
            # This is a multi-step task, generate execution plan
            step_number = 1
            
            if 'create' in message_lower and ('script' in message_lower or 'file' in message_lower):
                execution_plan.append({
                    'step': step_number,
                    'action': 'create_file',
                    'purpose': 'Create initial file or script',
                    'tools': ['file_operations']
                })
                step_number += 1
                
            if 'read' in message_lower or 'load' in message_lower:
                execution_plan.append({
                    'step': step_number,
                    'action': 'read_data',
                    'purpose': 'Read or load data',
                    'tools': ['file_operations', 'code_interpreter']
                })
                step_number += 1
                
            if 'process' in message_lower or 'calculate' in message_lower or 'statistics' in message_lower:
                execution_plan.append({
                    'step': step_number,
                    'action': 'process_data',
                    'purpose': 'Process data and calculate results',
                    'tools': ['code_interpreter', 'calculator']
                })
                step_number += 1
                
            if 'save' in message_lower and 'result' in message_lower:
                execution_plan.append({
                    'step': step_number,
                    'action': 'save_results',
                    'purpose': 'Save processed results',
                    'tools': ['file_operations']
                })
                step_number += 1
                
            if 'visualization' in message_lower or 'plot' in message_lower or 'chart' in message_lower:
                execution_plan.append({
                    'step': step_number,
                    'action': 'create_visualization',
                    'purpose': 'Generate visualization or chart',
                    'tools': ['code_interpreter']
                })
            
        return {
            'recommended_tools': relevant_tools,
            'context_analysis': {
                'workspace_files': workspace_files,
                'project_context': {
                    'project_type': project_type,
                    'languages': list(project_languages)
                },
                'intent': {
                    'primary_action': 'file_operation' if 'file' in user_message.lower() else 'unknown',
                    'complexity': 'complex' if execution_plan else 'simple',
                    'domain': 'general'
                },
                'fallback': False
            },
            'execution_plan': execution_plan
        }
    except Exception as e:
        # Fallback to basic recommendations if context analysis fails
        return {
            'recommended_tools': [tool['function']['name'] for tool in available_tools[:3]],
            'context_analysis': {
                'error': str(e),
                'fallback': True,
                'workspace_files': []
            },
            'execution_plan': []
        }

def build_context_aware_instruction(user_message: str, workspace_path: str, 
                                   available_tools: List[Dict]) -> str:
    """
    Build a context-aware instruction that includes specific tool recommendations.
    """
    # Get context-aware recommendations
    recommendations = get_context_aware_tool_recommendations(
        user_message, workspace_path, available_tools
    )
    
    base_instruction = build_enhanced_tool_instruction()
    
    # Add workspace context if files are present
    workspace_context = ""
    workspace_files = recommendations['context_analysis'].get('workspace_files', [])
    if workspace_files:
        workspace_context = f"""

WORKSPACE CONTEXT:
Available files in current workspace: {', '.join(workspace_files)}
"""
    else:
        workspace_context = """

WORKSPACE CONTEXT:
Workspace appears to be empty or no files detected.
"""
    
    # Add context-specific guidance
    context_guidance = f"""

CONTEXT-AWARE GUIDANCE FOR THIS REQUEST:

Based on analysis of your request "{user_message}" and the current workspace:
{workspace_context}
Recommended Tools (in priority order):
{', '.join(recommendations['recommended_tools'][:5])}

Intent Analysis:
- Primary Action: {recommendations['context_analysis'].get('intent', {}).get('primary_action', 'unknown')}
- Complexity: {recommendations['context_analysis'].get('intent', {}).get('complexity', 'unknown')}
- Domain: {recommendations['context_analysis'].get('intent', {}).get('domain', 'general')}

Project Context:
- Type: {recommendations['context_analysis'].get('project_context', {}).get('project_type', 'unknown')}
- Languages: {', '.join(recommendations['context_analysis'].get('project_context', {}).get('languages', []))}

Execution Plan:
"""
    
    for step in recommendations.get('execution_plan', []):
        context_guidance += f"  {step['step']}. {step['action'].title()}: {step['purpose']}\n"
        context_guidance += f"     Suggested tools: {', '.join(step['tools'])}\n"
    
    context_guidance += """
Use this analysis to guide your tool selection, but adapt based on the specific details of the request.
"""
    
    return base_instruction + context_guidance
