"""
Context-Weighted Tool Selector for WorkspaceAI
Handles precise tool selection with numerical confidence scoring
"""

import re
from typing import Dict, Tuple, Any, Optional

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
        Calculate weighted confidence scores for the input
        
        Args:
            user_input: The user's input string
            
        Returns:
            Tuple of (total_weight, word_breakdown)
        """
        total_weight = 0
        word_breakdown = {}
        input_lower = user_input.lower()
        
        for priority, config in self.WEIGHT_SYSTEM.items():
            for word in config['words']:
                if word in input_lower:
                    weight = config['weight']
                    total_weight += weight
                    word_breakdown[word] = weight
        
        return total_weight, word_breakdown
    
    def select_tool(self, intent: str, user_input: str, confidence: float) -> str:
        """
        Select specific tool based on intent and context weighting
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            
        Returns:
            Selected tool name
        """
        input_lower = user_input.lower()
        
        # Apply disambiguation rules first
        for rule_name, rule_config in self.DISAMBIGUATION_RULES.items():
            if re.search(rule_config['pattern'], input_lower):
                return rule_config['preferred_tool']
        
        # Handle low confidence cases
        if confidence < 0.3:
            return self._conservative_selection(user_input)
        
        # Select tool based on intent
        if intent == 'CONTENT_CREATION':
            return self._select_content_creation_tool(user_input)
        elif intent == 'SOFTWARE_INSTALLATION':
            return self._select_installation_tool(user_input)
        elif intent == 'FILE_MANAGEMENT':
            return self._select_file_management_tool(user_input)
        else:
            return self._conservative_selection(user_input)
    
    def _select_content_creation_tool(self, user_input: str) -> str:
        """Select tool for content creation intent"""
        input_lower = user_input.lower()
        
        # Check for specific patterns
        for pattern, tool in self.TOOL_MAPPINGS['CONTENT_CREATION']['patterns'].items():
            if re.search(pattern, input_lower):
                return tool
        
        return self.TOOL_MAPPINGS['CONTENT_CREATION']['default']
    
    def _select_installation_tool(self, user_input: str) -> str:
        """Select tool for software installation intent"""
        return self.TOOL_MAPPINGS['SOFTWARE_INSTALLATION']['default']
    
    def _select_file_management_tool(self, user_input: str) -> str:
        """Select tool for file management intent"""
        input_lower = user_input.lower()
        
        # Check for specific patterns
        for pattern, tool in self.TOOL_MAPPINGS['FILE_MANAGEMENT']['patterns'].items():
            if re.search(pattern, input_lower):
                return tool
        
        return self.TOOL_MAPPINGS['FILE_MANAGEMENT']['default']
    
    def _conservative_selection(self, user_input: str) -> str:
        """Conservative tool selection for unclear cases"""
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
        Get detailed selection breakdown for debugging
        
        Args:
            intent: The classified intent
            user_input: The user's input string
            confidence: Confidence score from intent classification
            
        Returns:
            Dictionary with selection details
        """
        total_weight, word_breakdown = self.calculate_context_weight(user_input)
        selected_tool = self.select_tool(intent, user_input, confidence)
        
        # Check which rules were applied
        applied_rules = []
        input_lower = user_input.lower()
        
        for rule_name, rule_config in self.DISAMBIGUATION_RULES.items():
            if re.search(rule_config['pattern'], input_lower):
                applied_rules.append({
                    'rule': rule_name,
                    'pattern': rule_config['pattern'],
                    'preferred_tool': rule_config['preferred_tool'],
                    'explanation': rule_config['rule']
                })
        
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
    Quick function to select tool
    
    Args:
        intent: The classified intent
        user_input: The user's input string
        confidence: Confidence score
        
    Returns:
        Selected tool name
    """
    selector = ContextWeightedToolSelector()
    return selector.select_tool(intent, user_input, confidence)


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
