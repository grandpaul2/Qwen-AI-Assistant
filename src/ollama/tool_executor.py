"""
Tool executor for WorkspaceAI

Handles direct tool execution and parameter generation for enhanced tool selection.
"""

import logging
from typing import Dict, Any, Optional, Tuple

from .client import OllamaClient
from .parameter_extractor import ParameterExtractor
from .function_validator import FunctionValidator
from .response_formatter import ResponseFormatter
from ..file_manager import file_manager
from ..utils import generate_install_commands

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools directly without LLM intervention"""
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """Initialize the tool executor"""
        self.client = client or OllamaClient()
        self.parameter_extractor = ParameterExtractor()
        self.function_validator = FunctionValidator()
        self.response_formatter = ResponseFormatter()
    
    def execute_tool_directly(self, selected_tool: str, prompt: str, debug_info: Dict, verbose_output: bool = False) -> Optional[str]:
        """
        Execute a tool directly without LLM parameter generation
        
        Args:
            selected_tool: Name of the tool to execute
            prompt: User's original prompt
            debug_info: Debug information from tool selection
            verbose_output: Whether to show debug information
            
        Returns:
            Formatted execution result
        """
        try:
            if verbose_output:
                print(self.response_formatter.format_debug_info(debug_info))
            
            # Generate parameters from prompt
            parameters = self.parameter_extractor.generate_tool_parameters(selected_tool, prompt)
            
            if not parameters:
                if verbose_output:
                    print(f"⚠️ Could not extract parameters for {selected_tool}, falling back to LLM")
                return None  # Signal fallback to LLM
            
            if verbose_output:
                print(f"🛠️ Executing {selected_tool} with parameters: {parameters}")
            
            # Execute the tool
            result = self._execute_function(selected_tool, parameters)
            
            if result:
                formatted_result = self.response_formatter.format_tool_result(selected_tool, result)
                if verbose_output:
                    print(f"✅ Direct execution successful: {formatted_result}")
                return formatted_result
            else:
                if verbose_output:
                    print(f"❌ Direct execution failed for {selected_tool}")
                return None  # Signal fallback to LLM
                
        except Exception as e:
            logger.error(f"Error in direct tool execution: {e}")
            if verbose_output:
                print(f"❌ Direct execution error: {e}")
            return None  # Signal fallback to LLM
    
    def _execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Optional[str]:
        """
        Execute a specific function with given parameters
        
        Args:
            function_name: Name of the function to execute
            parameters: Parameters for the function
            
        Returns:
            Function result or None if execution failed
        """
        try:
            # Validate and correct function name
            corrected_name, was_corrected = self.function_validator.auto_correct_function_name(function_name)
            
            if was_corrected:
                logger.info(f"Function name corrected: {function_name} -> {corrected_name}")
                # Also correct parameters if needed
                parameters = self.function_validator.auto_correct_parameters(corrected_name, function_name, parameters)
            
            function_name = corrected_name
            
            # Validate parameters
            is_valid, errors = self.function_validator.validate_parameters(function_name, parameters)
            if not is_valid:
                logger.error(f"Invalid parameters for {function_name}: {errors}")
                return None
            
            # Execute file management functions
            if hasattr(file_manager, function_name):
                method = getattr(file_manager, function_name)
                return method(**parameters)
            
            # Handle special cases
            elif function_name == "generate_install_commands":
                software = parameters.get("software", "")
                return generate_install_commands(software)
            
            else:
                logger.error(f"Unknown function: {function_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return None
    
    def validate_tool_execution(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate that a tool can be executed with given parameters
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters for execution
            
        Returns:
            Tuple of (can_execute, error_message)
        """
        # Check if function exists
        if not self.function_validator.validate_function_exists(tool_name):
            suggestions = self.function_validator.suggest_alternative_function(tool_name)
            suggestion_text = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
            return False, f"Unknown function: {tool_name}.{suggestion_text}"
        
        # Validate parameters
        is_valid, errors = self.function_validator.validate_parameters(tool_name, parameters)
        if not is_valid:
            return False, f"Invalid parameters: {'; '.join(errors)}"
        
        return True, ""
    
    def list_available_tools(self) -> Dict[str, Any]:
        """
        Get information about all available tools
        
        Returns:
            Dictionary containing tool information
        """
        return {
            "functions": self.function_validator.list_available_functions(),
            "categories": self.function_validator.get_functions_by_category(),
            "total_count": len(self.function_validator.valid_functions)
        }
    
    def get_tool_help(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get help information for a specific tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool schema and help information
        """
        schema = self.function_validator.get_function_schema(tool_name)
        if not schema:
            return None
        
        return {
            "name": schema["name"],
            "description": schema["description"],
            "parameters": schema.get("parameters", {}),
            "examples": self._get_tool_examples(tool_name)
        }
    
    def _get_tool_examples(self, tool_name: str) -> list[str]:
        """Get usage examples for a tool"""
        examples = {
            "create_file": [
                "Create a file called notes.txt with my todo list",
                "Make a Python script named hello.py",
                "Generate a markdown file for documentation"
            ],
            "write_to_file": [
                "Write content to existing_file.txt",
                "Add this text to my notes"
            ],
            "read_file": [
                "Read the contents of config.json",
                "Show me what's in the readme file"
            ],
            "delete_file": [
                "Delete the temporary.txt file",
                "Remove old_backup.zip"
            ],
            "copy_file": [
                "Copy notes.txt to backup.txt",
                "Duplicate my_script.py as my_script_backup.py"
            ],
            "search_files": [
                "Search for files containing 'project'",
                "Find files with the word 'configuration'"
            ],
            "list_files": [
                "List all files in the directory",
                "Show me what files are here"
            ]
        }
        
        return examples.get(tool_name, [f"Use {tool_name} to perform file operations"])


# Global executor instance for backward compatibility
_default_executor = None

def get_default_executor() -> ToolExecutor:
    """Get or create the default tool executor"""
    global _default_executor
    if _default_executor is None:
        _default_executor = ToolExecutor()
    return _default_executor
