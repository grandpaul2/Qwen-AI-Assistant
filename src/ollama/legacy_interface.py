"""
Legacy interface for backward compatibility

Maintains the original function signatures while using the new modular components.
"""

import logging
from typing import Optional, Dict, Any, Tuple

from .client import OllamaClient, get_default_client
from .tool_executor import ToolExecutor, get_default_executor
from .response_formatter import ResponseFormatter
from ..config import load_config
from ..memory import memory
from ..intent_classifier import IntentClassifier
from ..tool_selector import ContextWeightedToolSelector
from ..tool_schemas import get_all_tool_schemas

logger = logging.getLogger(__name__)

# Initialize components for legacy functions
intent_classifier = IntentClassifier()
tool_selector = ContextWeightedToolSelector()
response_formatter = ResponseFormatter()


def enhanced_tool_selection_pipeline(prompt: str, verbose_output: bool = False) -> Tuple[str, str, Dict]:
    """
    Enhanced three-stage tool selection pipeline (legacy interface)
    
    Args:
        prompt: User input string
        verbose_output: Whether to show debug information
        
    Returns:
        Tuple of (selected_tool, confidence_level, debug_info)
    """
    # Stage 1: Intent Classification
    intent, confidence = intent_classifier.classify_with_confidence(prompt)
    
    # Stage 2: Tool Selection with Context Weighting
    total_weight, word_breakdown = tool_selector.calculate_context_weight(prompt)
    selected_tool = tool_selector.select_tool(intent, prompt, confidence)
    
    # Stage 3: Determine confidence level
    if confidence > 0.8 and total_weight > 10:
        confidence_level = "HIGH_CONFIDENCE"
    elif confidence > 0.5 and total_weight > 5:
        confidence_level = "MEDIUM_CONFIDENCE"
    else:
        confidence_level = "LLM_FALLBACK"
    
    # Debug information
    debug_info = {
        'intent': intent,
        'intent_confidence': confidence,
        'total_weight': total_weight,
        'word_breakdown': word_breakdown,
        'selected_tool': selected_tool,
        'confidence_level': confidence_level
    }
    
    # Print debug information only if verbose
    if verbose_output:
        print(response_formatter.format_debug_info(debug_info))
    
    return selected_tool, confidence_level, debug_info


def should_use_enhanced_selection(prompt: str) -> bool:
    """Check if enhanced selection should be used (legacy interface)"""
    # Simple heuristic - use enhanced selection for most requests
    # Can be made more sophisticated later
    return len(prompt.strip()) > 5


def detect_file_intent(prompt: str) -> bool:
    """
    Detect if prompt indicates file management intent (legacy interface)
    
    Args:
        prompt: User input
        
    Returns:
        True if file operation is likely intended
    """
    # Use the intent classifier
    intent, confidence = intent_classifier.classify_with_confidence(prompt)
    
    # Consider file intent if classified as content creation or file management
    file_intents = ['CONTENT_CREATION', 'FILE_MANAGEMENT']
    return intent in file_intents and confidence > 0.3


def test_ollama_connection() -> bool:
    """Test connection to Ollama server (legacy interface)"""
    client = get_default_client()
    return client.test_connection()


def call_ollama_with_tools(prompt: str, model: Optional[str] = None, use_tools: bool = True):
    """
    Main function for calling Ollama with tool support (legacy interface)
    
    Args:
        prompt: User input
        model: Optional model override
        use_tools: Whether to use tools
    """
    try:
        # Load configuration
        config = load_config()
        verbose_output = config.get('verbose_output', False)
        
        # Store the user message in memory first
        memory.add_message("user", prompt)
        
        if not use_tools:
            # Simple chat without tools
            client = get_default_client()
            if model:
                client.model = model
            
            response = client.simple_chat(prompt)
            if response:
                print(f"\n{response}")
                memory.add_message("assistant", response)
            else:
                print("❌ No response received from Ollama")
            return
        
        # Enhanced tool selection pipeline
        selected_tool, confidence_level, debug_info = enhanced_tool_selection_pipeline(prompt, verbose_output)
        
        if confidence_level == "HIGH_CONFIDENCE":
            # Try direct execution first
            executor = get_default_executor()
            result = executor.execute_tool_directly(selected_tool, prompt, debug_info, verbose_output)
            
            if result:
                print(f"\n{result}")
                memory.add_message("assistant", result)
                return
        
        # Fall back to LLM-guided execution
        _call_ollama_with_guidance(prompt, model, selected_tool, debug_info)
        
    except Exception as e:
        logger.error(f"Error in call_ollama_with_tools: {e}")
        print(f"❌ An error occurred: {e}")


def _call_ollama_with_guidance(prompt: str, model: Optional[str], selected_tool: str, debug_info: Dict):
    """Call Ollama with guidance about tool selection"""
    try:
        client = get_default_client()
        if model:
            client.model = model
        
        # Build context messages from memory
        context_messages = memory.get_context_messages()
        
        # Add guidance about tool selection
        guidance = f"""
ENHANCED TOOL SELECTION GUIDANCE:
- Intent: {debug_info['intent']} (confidence: {debug_info['intent_confidence']:.2f})
- Context weight: {debug_info['total_weight']} {debug_info['word_breakdown']}
- Recommended tool: {selected_tool}

Please use the recommended tool if appropriate for the user's request.
"""
        
        if context_messages:
            context_messages.append({"role": "system", "content": guidance})
        else:
            context_messages = [
                {"role": "system", "content": guidance},
                {"role": "user", "content": prompt}
            ]
        
        # Get available tools
        tools = get_all_tool_schemas()
        
        # Make the API call
        response = client.chat_completion(context_messages, tools)
        
        if response and "message" in response:
            message = response["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])
            
            if tool_calls:
                # Execute tool calls
                for tool_call in tool_calls:
                    _execute_tool_call(tool_call)
            
            if content:
                print(f"\n{content}")
                memory.add_message("assistant", content, tool_calls)
        else:
            print("❌ No response received from Ollama")
            
    except Exception as e:
        logger.error(f"Error in guided Ollama call: {e}")
        print(f"❌ Error: {e}")


def _execute_tool_call(tool_call: Dict[str, Any]):
    """Execute a single tool call from the LLM response"""
    try:
        function = tool_call.get("function", {})
        function_name = function.get("name", "")
        function_args = function.get("arguments", {})
        
        # Parse arguments if they're a string
        if isinstance(function_args, str):
            import json
            function_args = json.loads(function_args)
        
        # Execute using tool executor
        executor = get_default_executor()
        result = executor._execute_function(function_name, function_args)
        
        if result:
            formatted_result = response_formatter.format_tool_result(function_name, result)
            print(f"\n{formatted_result}")
        else:
            print(f"❌ Tool execution failed: {function_name}")
            
    except Exception as e:
        logger.error(f"Error executing tool call: {e}")
        print(f"❌ Tool execution error: {e}")


# Additional legacy functions for compatibility
def enhance_prompt_for_function_selection(prompt: str) -> str:
    """Enhance prompt for better function selection (legacy)"""
    return prompt  # Now handled by the new pipeline


def auto_correct_function_name(function_name: str) -> Tuple[str, bool]:
    """Auto-correct function names (legacy interface)"""
    from .function_validator import FunctionValidator
    validator = FunctionValidator()
    return validator.auto_correct_function_name(function_name)


def auto_correct_parameters(function_name: str, original_function: str, function_args: Dict) -> Dict:
    """Auto-correct parameters (legacy interface)"""
    from .function_validator import FunctionValidator
    validator = FunctionValidator()
    return validator.auto_correct_parameters(function_name, original_function, function_args)
