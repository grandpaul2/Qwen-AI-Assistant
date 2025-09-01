"""
Intent Classification Layer for WorkspaceAI
Handles high-level intent categorization before tool selection
"""

import re
from typing import Tuple, Dict, Any

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
        Classify user input and return (intent, confidence_score)
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (intent_name, confidence_score)
        """
        scores = {}
        input_lower = user_input.lower()
        
        # Score base patterns
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    score += 1
            scores[intent] = score
        
        # Apply context boosters
        for intent, boosters in self.CONTEXT_BOOSTERS.items():
            if intent in scores:
                for booster in boosters:
                    if re.search(booster, input_lower):
                        scores[intent] += 0.5  # Boost existing scores
        
        # Handle no matches
        if all(score == 0 for score in scores.values()):
            return 'UNCLEAR', 0.0
        
        # Calculate confidence
        total_score = sum(scores.values())
        best_intent = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[best_intent] / total_score if total_score > 0 else 0.0
        
        return best_intent, confidence
    
    def get_classification_details(self, user_input: str) -> Dict[str, Any]:
        """
        Get detailed classification breakdown for debugging
        
        Args:
            user_input: The user's input string
            
        Returns:
            Dictionary with classification details
        """
        intent, confidence = self.classify_with_confidence(user_input)
        
        # Get pattern matches for debugging
        input_lower = user_input.lower()
        matches = {}
        
        for intent_name, patterns in self.INTENT_PATTERNS.items():
            intent_matches = []
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    intent_matches.append(pattern)
            if intent_matches:
                matches[intent_name] = intent_matches
        
        return {
            'input': user_input,
            'classified_intent': intent,
            'confidence': confidence,
            'pattern_matches': matches,
            'all_scores': self._calculate_all_scores(user_input)
        }
    
    def _calculate_all_scores(self, user_input: str) -> Dict[str, float]:
        """Calculate scores for all intents"""
        scores = {}
        input_lower = user_input.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    score += 1
            scores[intent] = score
        
        return scores


# Convenience function for quick classification
def classify_intent(user_input: str) -> Tuple[str, float]:
    """
    Quick function to classify intent
    
    Args:
        user_input: The user's input string
        
    Returns:
        Tuple of (intent_name, confidence_score)
    """
    classifier = IntentClassifier()
    return classifier.classify_with_confidence(user_input)


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
