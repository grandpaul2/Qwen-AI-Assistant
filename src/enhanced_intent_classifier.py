"""
Enhanced Intent Classification Layer for WorkspaceAI
Context-aware intent classification with conversation memory and multi-step detection
"""

import re
import logging
from typing import Tuple, Dict, Any, Optional, List

from .intent_classifier import IntentClassifier
from .context_manager import ConversationContext, get_conversation_context
from .exceptions import (
    IntentError,
    AmbiguousIntentError,
    UnknownIntentError,
    WorkspaceAIError,
    handle_exception
)

logger = logging.getLogger(__name__)


class EnhancedIntentClassifier(IntentClassifier):
    """
    Context-aware intent classification that considers conversation history,
    file state, and user patterns for improved accuracy and intelligence.
    """
    
    # Enhanced patterns that consider context
    CONTEXTUAL_PATTERNS = {
        'CONTENT_CREATION': [
            # Original patterns from base class
            r'\b(write|create|make|generate|build|compose)\s+.*\b(guide|file|doc|tutorial|content|documentation)',
            r'\b(save|store|put).*\b(in|to|as)\s+.*\b(file|document)',
            
            # Context-aware patterns
            r'\b(add|append|extend)\s+.*\b(to|in)\s+(the|that|this)\s+(file|document)',
            r'\b(update|modify|edit)\s+(the|that|this)\s+(file|document)',
            r'\bcontinue\s+(with|working\s+on)\s+.*\b(file|document)',
            r'\badd\s+(more|another)\s+(section|chapter|part)',
        ],
        
        'CONTENT_CONTINUATION': [
            # New intent for continuing previous work
            r'\bcontinue\s+(where\s+we\s+left\s+off|with\s+that)',
            r'\badd\s+(to|more\s+to)\s+(the|that)\s+(file|document)',
            r'\bkeep\s+(working|going)\s+on\s+(the|that|this)',
            r'\bextend\s+(the|that|this)\s+(file|document|guide)',
            r'\bappend\s+(to|more\s+to)\s+(the|that)\s+(file|document)',
        ],
        
        'FILE_REFERENCE': [
            # References to previously created files
            r'\b(the|that|this)\s+(file|document)\s+(we|i)\s+(created|made|built)',
            r'\b(the|that|this)\s+(file|document)\s+(from\s+)?(earlier|before)',
            r'\bprevious\s+(file|document|work)',
            r'\blast\s+(file|document)\s+(we|i)\s+(created|made)',
        ],
        
        'PROJECT_MANAGEMENT': [
            # Project-level operations
            r'\bcreate\s+a\s+(new\s+)?project',
            r'\bstart\s+a\s+(new\s+)?project',
            r'\bproject\s+structure',
            r'\bsetup\s+(a\s+)?workspace',
            r'\borganize\s+(the\s+)?files',
        ]
    }
    
    # Multi-step operation patterns
    MULTI_STEP_PATTERNS = {
        'CREATE_PROJECT_STRUCTURE': [
            r'\bcreate\s+.*\bproject\s+structure',
            r'\bsetup\s+.*\bproject\s+with\s+.*\bfiles',
            r'\bbuild\s+.*\bworkspace\s+with',
            r'\bmake\s+.*\bfolder\s+structure',
        ],
        
        'DOCUMENTATION_SERIES': [
            r'\bcreate\s+.*\b(guide|tutorial|documentation)\s+series',
            r'\bmake\s+.*\bmultiple\s+(guides|files|documents)',
            r'\bgenerate\s+.*\b(set|series)\s+of\s+(files|guides)',
        ],
        
        'FILE_BATCH_OPERATIONS': [
            r'\b(copy|move|backup)\s+.*\ball\s+(files|documents)',
            r'\b(process|handle|organize)\s+.*\bmultiple\s+files',
            r'\bbatch\s+(operation|process|create)',
        ]
    }
    
    def __init__(self, context: Optional[ConversationContext] = None):
        """
        Initialize enhanced intent classifier.
        
        Args:
            context: Optional conversation context (uses global if not provided)
        """
        super().__init__()
        self.context = context or get_conversation_context()
        
    def classify_with_context(self, user_input: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Classify user input with conversation context for enhanced accuracy.
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (intent_name, confidence_score, context_info)
        """
        try:
            return self._classify_with_context_with_exceptions(user_input)
        except Exception as e:
            # Log error but continue with fallback for backward compatibility
            logging.error(f"Enhanced intent classification failed: {e}")
            print(f"Warning: Enhanced intent classification error: {str(e)}")
            # Fall back to basic classification
            basic_intent, confidence = self.classify_with_confidence(user_input)
            return basic_intent, confidence, {"error": str(e), "fallback": True}

    def _classify_with_context_with_exceptions(self, user_input: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Classify user input with conversation context - raises exceptions for validation errors.
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (intent_name, confidence_score, context_info)
            
        Raises:
            IntentError: For intent classification issues
            AmbiguousIntentError: When multiple intents have equal high confidence
            UnknownIntentError: When no patterns match the input
        """
        # Input validation (inherited from base class)
        if user_input is None:
            error = IntentError("Input cannot be None")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Enhanced intent classification failed: {error}")
            raise error
            
        if not isinstance(user_input, str):
            error = IntentError(f"Input must be a string, got {type(user_input).__name__}")
            error.context["input_type"] = type(user_input).__name__
            error.context["input_value"] = str(user_input)
            logging.error(f"Enhanced intent classification failed: {error}")
            raise error
        
        # Get conversation context for this classification
        context_info = self.context.get_context_for_intent(user_input)
        
        try:
            # Start with base classification
            base_intent, base_confidence = self.classify_with_confidence(user_input)
            
            # Apply context-aware enhancements
            enhanced_intent, enhanced_confidence = self._apply_context_awareness(
                user_input, base_intent, base_confidence, context_info
            )
            
            # Check for multi-step operations
            multi_step_info = self._detect_multi_step_operations(user_input, context_info)
            
            # Update context info with classification results
            context_info.update({
                "base_classification": {"intent": base_intent, "confidence": base_confidence},
                "enhanced_classification": {"intent": enhanced_intent, "confidence": enhanced_confidence},
                "multi_step_detected": multi_step_info,
                "classification_method": "context_aware"
            })
            
            return enhanced_intent, enhanced_confidence, context_info
            
        except (IntentError, AmbiguousIntentError, UnknownIntentError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("enhanced_intent_classification", e)
            converted_error.context["input"] = user_input[:100] if user_input else None
            converted_error.context["context_info"] = str(context_info)
            logging.error(f"Enhanced intent classification failed: {converted_error}")
            raise converted_error
    
    def _apply_context_awareness(
        self, 
        user_input: str, 
        base_intent: str, 
        base_confidence: float, 
        context_info: Dict[str, Any]
    ) -> Tuple[str, float]:
        """
        Apply context-aware intelligence to refine intent classification.
        
        Args:
            user_input: Original user input
            base_intent: Base intent from standard classification
            base_confidence: Base confidence score
            context_info: Conversation context information
            
        Returns:
            Tuple of (refined_intent, refined_confidence)
        """
        input_lower = user_input.lower()
        input_analysis = context_info.get("input_analysis", {})
        
        # Check for file references that suggest continuation
        if input_analysis.get("references_previous", False):
            if base_intent == 'CONTENT_CREATION':
                # If user references previous work and wants to create content,
                # this might be continuation rather than new creation
                if self._matches_continuation_patterns(input_lower):
                    return 'CONTENT_CONTINUATION', min(base_confidence + 0.2, 1.0)
        
        # Check for project-level operations
        if self._matches_project_patterns(input_lower):
            if base_intent in ['CONTENT_CREATION', 'FILE_MANAGEMENT']:
                return 'PROJECT_MANAGEMENT', min(base_confidence + 0.15, 1.0)
        
        # Boost confidence for patterns matching user preferences
        user_patterns = context_info.get("user_patterns", {})
        preferred_tools = user_patterns.get("preferred_tools", [])
        
        # If the classified intent aligns with user's preferred tools, boost confidence
        intent_tool_mapping = {
            'CONTENT_CREATION': ['create_file', 'write_to_file', 'write_json_file'],
            'FILE_MANAGEMENT': ['read_file', 'list_files', 'search_files', 'copy_file'],
            'SOFTWARE_INSTALLATION': ['generate_install_commands']
        }
        
        if base_intent in intent_tool_mapping:
            expected_tools = intent_tool_mapping[base_intent]
            if any(tool in preferred_tools for tool in expected_tools):
                # User frequently uses tools associated with this intent
                boosted_confidence = min(base_confidence + 0.1, 1.0)
                return base_intent, boosted_confidence
        
        # Apply contextual pattern matching
        contextual_scores = self._score_contextual_patterns(input_lower)
        if contextual_scores:
            best_contextual_intent = max(contextual_scores.keys(), key=lambda k: contextual_scores[k])
            best_contextual_score = contextual_scores[best_contextual_intent]
            
            # If contextual scoring gives significantly higher confidence, use it
            if best_contextual_score > base_confidence + 0.2:
                return best_contextual_intent, best_contextual_score
        
        return base_intent, base_confidence
    
    def _matches_continuation_patterns(self, input_lower: str) -> bool:
        """Check if input matches continuation patterns"""
        continuation_patterns = self.CONTEXTUAL_PATTERNS.get('CONTENT_CONTINUATION', [])
        return any(re.search(pattern, input_lower) for pattern in continuation_patterns)
    
    def _matches_project_patterns(self, input_lower: str) -> bool:
        """Check if input matches project management patterns"""
        project_patterns = self.CONTEXTUAL_PATTERNS.get('PROJECT_MANAGEMENT', [])
        return any(re.search(pattern, input_lower) for pattern in project_patterns)
    
    def _score_contextual_patterns(self, input_lower: str) -> Dict[str, float]:
        """Score input against contextual patterns"""
        scores = {}
        
        for intent, patterns in self.CONTEXTUAL_PATTERNS.items():
            score = 0
            for pattern in patterns:
                try:
                    if re.search(pattern, input_lower):
                        score += 1
                except re.error as e:
                    # Handle regex compilation errors
                    logger.warning(f"Invalid contextual regex pattern in {intent}: {pattern} - {e}")
                    continue
            
            if score > 0:
                # Normalize score (could be enhanced with pattern weights)
                normalized_score = min(score / len(patterns), 1.0)
                scores[intent] = normalized_score
        
        return scores
    
    def _detect_multi_step_operations(self, user_input: str, context_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect if the user input suggests a multi-step operation.
        
        Args:
            user_input: The user's input
            context_info: Conversation context
            
        Returns:
            Dictionary with multi-step operation information
        """
        input_lower = user_input.lower()
        multi_step_info = {
            "is_multi_step": False,
            "operation_type": None,
            "estimated_steps": 0,
            "suggested_sequence": []
        }
        
        # Check multi-step patterns
        for operation_type, patterns in self.MULTI_STEP_PATTERNS.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, input_lower):
                        multi_step_info["is_multi_step"] = True
                        multi_step_info["operation_type"] = operation_type
                        break
                except re.error as e:
                    logger.warning(f"Invalid multi-step regex pattern: {pattern} - {e}")
                    continue
            
            if multi_step_info["is_multi_step"]:
                break
        
        # If multi-step operation detected, suggest sequence
        if multi_step_info["is_multi_step"]:
            multi_step_info = self._plan_multi_step_sequence(multi_step_info, user_input, context_info)
        
        return multi_step_info
    
    def _plan_multi_step_sequence(
        self, 
        multi_step_info: Dict[str, Any], 
        user_input: str, 
        context_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan the sequence of steps for a multi-step operation.
        
        Args:
            multi_step_info: Current multi-step information
            user_input: Original user input
            context_info: Conversation context
            
        Returns:
            Enhanced multi-step information with planned sequence
        """
        operation_type = multi_step_info["operation_type"]
        
        if operation_type == "CREATE_PROJECT_STRUCTURE":
            # Plan project structure creation
            sequence = [
                {"step": 1, "action": "create_folder", "description": "Create main project directory"},
                {"step": 2, "action": "create_file", "description": "Create README.md file"},
                {"step": 3, "action": "create_folder", "description": "Create subdirectories (src, docs, etc.)"},
                {"step": 4, "action": "create_file", "description": "Create additional project files"}
            ]
            multi_step_info["estimated_steps"] = 4
            multi_step_info["suggested_sequence"] = sequence
            
        elif operation_type == "DOCUMENTATION_SERIES":
            # Plan documentation series creation
            sequence = [
                {"step": 1, "action": "create_file", "description": "Create main guide/overview"},
                {"step": 2, "action": "create_file", "description": "Create detailed sections/chapters"},
                {"step": 3, "action": "create_file", "description": "Create examples and references"}
            ]
            multi_step_info["estimated_steps"] = 3
            multi_step_info["suggested_sequence"] = sequence
            
        elif operation_type == "FILE_BATCH_OPERATIONS":
            # Plan batch file operations
            recent_files = context_info.get("recent_files", [])
            estimated_files = max(len(recent_files), 3)  # Estimate based on context
            
            sequence = [
                {"step": 1, "action": "list_files", "description": "Identify files to process"},
                {"step": 2, "action": "batch_operation", "description": f"Process {estimated_files} files"},
                {"step": 3, "action": "verify_results", "description": "Verify operation completion"}
            ]
            multi_step_info["estimated_steps"] = estimated_files + 2
            multi_step_info["suggested_sequence"] = sequence
        
        return multi_step_info
    
    def resolve_ambiguous_intent(
        self, 
        user_input: str, 
        possible_intents: List[str], 
        context_info: Dict[str, Any]
    ) -> Tuple[str, float, str]:
        """
        Resolve ambiguous intent using conversation context.
        
        Args:
            user_input: The user's input
            possible_intents: List of possible intents with equal confidence
            context_info: Conversation context
            
        Returns:
            Tuple of (resolved_intent, confidence, reasoning)
        """
        input_lower = user_input.lower()
        input_analysis = context_info.get("input_analysis", {})
        recent_operations = context_info.get("recent_operations", [])
        user_patterns = context_info.get("user_patterns", {})
        
        # Rule 1: If user references previous work, prefer continuation over creation
        if input_analysis.get("references_previous", False):
            if "CONTENT_CREATION" in possible_intents and "FILE_MANAGEMENT" in possible_intents:
                return "FILE_MANAGEMENT", 0.8, "User references previous work, likely wants to manage existing files"
        
        # Rule 2: If user recently performed similar operations, prefer consistency
        if recent_operations:
            recent_types = [op["type"] for op in recent_operations[-3:]]  # Last 3 operations
            
            intent_operation_mapping = {
                "CONTENT_CREATION": ["file_creation", "content_writing"],
                "FILE_MANAGEMENT": ["file_read", "file_search", "file_copy"],
                "SOFTWARE_INSTALLATION": ["software_install", "package_install"]
            }
            
            for intent in possible_intents:
                if intent in intent_operation_mapping:
                    expected_ops = intent_operation_mapping[intent]
                    if any(recent_type in expected_ops for recent_type in recent_types):
                        return intent, 0.75, f"User recently performed {intent.lower()} operations"
        
        # Rule 3: Use user preferences from patterns
        preferred_tools = user_patterns.get("preferred_tools", [])
        if preferred_tools:
            intent_tool_mapping = {
                "CONTENT_CREATION": ["create_file", "write_to_file", "write_json_file"],
                "FILE_MANAGEMENT": ["read_file", "list_files", "search_files"],
                "SOFTWARE_INSTALLATION": ["generate_install_commands"]
            }
            
            for intent in possible_intents:
                if intent in intent_tool_mapping:
                    expected_tools = intent_tool_mapping[intent]
                    if any(tool in preferred_tools for tool in expected_tools):
                        return intent, 0.7, f"Matches user's preferred tools: {preferred_tools}"
        
        # Rule 4: Default to most specific intent based on keywords
        specificity_ranking = {
            "SOFTWARE_INSTALLATION": 3,  # Most specific
            "CONTENT_CREATION": 2,
            "FILE_MANAGEMENT": 1  # Most general
        }
        
        ranked_intents = sorted(
            possible_intents, 
            key=lambda intent: specificity_ranking.get(intent, 0), 
            reverse=True
        )
        
        if ranked_intents:
            return ranked_intents[0], 0.6, "Selected most specific intent from ambiguous options"
        
        # Fallback: return first intent with low confidence
        return possible_intents[0], 0.5, "Unable to resolve ambiguity, using first option"


# Enhanced classifier instance for the application
enhanced_intent_classifier = EnhancedIntentClassifier()


def get_enhanced_intent_classifier() -> EnhancedIntentClassifier:
    """Get the global enhanced intent classifier instance"""
    return enhanced_intent_classifier
