"""
Adaptive Budget Manager

Provides intelligent response allocation based on query complexity with
anti-gaming measures and percentage-based scaling across context windows.
"""

import re
import math
from typing import Dict, List, Optional, Tuple
from enum import Enum


class InteractionMode(Enum):
    """Supported interaction modes with different budget profiles"""
    TOOLS = "tools"
    CHAT = "chat"


class ComplexityFactors:
    """Weights for different complexity indicators"""
    
    # Analysis keywords (higher weight = more complex)
    ANALYSIS_KEYWORDS = {
        'analyze': 2.0, 'explain': 1.5, 'compare': 2.0, 'evaluate': 2.5,
        'implement': 3.0, 'create': 2.0, 'design': 2.5, 'develop': 2.5,
        'optimize': 2.5, 'debug': 2.0, 'refactor': 2.0, 'review': 1.5,
        'summarize': 1.5, 'research': 2.0, 'investigate': 2.0
    }
    
    # Code indicators
    CODE_PATTERNS = [
        r'```[\s\S]*?```',  # Code blocks
        r'`[^`]+`',         # Inline code
        r'def\s+\w+',       # Function definitions
        r'class\s+\w+',     # Class definitions
        r'import\s+\w+',    # Import statements
        r'<[\w/]+>',        # HTML/XML tags
    ]
    
    # Question complexity indicators
    QUESTION_INDICATORS = {
        'how': 1.0, 'what': 0.5, 'why': 1.5, 'when': 0.5, 'where': 0.5,
        'which': 0.8, 'who': 0.3, 'can you': 1.2, 'could you': 1.2,
        'explain how': 2.0, 'show me': 1.5, 'help me': 1.8
    }
    
    # Length thresholds
    SHORT_QUERY = 50      # Characters
    MEDIUM_QUERY = 150    # Characters
    LONG_QUERY = 300      # Characters


