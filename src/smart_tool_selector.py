"""
Smart Tool Selector for WorkspaceAI
Context-aware tool selection with planning capabilities for multi-step operations
"""

import re
import logging
from typing import Dict, Tuple, Any, Optional, List

from .tool_selector import ContextWeightedToolSelector
from .context_manager import ConversationContext, get_conversation_context
from .exceptions import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolParameterError,
    WorkspaceAIError,
    handle_exception
)

logger = logging.getLogger(__name__)


class SmartToolSelector(ContextWeightedToolSelector):
    """
    Context-aware tool selector that considers conversation history,
    user patterns, and can plan multi-step operations.
    """
    
    # Enhanced tool mappings with context consideration
    CONTEXTUAL_TOOL_MAPPINGS = {
        'CONTENT_CREATION': {
            'default': 'create_file',
            'patterns': {
                # Standard patterns from base class
                r'\bjson\b.*\b(create|write|generate)': 'write_json_file',
                r'\b(create|write|generate).*\bjson': 'write_json_file',
                r'\b(write|create).*\bto\s+file': 'write_to_file',
                
                # Context-aware patterns
                r'\bappend.*\bto\s+(the|that|this)\s+(file|document)': 'write_to_file',
                r'\badd.*\bto\s+(the|that|this)\s+(file|document)': 'write_to_file',
                r'\bupdate\s+(the|that|this)\s+(file|document)': 'write_to_file',
            }
        },
        
        'CONTENT_CONTINUATION': {
            'default': 'write_to_file',  # Assume continuation means appending
            'patterns': {
                r'\bappend': 'write_to_file',
                r'\badd\s+to': 'write_to_file',
                r'\bextend': 'write_to_file',
                r'\bcontinue\s+with': 'write_to_file',
            }
        },
        
        'FILE_REFERENCE': {
            'default': 'read_file',  # When referencing files, often want to read them
            'patterns': {
                r'\bshow\s+(me\s+)?(the|that|this)\s+(file|document)': 'read_file',
                r'\bread\s+(the|that|this)\s+(file|document)': 'read_file',
                r'\bopen\s+(the|that|this)\s+(file|document)': 'read_file',
                r'\bview\s+(the|that|this)\s+(file|document)': 'read_file',
            }
        },
        
        'PROJECT_MANAGEMENT': {
            'default': 'create_folder',  # Projects often start with folder creation
            'patterns': {
                r'\bproject\s+structure': 'create_folder',
                r'\bfolder\s+structure': 'create_folder',
                r'\bworkspace\s+setup': 'create_folder',
                r'\borganize\s+files': 'list_files',
            }
        },
        
        'SOFTWARE_INSTALLATION': {
            'default': 'generate_install_commands'
        },
        
        'FILE_MANAGEMENT': {
            'default': 'list_files',
            'patterns': {
                # Standard patterns from base class
                r'\b(read|open|view)\s+.*\bfile': 'read_file',
                r'\b(list|show).*files': 'list_files',
                r'\b(search|find)\s+.*\bfile': 'search_files',
                r'\b(copy|duplicate|backup)\s+.*\bfile': 'copy_file',
                r'\bmove\s+.*\bfile': 'move_file',
                r'\bdelete\s+.*\bfile': 'delete_file',
                
                # Context-aware patterns
                r'\b(the|that|this)\s+(file|document)\s+.*\b(read|open|view)': 'read_file',
                r'\b(the|that|this)\s+(file|document)\s+.*\b(copy|duplicate)': 'copy_file',
                r'\b(the|that|this)\s+(file|document)\s+.*\bmove': 'move_file',
            }
        }
    }
    
    # Multi-step operation plans
    MULTI_STEP_PLANS = {
        'CREATE_PROJECT_STRUCTURE': [
            {'tool': 'create_folder', 'priority': 1, 'description': 'Create main project directory'},
            {'tool': 'create_file', 'priority': 2, 'description': 'Create README.md'},
            {'tool': 'create_folder', 'priority': 3, 'description': 'Create subdirectories'},
            {'tool': 'create_file', 'priority': 4, 'description': 'Create project files'}
        ],
        
        'DOCUMENTATION_SERIES': [
            {'tool': 'create_file', 'priority': 1, 'description': 'Create main documentation file'},
            {'tool': 'create_file', 'priority': 2, 'description': 'Create section files'},
            {'tool': 'create_file', 'priority': 3, 'description': 'Create examples/references'}
        ],
        
        'FILE_BATCH_OPERATIONS': [
            {'tool': 'list_files', 'priority': 1, 'description': 'List files to process'},
            {'tool': 'copy_file', 'priority': 2, 'description': 'Process files'},  # Could be copy, move, etc.
            {'tool': 'list_files', 'priority': 3, 'description': 'Verify results'}
        ]
    }
    
    def __init__(self, context: Optional[ConversationContext] = None):
        """
        Initialize smart tool selector.
        
        Args:
            context: Optional conversation context (uses global if not provided)
        """
        super().__init__()
        self.context = context or get_conversation_context()
    
    def select_tools_with_context(
        self, 
        intent: str, 
        user_input: str, 
        confidence: float,
        context_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select tools with conversation context for enhanced accuracy.
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            context_info: Conversation context information
            
        Returns:
            Dictionary with tool selection information
        """
        try:
            return self._select_tools_with_context_with_exceptions(intent, user_input, confidence, context_info)
        except Exception as e:
            # Log error but continue with fallback for backward compatibility
            logging.error(f"Smart tool selection failed: {e}")
            print(f"Warning: Smart tool selection error: {str(e)}")
            # Fall back to basic selection
            basic_tool = self.select_tool(intent, user_input, confidence)
            return {
                "primary_tool": basic_tool,
                "tool_sequence": [basic_tool],
                "is_multi_step": False,
                "confidence": confidence,
                "selection_method": "fallback",
                "error": str(e)
            }

    def _select_tools_with_context_with_exceptions(
        self, 
        intent: str, 
        user_input: str, 
        confidence: float,
        context_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select tools with conversation context - raises exceptions for validation errors.
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            context_info: Conversation context information
            
        Returns:
            Dictionary with tool selection information
            
        Raises:
            ToolParameterError: For invalid input parameters
            ToolNotFoundError: When no suitable tool is found
            ToolExecutionError: For tool selection issues
        """
        # Input validation
        if not intent or not isinstance(intent, str):
            error = ToolParameterError(f"Invalid intent: {intent}")
            error.context["intent"] = intent
            logging.error(f"Smart tool selection failed: {error}")
            raise error
            
        if user_input is None or not isinstance(user_input, str):
            error = ToolParameterError(f"Invalid user input: {type(user_input)}")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Smart tool selection failed: {error}")
            raise error
        
        try:
            # Check for multi-step operations first
            multi_step_info = context_info.get("multi_step_detected", {})
            if multi_step_info.get("is_multi_step", False):
                return self._plan_multi_step_operations(intent, user_input, confidence, context_info)
            
            # Single-step operation: use context-aware selection
            primary_tool = self._select_contextual_tool(intent, user_input, context_info)
            
            # Calculate enhanced confidence based on context alignment
            enhanced_confidence = self._calculate_contextual_confidence(
                primary_tool, intent, confidence, context_info
            )
            
            # Build response
            selection_info = {
                "primary_tool": primary_tool,
                "tool_sequence": [primary_tool],
                "is_multi_step": False,
                "confidence": enhanced_confidence,
                "selection_method": "context_aware",
                "context_factors": self._get_context_factors_used(intent, user_input, context_info),
                "alternative_tools": self._suggest_alternative_tools(intent, user_input, context_info)
            }
            
            return selection_info
            
        except (ToolParameterError, ToolNotFoundError, ToolExecutionError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("smart_tool_selection", e)
            converted_error.context.update({
                "intent": intent,
                "input": user_input[:100] if user_input else None,
                "confidence": confidence
            })
            logging.error(f"Smart tool selection failed: {converted_error}")
            raise converted_error
    
    def _select_contextual_tool(self, intent: str, user_input: str, context_info: Dict[str, Any]) -> str:
        """
        Select tool using contextual mappings and conversation awareness.
        
        Args:
            intent: The classified intent
            user_input: User's input
            context_info: Conversation context
            
        Returns:
            Selected tool name
        """
        input_lower = user_input.lower()
        
        # Get tool mappings for this intent
        if intent not in self.CONTEXTUAL_TOOL_MAPPINGS:
            # Fall back to base class logic
            return self.select_tool(intent, user_input, 0.5)
        
        mapping = self.CONTEXTUAL_TOOL_MAPPINGS[intent]
        
        # Check patterns with context awareness
        if 'patterns' in mapping:
            for pattern, tool in mapping['patterns'].items():
                try:
                    if re.search(pattern, input_lower):
                        # Verify tool makes sense in current context
                        if self._validate_tool_in_context(tool, context_info):
                            return tool
                except re.error as e:
                    logger.warning(f"Invalid contextual regex pattern: {pattern} - {e}")
                    continue
        
        # Check for file references in context
        file_referenced = self._resolve_file_reference(user_input, context_info)
        if file_referenced:
            # If user references a specific file, adapt tool selection
            if intent == 'CONTENT_CREATION':
                # Creating content for existing file = updating
                return 'write_to_file'
            elif intent == 'FILE_MANAGEMENT':
                # Managing existing file = likely reading first
                return 'read_file'
        
        # Use user's preferred tools if available
        user_patterns = context_info.get("user_patterns", {})
        preferred_tools = user_patterns.get("preferred_tools", [])
        
        if preferred_tools and intent in self.TOOL_MAPPINGS:
            # Get expected tools for this intent
            base_mapping = self.TOOL_MAPPINGS[intent]
            expected_tools = [base_mapping.get('default')]
            if 'patterns' in base_mapping:
                expected_tools.extend(base_mapping['patterns'].values())
            
            # If user has preference for tools that work with this intent, use it
            for preferred_tool in preferred_tools:
                if preferred_tool in expected_tools:
                    return preferred_tool
        
        # Return default tool for intent
        return mapping.get('default', 'create_file')
    
    def _validate_tool_in_context(self, tool: str, context_info: Dict[str, Any]) -> bool:
        """
        Validate that a tool makes sense in the current conversation context.
        
        Args:
            tool: Tool name to validate
            context_info: Conversation context
            
        Returns:
            True if tool is appropriate for current context
        """
        # Check if tool requires files that don't exist
        if tool in ['read_file', 'write_to_file'] and 'write_to_file' in tool:
            input_analysis = context_info.get("input_analysis", {})
            recent_files = context_info.get("recent_files", [])
            
            # If tool suggests working with existing files but no files exist
            if input_analysis.get("references_previous", False) and not recent_files:
                return False  # Can't reference files that don't exist
        
        # For now, most tools are generally valid
        return True
    
    def _resolve_file_reference(self, user_input: str, context_info: Dict[str, Any]) -> Optional[str]:
        """
        Resolve file references in user input using conversation context.
        
        Args:
            user_input: User's input
            context_info: Conversation context
            
        Returns:
            Filename if reference resolved, None otherwise
        """
        input_lower = user_input.lower()
        input_analysis = context_info.get("input_analysis", {})
        
        # Check if user is referencing previous work
        if not input_analysis.get("references_previous", False):
            return None
        
        # Get recent files for context
        recent_files = context_info.get("recent_files", [])
        if not recent_files:
            return None
        
        # Simple heuristic: if user says "the file" or similar, assume most recent file
        reference_patterns = [
            r'\b(the|that|this)\s+(file|document)',
            r'\bprevious\s+(file|document)',
            r'\blast\s+(file|document)',
        ]
        
        for pattern in reference_patterns:
            if re.search(pattern, input_lower):
                # Return most recently created/modified file
                recent_files_sorted = sorted(recent_files, key=lambda f: f.get("created", 0), reverse=True)
                if recent_files_sorted:
                    return recent_files_sorted[0].get("name")
        
        return None
    
    def _calculate_contextual_confidence(
        self, 
        tool: str, 
        intent: str, 
        base_confidence: float, 
        context_info: Dict[str, Any]
    ) -> float:
        """
        Calculate enhanced confidence based on contextual factors.
        
        Args:
            tool: Selected tool
            intent: Classified intent
            base_confidence: Original confidence score
            context_info: Conversation context
            
        Returns:
            Enhanced confidence score
        """
        enhanced_confidence = base_confidence
        
        # Boost confidence if tool aligns with user patterns
        user_patterns = context_info.get("user_patterns", {})
        preferred_tools = user_patterns.get("preferred_tools", [])
        
        if tool in preferred_tools:
            enhanced_confidence += 0.15  # Boost for user preference
        
        # Boost confidence if tool aligns with recent operations
        recent_operations = context_info.get("recent_operations", [])
        if recent_operations:
            recent_tools = [op.get("tool", "") for op in recent_operations[-3:]]
            if tool in recent_tools:
                enhanced_confidence += 0.1  # Boost for consistency
        
        # Boost confidence if context strongly suggests this tool
        input_analysis = context_info.get("input_analysis", {})
        if input_analysis.get("references_previous", False) and tool in ['read_file', 'write_to_file']:
            enhanced_confidence += 0.1  # Boost for contextual appropriateness
        
        # Ensure confidence doesn't exceed 1.0
        return min(enhanced_confidence, 1.0)
    
    def _get_context_factors_used(self, intent: str, user_input: str, context_info: Dict[str, Any]) -> List[str]:
        """Get list of context factors that influenced tool selection"""
        factors = []
        
        input_analysis = context_info.get("input_analysis", {})
        
        if input_analysis.get("references_previous", False):
            factors.append("references_previous_work")
        
        if input_analysis.get("suggests_continuation", False):
            factors.append("suggests_continuation")
        
        user_patterns = context_info.get("user_patterns", {})
        if user_patterns.get("preferred_tools"):
            factors.append("user_tool_preferences")
        
        recent_operations = context_info.get("recent_operations", [])
        if recent_operations:
            factors.append("recent_operation_consistency")
        
        if not factors:
            factors.append("pattern_matching_only")
        
        return factors
    
    def _suggest_alternative_tools(self, intent: str, user_input: str, context_info: Dict[str, Any]) -> List[str]:
        """Suggest alternative tools that could work for this intent"""
        alternatives = []
        
        if intent in self.CONTEXTUAL_TOOL_MAPPINGS:
            mapping = self.CONTEXTUAL_TOOL_MAPPINGS[intent]
            
            # Add default tool if not already primary
            if 'default' in mapping:
                alternatives.append(mapping['default'])
            
            # Add tools from patterns
            if 'patterns' in mapping:
                alternatives.extend(mapping['patterns'].values())
        
        # Remove duplicates and return up to 3 alternatives
        unique_alternatives = list(dict.fromkeys(alternatives))
        return unique_alternatives[:3]
    
    def _plan_multi_step_operations(
        self, 
        intent: str, 
        user_input: str, 
        confidence: float,
        context_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan multi-step operations with tool sequence.
        
        Args:
            intent: The classified intent
            user_input: User's input
            confidence: Confidence score
            context_info: Conversation context
            
        Returns:
            Dictionary with multi-step operation plan
        """
        multi_step_info = context_info.get("multi_step_detected", {})
        operation_type = multi_step_info.get("operation_type")
        
        if operation_type not in self.MULTI_STEP_PLANS:
            # Fall back to single-step
            primary_tool = self._select_contextual_tool(intent, user_input, context_info)
            return {
                "primary_tool": primary_tool,
                "tool_sequence": [primary_tool],
                "is_multi_step": False,
                "confidence": confidence,
                "selection_method": "single_step_fallback"
            }
        
        # Get planned sequence
        plan = self.MULTI_STEP_PLANS[operation_type].copy()
        
        # Customize plan based on user input and context
        customized_plan = self._customize_multi_step_plan(plan, user_input, context_info)
        
        # Build tool sequence
        tool_sequence = [step['tool'] for step in customized_plan]
        primary_tool = tool_sequence[0] if tool_sequence else 'create_file'
        
        return {
            "primary_tool": primary_tool,
            "tool_sequence": tool_sequence,
            "is_multi_step": True,
            "estimated_steps": len(tool_sequence),
            "step_descriptions": [step['description'] for step in customized_plan],
            "operation_type": operation_type,
            "confidence": min(confidence + 0.1, 1.0),  # Boost confidence for planned operations
            "selection_method": "multi_step_planning"
        }
    
    def _customize_multi_step_plan(
        self, 
        plan: List[Dict[str, Any]], 
        user_input: str, 
        context_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Customize a multi-step plan based on user input and context.
        
        Args:
            plan: Base plan template
            user_input: User's input
            context_info: Conversation context
            
        Returns:
            Customized plan
        """
        customized_plan = plan.copy()
        input_lower = user_input.lower()
        
        # Customize based on specific mentions in user input
        for step in customized_plan:
            # If user mentions specific file types, adapt descriptions
            if 'json' in input_lower and step['tool'] == 'create_file':
                step['tool'] = 'write_json_file'
                step['description'] = step['description'].replace('file', 'JSON file')
            
            # If user has preferences, adapt tools
            user_patterns = context_info.get("user_patterns", {})
            preferred_tools = user_patterns.get("preferred_tools", [])
            
            if step['tool'] == 'create_file' and 'write_to_file' in preferred_tools:
                step['tool'] = 'write_to_file'
        
        return customized_plan


# Smart tool selector instance for the application
smart_tool_selector = SmartToolSelector()


def get_smart_tool_selector() -> SmartToolSelector:
    """Get the global smart tool selector instance"""
    return smart_tool_selector
