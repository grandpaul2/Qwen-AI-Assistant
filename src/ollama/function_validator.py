"""
Function validation and auto-correction for WorkspaceAI tools

Validates function names and provides corrections for common mistakes.
"""

import logging
from typing import Dict, List, Tuple, Optional
from difflib import get_close_matches

from ..tool_schemas import get_all_tool_schemas

logger = logging.getLogger(__name__)


class FunctionValidator:
    """Validates and auto-corrects function names and parameters"""
    
    def __init__(self):
        """Initialize the validator with available function schemas"""
        self.schemas = get_all_tool_schemas()
        self.valid_functions = {schema["function"]["name"] for schema in self.schemas}
        
        # Common function name corrections
        self.function_corrections = {
            # Content creation variations
            "create_csv_file": "create_file",
            "create_txt_file": "create_file", 
            "create_md_file": "create_file",
            "create_python_file": "create_file",
            "write_file": "write_to_file",
            "save_file": "create_file",
            "make_file": "create_file",
            "generate_file": "create_file",
            
            # File operations variations
            "backup_file": "copy_file",
            "duplicate_file": "copy_file",
            "clone_file": "copy_file",
            "remove_file": "delete_file",
            "unlink_file": "delete_file",
            "erase_file": "delete_file",
            
            # Search variations
            "find_files": "search_files",
            "locate_files": "search_files",
            "grep_files": "search_files",
            
            # Folder operations
            "make_directory": "create_folder",
            "mkdir": "create_folder",
            "create_dir": "create_folder",
            "new_folder": "create_folder",
            
            # JSON operations
            "create_json_file": "write_json_file",
            "save_json": "write_json_file",
            "make_json": "write_json_file",
            
            # Installation variations
            "install_software": "generate_install_commands",
            "setup_software": "generate_install_commands",
            "install_package": "generate_install_commands",
        }
    
    def validate_function_exists(self, function_name: str) -> bool:
        """
        Check if a function name exists in the available schemas
        
        Args:
            function_name: Name of the function to validate
            
        Returns:
            True if function exists, False otherwise
        """
        return function_name in self.valid_functions
    
    def auto_correct_function_name(self, function_name: str) -> Tuple[str, bool]:
        """
        Auto-correct common function name mistakes
        
        Args:
            function_name: Original function name
            
        Returns:
            Tuple of (corrected_name, was_corrected)
        """
        # First check direct corrections
        if function_name in self.function_corrections:
            corrected = self.function_corrections[function_name]
            logger.info(f"Auto-corrected function name: {function_name} -> {corrected}")
            return corrected, True
        
        # If already valid, return as-is
        if function_name in self.valid_functions:
            return function_name, False
        
        # Try fuzzy matching for typos
        close_matches = get_close_matches(function_name, self.valid_functions, n=1, cutoff=0.6)
        if close_matches:
            corrected = close_matches[0]
            logger.info(f"Fuzzy-matched function name: {function_name} -> {corrected}")
            return corrected, True
        
        # No correction found
        return function_name, False
    
    def suggest_alternative_function(self, function_name: str) -> List[str]:
        """
        Suggest alternative function names for invalid functions
        
        Args:
            function_name: Invalid function name
            
        Returns:
            List of suggested function names
        """
        suggestions = []
        
        # Check for partial matches
        for valid_func in self.valid_functions:
            if any(word in valid_func for word in function_name.split('_')):
                suggestions.append(valid_func)
        
        # If no partial matches, use fuzzy matching
        if not suggestions:
            suggestions = get_close_matches(function_name, self.valid_functions, n=3, cutoff=0.3)
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def auto_correct_parameters(self, function_name: str, original_function: str, function_args: Dict) -> Dict:
        """
        Auto-correct parameter names for known function corrections
        
        Args:
            function_name: Corrected function name
            original_function: Original function name that was corrected
            function_args: Original function arguments
            
        Returns:
            Corrected function arguments
        """
        # Parameter name corrections based on function corrections
        param_corrections = {
            # When correcting to create_file, ensure correct parameter names
            "create_file": {
                "filename": "file_name",
                "text": "content",
                "data": "content",
                "text_content": "content",
                "file_content": "content"
            },
            
            # When correcting to write_to_file
            "write_to_file": {
                "filename": "file_name", 
                "text": "content",
                "data": "content"
            },
            
            # When correcting to copy_file
            "copy_file": {
                "source": "source_file",
                "destination": "target_file",
                "dest": "target_file",
                "target": "target_file"
            },
            
            # When correcting to search_files
            "search_files": {
                "keyword": "search_term",
                "pattern": "search_term",
                "query": "search_term"
            }
        }
        
        if function_name in param_corrections:
            corrections = param_corrections[function_name]
            corrected_args = {}
            
            for key, value in function_args.items():
                corrected_key = corrections.get(key, key)
                corrected_args[corrected_key] = value
                
                if corrected_key != key:
                    logger.info(f"Auto-corrected parameter: {key} -> {corrected_key}")
            
            return corrected_args
        
        return function_args
    
    def validate_parameters(self, function_name: str, parameters: Dict) -> Tuple[bool, List[str]]:
        """
        Validate parameters against function schema
        
        Args:
            function_name: Name of the function
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        # Find the schema for this function
        schema = None
        for s in self.schemas:
            if s["function"]["name"] == function_name:
                schema = s["function"]
                break
        
        if not schema:
            return False, [f"No schema found for function: {function_name}"]
        
        errors = []
        required_params = schema.get("parameters", {}).get("required", [])
        available_params = schema.get("parameters", {}).get("properties", {})
        
        # Check required parameters
        for required_param in required_params:
            if required_param not in parameters:
                errors.append(f"Missing required parameter: {required_param}")
        
        # Check for unknown parameters
        for param_name in parameters:
            if param_name not in available_params:
                errors.append(f"Unknown parameter: {param_name}")
        
        return len(errors) == 0, errors
    
    def get_function_schema(self, function_name: str) -> Optional[Dict]:
        """
        Get the schema for a specific function
        
        Args:
            function_name: Name of the function
            
        Returns:
            Function schema dictionary or None if not found
        """
        for schema in self.schemas:
            if schema["function"]["name"] == function_name:
                return schema["function"]
        return None
    
    def list_available_functions(self) -> List[str]:
        """
        Get list of all available function names
        
        Returns:
            List of function names
        """
        return sorted(list(self.valid_functions))
    
    def get_functions_by_category(self) -> Dict[str, List[str]]:
        """
        Group functions by category for easier discovery
        
        Returns:
            Dictionary mapping categories to function lists
        """
        categories = {
            "File Creation": ["create_file", "write_to_file", "write_json_file", "write_txt_file", "write_md_file"],
            "File Operations": ["read_file", "delete_file", "copy_file", "move_file", "get_file_info"],
            "Directory Operations": ["create_folder", "delete_folder", "copy_folder", "list_files"],
            "Search & Find": ["search_files"],
            "Archive Operations": ["compress_file", "extract_archive"],
            "Software Installation": ["generate_install_commands"]
        }
        
        # Filter to only include functions that actually exist
        filtered_categories = {}
        for category, functions in categories.items():
            existing_functions = [f for f in functions if f in self.valid_functions]
            if existing_functions:
                filtered_categories[category] = existing_functions
        
        return filtered_categories
