"""
Context-Weighted Tool Selector for WorkspaceAI
Handles precise tool selection with numerical confidence scoring
"""

import re
import logging
from typing import Dict, Tuple, Any, Optional

# Import custom exceptions
from .exceptions import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolParameterError,
    WorkspaceAIError,
    handle_exception
)

class ContextWeightedToolSelector:
    """Selects specific tools based on intent and context weighting"""
    
    WEIGHT_SYSTEM = {
        'HIGH_PRIORITY': {
            'words': ['write', 'create', 'make', 'generate', 'build', 'guide', 'file', 'document', 'tutorial', 'documentation'],
            'weight': 10
        },
        'MEDIUM_PRIORITY': {
            'words': ['save', 'store', 'put', 'install', 'setup', 'configure', 'copy', 'move', 'backup'],
            'weight': 5
        },
        'LOW_PRIORITY': {
            'words': ['git', 'python', 'docker', 'node', 'commands', 'steps', 'instructions'],
            'weight': 1
        }
    }
    
    TOOL_MAPPINGS = {
        'CONTENT_CREATION': {
            'default': 'create_file',
            'patterns': {
                r'\bjson\b.*\b(create|write|generate)': 'write_json_file',
                r'\b(create|write|generate).*\bjson': 'write_json_file',
                r'\b(write|create).*\bto\s+file': 'write_to_file',
                r'\bappend.*\bto\s+file': 'write_to_file'
            }
        },
        'SOFTWARE_INSTALLATION': {
            'default': 'generate_install_commands'
        },
        'FILE_MANAGEMENT': {
            'default': 'list_files',
            'patterns': {
                r'\b(read|open|view)\s+.*\bfile': 'read_file',
                r'\b(list|show).*files': 'list_files',
                r'\b(search|find)\s+.*\bfile': 'search_files',
                r'\b(copy|duplicate|backup)\s+.*\bfile': 'copy_file',
                r'\bcopy\s+\w+\.\w+\s+to\s+\w+\.\w+': 'copy_file',
                r'\bmove\s+.*\bfile': 'move_file',
                r'\bmove\s+\w+\.\w+\s+to\s+\w+\.\w+': 'move_file',
                r'\bdelete\s+.*\bfile': 'delete_file',
                r'\bcompress\s+.*\bfile': 'compress_file',
                r'\bextract\s+.*\barchive': 'extract_archive'
            }
        }
    }
    
    # Disambiguation rules for conflicting patterns
    DISAMBIGUATION_RULES = {
        'write_guide_vs_install': {
            'pattern': r'\b(write|create|make)\s+.*\b(guide|tutorial|documentation)\s+.*\b(for|about)\s+\w+',
            'preferred_tool': 'create_file',
            'rule': 'Writing content about software should create files, not installation commands'
        },
        'save_vs_install': {
            'pattern': r'\b(save|store|put)\s+.*\b(guide|content|text)\s+.*\bfile',
            'preferred_tool': 'create_file',
            'rule': 'Saving content to files should use create_file'
        }
    }
    
    def __init__(self):
        """Initialize the tool selector"""
        pass
    
    def calculate_context_weight(self, user_input: str) -> Tuple[int, Dict[str, int]]:
        """
        Calculate weighted confidence scores for the input - backward compatible wrapper
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (total_weight, word_breakdown)
        """
        try:
            return self._calculate_context_weight_with_exceptions(user_input)
        except Exception as e:
            # Log error but return fallback for backward compatibility
            logging.error(f"Context weight calculation failed: {e}")
            print(f"Warning: Context weight calculation error: {str(e)}")
            return 0, {}

    def _calculate_context_weight_with_exceptions(self, user_input: str) -> Tuple[int, Dict[str, int]]:
        """
        Calculate weighted confidence scores for the input - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (total_weight, word_breakdown)
            
        Raises:
            ToolParameterError: For invalid input parameters
            ToolExecutionError: For weight calculation issues
        """
        # Input validation
        if user_input is None:
            error = ToolParameterError("Input cannot be None for weight calculation")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Weight calculation failed: {error}")
            raise error
            
        if not isinstance(user_input, str):
            error = ToolParameterError(f"Input must be a string, got {type(user_input).__name__}")
            error.context["input_type"] = type(user_input).__name__
            error.context["input_value"] = str(user_input)
            logging.error(f"Weight calculation failed: {error}")
            raise error
            
        # Check for extremely long inputs that might cause performance issues
        if len(user_input) > 50000:  # 50KB limit for tool selection
            error = ToolParameterError(f"Input too long: {len(user_input)} characters (max 50000)")
            error.context["input_length"] = len(user_input)
            error.context["max_length"] = 50000
            logging.error(f"Weight calculation failed: {error}")
            raise error

        try:
            total_weight = 0
            word_breakdown = {}
            input_lower = user_input.lower()
            
            for priority, config in self.WEIGHT_SYSTEM.items():
                if not isinstance(config, dict) or 'words' not in config or 'weight' not in config:
                    error = ToolExecutionError(f"Invalid weight system configuration for {priority}")
                    error.context["priority"] = priority
                    error.context["config"] = str(config)
                    logging.error(f"Weight system error: {error}")
                    raise error
                    
                for word in config['words']:
                    if word in input_lower:
                        weight = config['weight']
                        total_weight += weight
                        word_breakdown[word] = weight

            return total_weight, word_breakdown
            
        except (ToolParameterError, ToolExecutionError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("weight_calculation", e)
            converted_error.context["input"] = user_input[:100] if user_input else None
            logging.error(f"Weight calculation failed: {converted_error}")
            raise converted_error
    
    def select_tool(self, intent: str, user_input: str, confidence: float) -> str:
        """
        Select specific tool based on intent and context weighting - backward compatible wrapper
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            
        Returns:
            Selected tool name
        """
        try:
            return self._select_tool_with_exceptions(intent, user_input, confidence)
        except Exception as e:
            # Log error but return fallback for backward compatibility
            logging.error(f"Tool selection failed: {e}")
            print(f"Warning: Tool selection error: {str(e)}")
            return 'create_file'  # Safe default

    def _select_tool_with_exceptions(self, intent: str, user_input: str, confidence: float) -> str:
        """
        Select specific tool based on intent and context weighting - raises exceptions for validation errors
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            
        Returns:
            Selected tool name
            
        Raises:
            ToolParameterError: For invalid input parameters
            ToolNotFoundError: When no suitable tool can be found
            ToolExecutionError: For tool selection issues
        """
        # Input validation
        if intent is None:
            error = ToolParameterError("Intent cannot be None")
            error.context["intent"] = intent
            logging.error(f"Tool selection failed: {error}")
            raise error
            
        if not isinstance(intent, str):
            error = ToolParameterError(f"Intent must be a string, got {type(intent).__name__}")
            error.context["intent_type"] = type(intent).__name__
            error.context["intent_value"] = str(intent)
            logging.error(f"Tool selection failed: {error}")
            raise error
            
        if user_input is None:
            error = ToolParameterError("User input cannot be None")
            error.context["user_input"] = user_input
            logging.error(f"Tool selection failed: {error}")
            raise error
            
        if not isinstance(user_input, str):
            error = ToolParameterError(f"User input must be a string, got {type(user_input).__name__}")
            error.context["input_type"] = type(user_input).__name__
            error.context["input_value"] = str(user_input)
            logging.error(f"Tool selection failed: {error}")
            raise error
            
        if not isinstance(confidence, (int, float)):
            error = ToolParameterError(f"Confidence must be a number, got {type(confidence).__name__}")
            error.context["confidence_type"] = type(confidence).__name__
            error.context["confidence_value"] = str(confidence)
            logging.error(f"Tool selection failed: {error}")
            raise error
            
        if not (0.0 <= confidence <= 1.0):
            error = ToolParameterError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
            error.context["confidence"] = confidence
            logging.error(f"Tool selection failed: {error}")
            raise error

        try:
            input_lower = user_input.lower()
            
            # Apply disambiguation rules first with error handling
            for rule_name, rule_config in self.DISAMBIGUATION_RULES.items():
                try:
                    if re.search(rule_config['pattern'], input_lower):
                        return rule_config['preferred_tool']
                except re.error as e:
                    # Handle regex compilation errors
                    error = ToolExecutionError(f"Invalid regex pattern in disambiguation rule {rule_name}")
                    error.context["rule_name"] = rule_name
                    error.context["pattern"] = rule_config['pattern']
                    error.context["regex_error"] = str(e)
                    logging.error(f"Disambiguation rule error: {error}")
                    raise error

            # Handle low confidence cases
            if confidence < 0.3:
                return self._conservative_selection_with_exceptions(user_input)

            # Select tool based on intent
            if intent == 'CONTENT_CREATION':
                return self._select_content_creation_tool_with_exceptions(user_input)
            elif intent == 'SOFTWARE_INSTALLATION':
                return self._select_installation_tool_with_exceptions(user_input)
            elif intent == 'FILE_MANAGEMENT':
                return self._select_file_management_tool_with_exceptions(user_input)
            elif intent in ['UNCLEAR', 'UNKNOWN']:
                return self._conservative_selection_with_exceptions(user_input)
            else:
                # Unknown intent
                error = ToolNotFoundError(f"No tool mapping found for intent: {intent}")
                error.context["intent"] = intent
                error.context["available_intents"] = list(self.TOOL_MAPPINGS.keys())
                error.context["input"] = user_input[:100]
                logging.warning(f"Unknown intent for tool selection: {error}")
                # Return conservative selection instead of raising
                return self._conservative_selection_with_exceptions(user_input)
                
        except (ToolParameterError, ToolExecutionError, ToolNotFoundError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("tool_selection", e)
            converted_error.context["intent"] = intent
            converted_error.context["input"] = user_input[:100] if user_input else None
            converted_error.context["confidence"] = confidence
            logging.error(f"Tool selection failed: {converted_error}")
            raise converted_error
    
    def _select_content_creation_tool(self, user_input: str) -> str:
        """Select tool for content creation intent - backward compatible wrapper"""
        try:
            return self._select_content_creation_tool_with_exceptions(user_input)
        except Exception as e:
            logging.error(f"Content creation tool selection failed: {e}")
            return self.TOOL_MAPPINGS['CONTENT_CREATION']['default']

    def _select_content_creation_tool_with_exceptions(self, user_input: str) -> str:
        """
        Select tool for content creation intent - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Selected tool name
            
        Raises:
            ToolParameterError: For invalid input parameters
            ToolExecutionError: For tool selection issues
        """
        if user_input is None or not isinstance(user_input, str):
            error = ToolParameterError("Invalid input for content creation tool selection")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Content creation tool selection failed: {error}")
            raise error

        try:
            input_lower = user_input.lower()
            
            # Check for specific patterns with error handling
            for pattern, tool in self.TOOL_MAPPINGS['CONTENT_CREATION']['patterns'].items():
                try:
                    if re.search(pattern, input_lower):
                        return tool
                except re.error as e:
                    # Handle regex compilation errors
                    error = ToolExecutionError(f"Invalid regex pattern in content creation: {pattern}")
                    error.context["pattern"] = pattern
                    error.context["tool"] = tool
                    error.context["regex_error"] = str(e)
                    logging.error(f"Content creation pattern error: {error}")
                    raise error

            return self.TOOL_MAPPINGS['CONTENT_CREATION']['default']
            
        except (ToolParameterError, ToolExecutionError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("content_creation_tool_selection", e)
            converted_error.context["input"] = user_input[:100] if user_input else None
            logging.error(f"Content creation tool selection failed: {converted_error}")
            raise converted_error
    
    def _select_installation_tool(self, user_input: str) -> str:
        """Select tool for software installation intent - backward compatible wrapper"""
        try:
            return self._select_installation_tool_with_exceptions(user_input)
        except Exception as e:
            logging.error(f"Installation tool selection failed: {e}")
            return self.TOOL_MAPPINGS['SOFTWARE_INSTALLATION']['default']

    def _select_installation_tool_with_exceptions(self, user_input: str) -> str:
        """
        Select tool for software installation intent - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Selected tool name
            
        Raises:
            ToolParameterError: For invalid input parameters
        """
        if user_input is None or not isinstance(user_input, str):
            error = ToolParameterError("Invalid input for installation tool selection")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Installation tool selection failed: {error}")
            raise error

        return self.TOOL_MAPPINGS['SOFTWARE_INSTALLATION']['default']
    
    def _select_file_management_tool(self, user_input: str) -> str:
        """Select tool for file management intent - backward compatible wrapper"""
        try:
            return self._select_file_management_tool_with_exceptions(user_input)
        except Exception as e:
            logging.error(f"File management tool selection failed: {e}")
            return self.TOOL_MAPPINGS['FILE_MANAGEMENT']['default']

    def _select_file_management_tool_with_exceptions(self, user_input: str) -> str:
        """
        Select tool for file management intent - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Selected tool name
            
        Raises:
            ToolParameterError: For invalid input parameters
            ToolExecutionError: For tool selection issues
        """
        if user_input is None or not isinstance(user_input, str):
            error = ToolParameterError("Invalid input for file management tool selection")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"File management tool selection failed: {error}")
            raise error

        try:
            input_lower = user_input.lower()
            
            # Check for specific patterns with error handling
            for pattern, tool in self.TOOL_MAPPINGS['FILE_MANAGEMENT']['patterns'].items():
                try:
                    if re.search(pattern, input_lower):
                        return tool
                except re.error as e:
                    # Handle regex compilation errors
                    error = ToolExecutionError(f"Invalid regex pattern in file management: {pattern}")
                    error.context["pattern"] = pattern
                    error.context["tool"] = tool
                    error.context["regex_error"] = str(e)
                    logging.error(f"File management pattern error: {error}")
                    raise error

            return self.TOOL_MAPPINGS['FILE_MANAGEMENT']['default']
            
        except (ToolParameterError, ToolExecutionError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("file_management_tool_selection", e)
            converted_error.context["input"] = user_input[:100] if user_input else None
            logging.error(f"File management tool selection failed: {converted_error}")
            raise converted_error
    
    def _conservative_selection(self, user_input: str) -> str:
        """Conservative tool selection for unclear cases - backward compatible wrapper"""
        try:
            return self._conservative_selection_with_exceptions(user_input)
        except Exception as e:
            logging.error(f"Conservative selection failed: {e}")
            return 'create_file'  # Ultimate fallback

    def _conservative_selection_with_exceptions(self, user_input: str) -> str:
        """
        Conservative tool selection for unclear cases - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Selected tool name
            
        Raises:
            ToolParameterError: For invalid input parameters
        """
        if user_input is None or not isinstance(user_input, str):
            error = ToolParameterError("Invalid input for conservative selection")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Conservative selection failed: {error}")
            raise error

        input_lower = user_input.lower()
        
        # Conservative rules - prefer file creation for most content requests
        if any(word in input_lower for word in ['write', 'create', 'make', 'save', 'generate']):
            return 'create_file'
        elif any(word in input_lower for word in ['read', 'open', 'view']):
            return 'read_file'
        elif any(word in input_lower for word in ['list', 'show']):
            return 'list_files'
        else:
            return 'create_file'  # Default to file creation
    
    def get_selection_details(self, intent: str, user_input: str, confidence: float) -> Dict[str, Any]:
        """
        Get detailed selection breakdown for debugging - backward compatible wrapper
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            
        Returns:
            Dictionary with selection details
        """
        try:
            return self._get_selection_details_with_exceptions(intent, user_input, confidence)
        except Exception as e:
            # Log error and return minimal details for backward compatibility
            logging.error(f"Selection details failed: {e}")
            print(f"Warning: Selection details error: {str(e)}")
            return {
                'input': user_input,
                'intent': intent,
                'confidence': confidence,
                'total_weight': 0,
                'word_breakdown': {},
                'selected_tool': 'create_file',
                'applied_rules': [],
                'selection_method': 'error_fallback',
                'error': str(e)
            }

    def _get_selection_details_with_exceptions(self, intent: str, user_input: str, confidence: float) -> Dict[str, Any]:
        """
        Get detailed selection breakdown for debugging - raises exceptions for validation errors
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            
        Returns:
            Dictionary with selection details
            
        Raises:
            ToolParameterError: For invalid input parameters
            ToolExecutionError: For selection detail issues
        """
        try:
            total_weight, word_breakdown = self._calculate_context_weight_with_exceptions(user_input)
        except Exception as e:
            logging.warning(f"Weight calculation failed in details: {e}")
            total_weight, word_breakdown = 0, {}
            
        try:
            selected_tool = self._select_tool_with_exceptions(intent, user_input, confidence)
        except Exception as e:
            logging.warning(f"Tool selection failed in details: {e}")
            selected_tool = 'create_file'

        # Check which rules were applied with error handling
        applied_rules = []
        if user_input and isinstance(user_input, str):
            input_lower = user_input.lower()
            
            for rule_name, rule_config in self.DISAMBIGUATION_RULES.items():
                try:
                    if re.search(rule_config['pattern'], input_lower):
                        applied_rules.append({
                            'rule': rule_name,
                            'pattern': rule_config['pattern'],
                            'preferred_tool': rule_config['preferred_tool'],
                            'explanation': rule_config['rule']
                        })
                except re.error as e:
                    # Log regex errors but continue
                    logging.warning(f"Regex error in rule {rule_name}: {e}")
                    continue

        return {
            'input': user_input,
            'intent': intent,
            'confidence': confidence,
            'total_weight': total_weight,
            'word_breakdown': word_breakdown,
            'selected_tool': selected_tool,
            'applied_rules': applied_rules,
            'selection_method': self._get_selection_method(intent, confidence)
        }
    
    def _get_selection_method(self, intent: str, confidence: float) -> str:
        """Determine which selection method was used"""
        if confidence < 0.3:
            return 'conservative_selection'
        elif intent in self.TOOL_MAPPINGS:
            return f'{intent.lower()}_patterns'
        else:
            return 'fallback'


# Convenience function for quick tool selection
def select_tool_for_intent(intent: str, user_input: str, confidence: float) -> str:
    """
    Quick function to select tool - backward compatible wrapper
    
    Args:
        intent: The classified intent
        user_input: The user's input string
        confidence: Confidence score
        
    Returns:
        Selected tool name
    """
    try:
        return select_tool_for_intent_with_exceptions(intent, user_input, confidence)
    except Exception as e:
        # Log error but return fallback for backward compatibility
        logging.error(f"Tool selection failed: {e}")
        print(f"Warning: Tool selection error: {str(e)}")
        return 'create_file'

def select_tool_for_intent_with_exceptions(intent: str, user_input: str, confidence: float) -> str:
    """
    Quick function to select tool - raises exceptions for validation errors
    
    Args:
        intent: The classified intent
        user_input: The user's input string
        confidence: Confidence score
        
    Returns:
        Selected tool name
        
    Raises:
        ToolParameterError: For invalid input parameters
        ToolExecutionError: For tool selection issues
        ToolNotFoundError: When no suitable tool can be found
    """
    selector = ContextWeightedToolSelector()
    return selector._select_tool_with_exceptions(intent, user_input, confidence)


# Test the selector
if __name__ == "__main__":
    selector = ContextWeightedToolSelector()
    
    test_cases = [
        ("CONTENT_CREATION", "write me a guide for git", 0.85),
        ("SOFTWARE_INSTALLATION", "install git on ubuntu", 0.90),
        ("FILE_MANAGEMENT", "copy main.py to backup.py", 0.80),
        ("CONTENT_CREATION", "create documentation about docker", 0.75)
    ]
    
    for intent, input_text, confidence in test_cases:
        details = selector.get_selection_details(intent, input_text, confidence)
        print(f"\nInput: '{input_text}'")
        print(f"Intent: {intent} (confidence: {confidence:.2f})")
        print(f"Weight: {details['total_weight']} {details['word_breakdown']}")
        print(f"Selected: {details['selected_tool']}")
        if details['applied_rules']:
            print(f"Rules applied: {[r['rule'] for r in details['applied_rules']]}")
