"""
Intent Classification Layer for WorkspaceAI
Handles high-level intent categorization before tool selection
"""

import re
import logging
from typing import Tuple, Dict, Any, Optional

# Import custom exceptions
from .exceptions import (
    IntentError,
    AmbiguousIntentError,
    UnknownIntentError,
    WorkspaceAIError,
    handle_exception
)

class IntentClassifier:
    """Classifies user input into high-level intents with confidence scoring"""
    
    INTENT_PATTERNS = {
        'CONTENT_CREATION': [
            r'\b(write|create|make|generate|build|compose)\s+.*\b(guide|file|doc|tutorial|content|documentation)',
            r'\b(save|store|put).*\b(in|to|as)\s+.*\b(file|document)',
            r'\b(make|create).*\b(guide|tutorial|documentation)',
            r'\b(write|create).*\b(me|a)\s+.*\b(guide|file|document)',
            r'\b(generate|build).*\b(file|content|document)',
            r'\bput.*\bin\s+.*\bfile\b',
            r'\bcreate.*\.(txt|md|csv|json|py)\b'
        ],
        'SOFTWARE_INSTALLATION': [
            r'\b(install|setup|configure)\s+\w+',
            r'\bhow\s+to\s+install\b',
            r'\binstallation\s+(steps|commands|instructions)',
            r'\bsetup\s+(guide|instructions)\s+for\b',
            r'\binstall\s+commands\s+for\b',
            r'\bget\s+.*\binstallation\b'
        ],
        'FILE_MANAGEMENT': [
            r'\b(read|open|view|list|search|find)\s+.*\b(file|folder)',
            r'\b(copy|move|delete|backup)\s+.*\b(file|folder)',
            r'\bshow\s+me\s+(files|folders)',
            r'\blist\s+(all\s+)?files\b',
            r'\bsearch\s+for\s+.*\bfile',
            r'\bfind\s+.*\bfile',
            r'\bbackup\s+.*\bto\b',
            r'\bduplicate\s+.*\bfile',
            r'\bcopy\s+\w+\.\w+\s+to\s+\w+\.\w+',
            r'\bmove\s+\w+\.\w+\s+to\s+\w+\.\w+',
            r'\bdelete\s+\w+\.\w+'
        ]
    }
    
    # Additional context boost patterns
    CONTEXT_BOOSTERS = {
        'CONTENT_CREATION': [
            r'\bwrite\s+me\b',
            r'\bcreate\s+a\b',
            r'\bmake\s+me\b',
            r'\bgenerate\s+a\b'
        ],
        'SOFTWARE_INSTALLATION': [
            r'\bhow\s+do\s+i\s+install\b',
            r'\binstall\s+on\s+(ubuntu|windows|mac)',
            r'\bsetup\s+on\b'
        ]
    }
    
    def __init__(self):
        """Initialize the intent classifier"""
        pass
    
    def classify_with_confidence(self, user_input: str) -> Tuple[str, float]:
        """
        Classify user input and return (intent, confidence_score) - backward compatible wrapper
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (intent_name, confidence_score)
        """
        try:
            return self._classify_with_confidence_with_exceptions(user_input)
        except Exception as e:
            # Log error but continue with fallback for backward compatibility
            logging.error(f"Intent classification failed: {e}")
            print(f"Warning: Intent classification error: {str(e)}")
            return 'UNCLEAR', 0.0

    def _classify_with_confidence_with_exceptions(self, user_input: str) -> Tuple[str, float]:
        """
        Classify user input and return (intent, confidence_score) - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (intent_name, confidence_score)
            
        Raises:
            IntentError: For intent classification issues
            AmbiguousIntentError: When multiple intents have equal high confidence
            UnknownIntentError: When no patterns match the input
        """
        # Input validation
        if user_input is None:
            error = IntentError("Input cannot be None")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Intent classification failed: {error}")
            raise error
            
        if not isinstance(user_input, str):
            error = IntentError(f"Input must be a string, got {type(user_input).__name__}")
            error.context["input_type"] = type(user_input).__name__
            error.context["input_value"] = str(user_input)
            logging.error(f"Intent classification failed: {error}")
            raise error
            
        # Handle empty input gracefully
        if not user_input.strip():
            return 'UNCLEAR', 0.0
            
        # Check for extremely long inputs that might cause performance issues
        if len(user_input) > 10000:  # 10KB limit
            error = IntentError(f"Input too long: {len(user_input)} characters (max 10000)")
            error.context["input_length"] = len(user_input)
            error.context["max_length"] = 10000
            logging.error(f"Intent classification failed: {error}")
            raise error

        try:
            scores = {}
            input_lower = user_input.lower()
            
            # Score base patterns with error handling for regex issues
            for intent, patterns in self.INTENT_PATTERNS.items():
                score = 0
                for pattern in patterns:
                    try:
                        if re.search(pattern, input_lower):
                            score += 1
                    except re.error as e:
                        # Handle regex compilation errors
                        error = IntentError(f"Invalid regex pattern in {intent}: {pattern}")
                        error.context["intent"] = intent
                        error.context["pattern"] = pattern
                        error.context["regex_error"] = str(e)
                        logging.error(f"Regex pattern error: {error}")
                        raise error
                scores[intent] = score

            # Apply context boosters with error handling
            for intent, boosters in self.CONTEXT_BOOSTERS.items():
                if intent in scores:
                    for booster in boosters:
                        try:
                            if re.search(booster, input_lower):
                                scores[intent] += 0.5  # Boost existing scores
                        except re.error as e:
                            # Handle regex compilation errors in boosters
                            error = IntentError(f"Invalid regex booster pattern in {intent}: {booster}")
                            error.context["intent"] = intent
                            error.context["booster_pattern"] = booster
                            error.context["regex_error"] = str(e)
                            logging.error(f"Regex booster error: {error}")
                            raise error

            # Handle no matches
            if all(score == 0 for score in scores.values()):
                error = UnknownIntentError(f"No patterns matched input")
                error.context["input"] = user_input[:100]  # First 100 chars for context
                error.context["input_length"] = len(user_input)
                error.context["available_intents"] = list(self.INTENT_PATTERNS.keys())
                logging.warning(f"Unknown intent: {error}")
                raise error

            # Calculate confidence
            total_score = sum(scores.values())
            if total_score == 0:
                return 'UNCLEAR', 0.0
                
            best_intent = max(scores.keys(), key=lambda k: scores[k])
            confidence = scores[best_intent] / total_score
            
            # Check for ambiguous results (multiple intents with same high score)
            max_score = scores[best_intent]
            tied_intents = [intent for intent, score in scores.items() if score == max_score and score > 0]
            
            if len(tied_intents) > 1 and confidence >= 0.4:  # High confidence tie
                error = AmbiguousIntentError(
                    f"Multiple intents tied with high confidence: {tied_intents}"
                )
                error.context["tied_intents"] = tied_intents
                error.context["tied_score"] = max_score
                error.context["confidence"] = confidence
                error.context["input"] = user_input[:100]
                logging.warning(f"Ambiguous intent: {error}")
                # Don't raise for ambiguous - return best guess for now
                # raise error

            return best_intent, confidence
            
        except (IntentError, AmbiguousIntentError, UnknownIntentError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("intent_classification", e)
            converted_error.context["input"] = user_input[:100] if user_input else None
            logging.error(f"Intent classification failed: {converted_error}")
            raise converted_error
    
    def get_classification_details(self, user_input: str) -> Dict[str, Any]:
        """
        Get detailed classification breakdown for debugging - backward compatible wrapper
        
        Args:
            user_input: The user's input string
            
        Returns:
            Dictionary with classification details
        """
        try:
            return self._get_classification_details_with_exceptions(user_input)
        except Exception as e:
            # Log error and return minimal details for backward compatibility
            logging.error(f"Classification details failed: {e}")
            print(f"Warning: Classification details error: {str(e)}")
            return {
                'input': user_input,
                'classified_intent': 'UNCLEAR',
                'confidence': 0.0,
                'pattern_matches': {},
                'all_scores': {},
                'error': str(e)
            }

    def _get_classification_details_with_exceptions(self, user_input: str) -> Dict[str, Any]:
        """
        Get detailed classification breakdown for debugging - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Dictionary with classification details
            
        Raises:
            IntentError: For intent classification issues
        """
        try:
            intent, confidence = self._classify_with_confidence_with_exceptions(user_input)
        except (UnknownIntentError, AmbiguousIntentError) as e:
            # These are valid classification results, just with warnings
            intent = 'UNCLEAR' if isinstance(e, UnknownIntentError) else e.context.get('tied_intents', ['UNCLEAR'])[0]
            confidence = 0.0 if isinstance(e, UnknownIntentError) else e.context.get('confidence', 0.0)
        
        # Get pattern matches for debugging
        if user_input is None or not isinstance(user_input, str):
            error = IntentError("Invalid input for pattern matching")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Pattern matching failed: {error}")
            raise error
            
        input_lower = user_input.lower()
        matches = {}
        
        try:
            for intent_name, patterns in self.INTENT_PATTERNS.items():
                intent_matches = []
                for pattern in patterns:
                    try:
                        if re.search(pattern, input_lower):
                            intent_matches.append(pattern)
                    except re.error as e:
                        # Log regex errors but continue
                        logging.warning(f"Regex error in pattern {pattern}: {e}")
                        continue
                if intent_matches:
                    matches[intent_name] = intent_matches
        except Exception as e:
            converted_error = handle_exception("pattern_matching", e)
            converted_error.context["input"] = user_input[:100] if user_input else None
            logging.error(f"Pattern matching failed: {converted_error}")
            raise converted_error

        try:
            all_scores = self._calculate_all_scores_with_exceptions(user_input)
        except Exception as e:
            logging.warning(f"Score calculation failed: {e}")
            all_scores = {}

        return {
            'input': user_input,
            'classified_intent': intent,
            'confidence': confidence,
            'pattern_matches': matches,
            'all_scores': all_scores
        }
    
    def _calculate_all_scores(self, user_input: str) -> Dict[str, float]:
        """Calculate scores for all intents - backward compatible wrapper"""
        try:
            return self._calculate_all_scores_with_exceptions(user_input)
        except Exception as e:
            logging.error(f"Score calculation failed: {e}")
            return {}

    def _calculate_all_scores_with_exceptions(self, user_input: str) -> Dict[str, float]:
        """
        Calculate scores for all intents - raises exceptions for validation errors
        
        Args:
            user_input: The user's input string
            
        Returns:
            Dictionary of intent scores
            
        Raises:
            IntentError: For score calculation issues
        """
        # Input validation
        if user_input is None:
            error = IntentError("Input cannot be None for score calculation")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Score calculation failed: {error}")
            raise error
            
        if not isinstance(user_input, str):
            error = IntentError(f"Input must be a string for score calculation, got {type(user_input).__name__}")
            error.context["input_type"] = type(user_input).__name__
            logging.error(f"Score calculation failed: {error}")
            raise error

        scores = {}
        input_lower = user_input.lower()
        
        try:
            for intent, patterns in self.INTENT_PATTERNS.items():
                score = 0
                for pattern in patterns:
                    try:
                        if re.search(pattern, input_lower):
                            score += 1
                    except re.error as e:
                        # Handle regex compilation errors
                        error = IntentError(f"Invalid regex pattern in {intent}: {pattern}")
                        error.context["intent"] = intent
                        error.context["pattern"] = pattern
                        error.context["regex_error"] = str(e)
                        logging.error(f"Regex pattern error in scoring: {error}")
                        raise error
                scores[intent] = score
        except IntentError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            converted_error = handle_exception("score_calculation", e)
            converted_error.context["input"] = user_input[:100] if user_input else None
            logging.error(f"Score calculation failed: {converted_error}")
            raise converted_error

        return scores


# Convenience function for quick classification
def classify_intent(user_input: str) -> Tuple[str, float]:
    """
    Quick function to classify intent - backward compatible wrapper
    
    Args:
        user_input: The user's input string
        
    Returns:
        Tuple of (intent_name, confidence_score)
    """
    try:
        return classify_intent_with_exceptions(user_input)
    except Exception as e:
        # Log error but return fallback for backward compatibility
        logging.error(f"Intent classification failed: {e}")
        print(f"Warning: Intent classification error: {str(e)}")
        return 'UNCLEAR', 0.0

def classify_intent_with_exceptions(user_input: str) -> Tuple[str, float]:
    """
    Quick function to classify intent - raises exceptions for validation errors
    
    Args:
        user_input: The user's input string
        
    Returns:
        Tuple of (intent_name, confidence_score)
        
    Raises:
        IntentError: For intent classification issues
        AmbiguousIntentError: When multiple intents have equal high confidence
        UnknownIntentError: When no patterns match the input
    """
    classifier = IntentClassifier()
    return classifier._classify_with_confidence_with_exceptions(user_input)


# Test the classifier
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    test_cases = [
        "write me a guide for git",
        "create documentation about docker", 
        "install git on ubuntu",
        "copy main.py to backup.py",
        "list all files",
        "make a tutorial on python"
    ]
    
    for test in test_cases:
        intent, confidence = classifier.classify_with_confidence(test)
        print(f"'{test}' → {intent} (confidence: {confidence:.2f})")