class AdaptiveBudgetManager:
    """Intelligent response allocation based on query complexity"""
    
    def __init__(self):
        """Initialize budget manager with default parameters"""
        
        # Base budget allocations (percentages)
        self.base_budgets = {
            InteractionMode.TOOLS: {
                'system_prompt': 3.0,
                'tool_definitions': 6.0,
                'conversation_memory': 60.0,
                'response_generation': 15.0,  # Minimum, can expand
                'safety_margin': 5.0,
                'reserved': 11.0  # Available for adaptive allocation
            },
            InteractionMode.CHAT: {
                'system_prompt': 0.6,
                'tool_definitions': 0.0,
                'conversation_memory': 80.0,
                'response_generation': 15.0,  # Minimum, can expand
                'safety_margin': 5.0,
                'reserved': 4.4  # Available for adaptive allocation
            }
        }
        
        # Adaptive allocation ranges
        self.adaptive_ranges = {
            InteractionMode.TOOLS: {
                'response_min': 15.0,
                'response_max': 35.0,
                'memory_min': 55.0,
                'memory_max': 60.0
            },
            InteractionMode.CHAT: {
                'response_min': 15.0,
                'response_max': 25.0,
                'memory_min': 77.0,
                'memory_max': 80.0
            }
        }
    
    def analyze_complexity(self, user_input: str, mode: str = "chat") -> float:
        """
        Analyze query complexity with anti-gaming measures
        
        Args:
            user_input: User's input text
            mode: Interaction mode ("tools" or "chat")
            
        Returns:
            Complexity score from 0.0 (simple) to 1.0 (complex)
        """
        if not user_input or not isinstance(user_input, str):
            return 0.1
        
        # Normalize input
        text = user_input.strip().lower()
        text_length = len(text)
        
        if text_length == 0:
            return 0.1
        
        complexity_score = 0.0
        
        # 1. Length-based complexity (with diminishing returns)
        length_score = self._calculate_length_complexity(text_length)
        complexity_score += length_score * 0.25
        
        # 2. Keyword-based complexity (with anti-gaming)
        keyword_score = self._calculate_keyword_complexity(text, text_length)
        complexity_score += keyword_score * 0.30
        
        # 3. Code/technical content detection
        code_score = self._calculate_code_complexity(user_input)  # Use original case
        complexity_score += code_score * 0.25
        
        # 4. Question complexity
        question_score = self._calculate_question_complexity(text)
        complexity_score += question_score * 0.20
        
        # Apply mode-specific adjustments
        if mode == "tools":
            # Tools mode tends to be more complex
            complexity_score *= 1.2
        
        # Normalize to 0.0-1.0 range
        return max(0.0, min(1.0, complexity_score))
    
    def _calculate_length_complexity(self, length: int) -> float:
        """Calculate complexity based on text length with diminishing returns"""
        if length <= ComplexityFactors.SHORT_QUERY:
            return 0.1
        elif length <= ComplexityFactors.MEDIUM_QUERY:
            return 0.3
        elif length <= ComplexityFactors.LONG_QUERY:
            return 0.6
        else:
            # Diminishing returns for very long queries
            excess = length - ComplexityFactors.LONG_QUERY
            return min(0.9, 0.6 + (excess / 1000) * 0.3)
    
    def _calculate_keyword_complexity(self, text: str, text_length: int) -> float:
        """Calculate complexity based on keywords with anti-gaming normalization"""
        keyword_weights = 0.0
        keyword_count = 0
        
        # Count analysis keywords
        for keyword, weight in ComplexityFactors.ANALYSIS_KEYWORDS.items():
            count = text.count(keyword)
            if count > 0:
                # Diminishing returns for repeated keywords (anti-gaming)
                effective_count = math.sqrt(count)
                keyword_weights += weight * effective_count
                keyword_count += count
        
        if keyword_weights == 0:
            return 0.0
        
        # Normalize by text length to prevent gaming with keyword stuffing
        density = keyword_count / max(1, text_length / 10)  # Keywords per 10 chars
        if density > 0.3:  # More than 30% keyword density is suspicious
            keyword_weights *= 0.5  # Penalize keyword stuffing
        
        # Normalize to reasonable range
        return min(1.0, keyword_weights / 10.0)
    
    def _calculate_code_complexity(self, text: str) -> float:
        """Calculate complexity based on code content detection"""
        code_score = 0.0
        
        for pattern in ComplexityFactors.CODE_PATTERNS:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                # Code blocks are more complex than inline code
                if pattern.startswith(r'```'):
                    code_score += len(matches) * 0.5
                else:
                    code_score += len(matches) * 0.1
        
        return min(1.0, code_score)
    
    def _calculate_question_complexity(self, text: str) -> float:
        """Calculate complexity based on question patterns"""
        question_score = 0.0
        
        for indicator, weight in ComplexityFactors.QUESTION_INDICATORS.items():
            if indicator in text:
                question_score += weight
        
        # Multiple question words suggest more complex inquiry
        question_words = ['?', 'how', 'what', 'why', 'when', 'where', 'which']
        question_count = sum(1 for word in question_words if word in text)
        
        if question_count > 1:
            question_score *= 1.2
        
        return min(1.0, question_score / 5.0)
    
    def calculate_adaptive_budgets(self, context_window: int, mode: str, 
                                 user_input: str, minimum_memory_needed: int = 0) -> Dict[str, int]:
        """
        Calculate adaptive token budgets based on query complexity
        
        Args:
            context_window: Total context window size
            mode: Interaction mode ("tools" or "chat")
            user_input: User's input for complexity analysis
            minimum_memory_needed: Minimum tokens needed for conversation memory
            
        Returns:
            Dictionary of component -> token count mappings
        """
        try:
            interaction_mode = InteractionMode(mode.lower())
        except ValueError:
            interaction_mode = InteractionMode.CHAT
        
        # Analyze query complexity
        complexity = self.analyze_complexity(user_input, mode)
        
        # Get base budgets and ranges
        base_budgets = self.base_budgets[interaction_mode].copy()
        ranges = self.adaptive_ranges[interaction_mode]
        
        # Calculate adaptive response allocation
        response_range = ranges['response_max'] - ranges['response_min']
        adaptive_response = ranges['response_min'] + (complexity * response_range)
        
        # Calculate corresponding memory adjustment
        memory_range = ranges['memory_max'] - ranges['memory_min']
        memory_reduction = complexity * (memory_range / (response_range / (adaptive_response - ranges['response_min'])))
        adaptive_memory = ranges['memory_max'] - memory_reduction
        
        # Apply adaptive allocations
        base_budgets['response_generation'] = adaptive_response
        base_budgets['conversation_memory'] = adaptive_memory
        
        # Adjust reserved space
        total_fixed = (base_budgets['system_prompt'] + 
                      base_budgets['tool_definitions'] + 
                      base_budgets['safety_margin'])
        
        remaining_for_reserved = 100.0 - total_fixed - adaptive_response - adaptive_memory
        base_budgets['reserved'] = max(2.0, remaining_for_reserved)
        
        # Convert percentages to absolute tokens
        absolute_budgets = {}
        for component, percentage in base_budgets.items():
            absolute_budgets[component] = int(context_window * (percentage / 100.0))
        
        # Validate minimum memory requirement
        if minimum_memory_needed > absolute_budgets['conversation_memory']:
            # Reduce response allocation to accommodate minimum memory
            shortage = minimum_memory_needed - absolute_budgets['conversation_memory']
            
            # Try to take from reserved first
            available_reserved = absolute_budgets['reserved']
            if available_reserved >= shortage:
                absolute_budgets['reserved'] -= shortage
                absolute_budgets['conversation_memory'] = minimum_memory_needed
            else:
                # Take from response if necessary
                absolute_budgets['reserved'] = max(int(context_window * 0.02), 0)  # Keep 2% minimum
                remaining_shortage = shortage - available_reserved
                absolute_budgets['response_generation'] = max(
                    int(context_window * 0.10),  # Keep 10% minimum
                    absolute_budgets['response_generation'] - remaining_shortage
                )
                absolute_budgets['conversation_memory'] = minimum_memory_needed
        
        return absolute_budgets
    
    def validate_budget_allocation(self, budgets: Dict[str, int], context_window: int) -> Dict[str, any]:
        """
        Validate budget allocation and provide warnings
        
        Args:
            budgets: Dictionary of component -> token count
            context_window: Total context window size
            
        Returns:
            Validation results with detailed analysis
        """
        total_allocated = sum(budgets.values())
        utilization = (total_allocated / context_window) * 100
        
        result = {
            'is_valid': total_allocated <= context_window,
            'total_allocated': total_allocated,
            'context_window': context_window,
            'utilization_percent': round(utilization, 1),
            'remaining_tokens': context_window - total_allocated,
            'warnings': [],
            'recommendations': [],
            'budget_breakdown': {}
        }
        
        # Calculate percentages for breakdown
        for component, tokens in budgets.items():
            percentage = (tokens / context_window) * 100
            result['budget_breakdown'][component] = {
                'tokens': tokens,
                'percentage': round(percentage, 1)
            }
        
        # Validation checks
        if total_allocated > context_window:
            excess = total_allocated - context_window
            result['warnings'].append(f"Budget exceeds context window by {excess} tokens ({(excess/context_window)*100:.1f}%)")
            result['recommendations'].append("Reduce response or memory allocation")
        
        if utilization > 95:
            result['warnings'].append(f"Very high utilization: {utilization:.1f}%")
            result['recommendations'].append("Consider increasing safety margin")
        
        if budgets.get('response_generation', 0) < context_window * 0.10:
            result['warnings'].append("Response allocation very low (<10%)")
            result['recommendations'].append("May result in truncated responses")
        
        if budgets.get('conversation_memory', 0) < context_window * 0.30:
            result['warnings'].append("Memory allocation very low (<30%)")
            result['recommendations'].append("May lose important conversation context")
        
        return result
    
    def get_complexity_breakdown(self, user_input: str, mode: str = "chat") -> Dict[str, any]:
        """
        Get detailed breakdown of complexity analysis for debugging
        
        Args:
            user_input: User's input text
            mode: Interaction mode
            
        Returns:
            Detailed complexity analysis breakdown
        """
        if not user_input:
            return {'total_complexity': 0.0, 'factors': {}}
        
        text = user_input.strip().lower()
        text_length = len(text)
        
        factors = {
            'length': {
                'score': self._calculate_length_complexity(text_length),
                'weight': 0.25,
                'details': f"Text length: {text_length} chars"
            },
            'keywords': {
                'score': self._calculate_keyword_complexity(text, text_length),
                'weight': 0.30,
                'details': self._get_keyword_details(text)
            },
            'code': {
                'score': self._calculate_code_complexity(user_input),
                'weight': 0.25,
                'details': self._get_code_details(user_input)
            },
            'questions': {
                'score': self._calculate_question_complexity(text),
                'weight': 0.20,
                'details': self._get_question_details(text)
            }
        }
        
        # Calculate weighted total
        total_complexity = sum(
            factor['score'] * factor['weight'] 
            for factor in factors.values()
        )
        
        # Apply mode adjustment
        if mode == "tools":
            total_complexity *= 1.2
        
        total_complexity = max(0.0, min(1.0, total_complexity))
        
        return {
            'total_complexity': round(total_complexity, 3),
            'mode_adjustment': 1.2 if mode == "tools" else 1.0,
            'factors': factors
        }
    
    def _get_keyword_details(self, text: str) -> str:
        """Get details about detected keywords"""
        found_keywords = []
        for keyword in ComplexityFactors.ANALYSIS_KEYWORDS:
            if keyword in text:
                count = text.count(keyword)
                found_keywords.append(f"{keyword}({count})")
        
        return f"Keywords: {', '.join(found_keywords) if found_keywords else 'none'}"
    
    def _get_code_details(self, text: str) -> str:
        """Get details about detected code patterns"""
        code_matches = []
        for pattern in ComplexityFactors.CODE_PATTERNS:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                pattern_name = pattern.split('\\')[0][:10] + "..."
                code_matches.append(f"{pattern_name}({len(matches)})")
        
        return f"Code patterns: {', '.join(code_matches) if code_matches else 'none'}"
    
    def _get_question_details(self, text: str) -> str:
        """Get details about detected question patterns"""
        found_indicators = []
        for indicator in ComplexityFactors.QUESTION_INDICATORS:
            if indicator in text:
                found_indicators.append(indicator)
        
        question_count = text.count('?')
        details = f"Indicators: {', '.join(found_indicators) if found_indicators else 'none'}"
        if question_count > 0:
            details += f", Question marks: {question_count}"
        
        return details
