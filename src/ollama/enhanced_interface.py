"""
Enhanced Ollama interface with context-aware intelligence

This module provides an enhanced version of the Ollama interface that integrates
the new context-aware bot logic components for intelligent conversation handling.
"""

import logging
from typing import Optional, Dict, Any, Tuple, List

from .client import OllamaClient, get_default_client
from .tool_executor import ToolExecutor, get_default_executor
from .response_formatter import ResponseFormatter
from .legacy_interface import _execute_tool_call
from ..config import load_config
from ..memory import memory
from ..context_manager import ConversationContext
from ..enhanced_intent_classifier import EnhancedIntentClassifier
from ..smart_tool_selector import SmartToolSelector

from ..tool_schemas import get_all_tool_schemas
from ..exceptions import WorkspaceAIError, IntentError, ToolParameterError

logger = logging.getLogger(__name__)

# Global conversation context (singleton pattern for session persistence)
_global_context = None

def get_global_context() -> ConversationContext:
    """Get or create the global conversation context"""
    global _global_context
    if _global_context is None:
        # Create a session ID based on current time for uniqueness
        import time
        session_id = f"session_{int(time.time())}"
        _global_context = ConversationContext(session_id)
    return _global_context

# Initialize enhanced components
def get_enhanced_components():
    """Get enhanced components with current context"""
    context = get_global_context()
    
    # Create enhanced components with conversation context
    intent_classifier = EnhancedIntentClassifier(context)
    tool_selector = SmartToolSelector(context)
    response_formatter = ResponseFormatter()
    
    return (context, intent_classifier, tool_selector, response_formatter)


def call_ollama_with_enhanced_intelligence(
    prompt: str, 
    model: Optional[str] = None, 
    use_tools: bool = True,
    verbose_output: Optional[bool] = None
):
    """
    Enhanced Ollama interface with context-aware intelligence
    
    This function integrates the enhanced intent classification, smart tool selection,
    and conversation context management for intelligent bot behavior.
    
    Args:
        prompt: User input
        model: Optional model override
        use_tools: Whether to use tools
        verbose_output: Whether to show debug information (overrides config)
    """
    try:
        # Load configuration
        config = load_config()
        if verbose_output is None:
            verbose_output = config.get('verbose_output', False)
        
        # Get enhanced components
        components = get_enhanced_components()
        context, intent_classifier, tool_selector, response_formatter = components
        
        # Store the user message in memory first
        memory.add_message("user", prompt)
        
        if not use_tools:
            # Simple chat without tools
            response = _enhanced_simple_chat(prompt, model, context, verbose_output or False)
            
            # Just show the response directly - no conversational enhancement needed
            if response and response.get("success"):
                print(f"\n{response.get('result', '')}")
            
            return
        
        # Enhanced context-aware tool selection pipeline
        selected_tool_info, debug_info = enhanced_context_aware_pipeline(
            prompt, context, intent_classifier, tool_selector, verbose_output or False
        )
        
        # Execute based on confidence and context
        execution_result = _execute_with_context_awareness(
            prompt, model, selected_tool_info, debug_info, context, verbose_output or False
        )
        
        # Generate simple response - no conversational enhancement
        _generate_simple_response(execution_result)
        
        # Record operation in context for future reference
        _record_operation_in_context(prompt, selected_tool_info, execution_result, context)
        
    except Exception as e:
        logger.error(f"Error in enhanced Ollama call: {e}")
        
        # Record failed operation in context
        try:
            context = get_global_context()
            context.add_operation(
                operation_type="llm_request",
                tool_name="call_ollama_with_tools",
                parameters={"prompt": prompt[:100], "use_tools": use_tools},
                result=f"Error: {str(e)}",
                success=False,
                context_tags=["error", "llm_failure"]
            )
        except Exception as ctx_error:
            logger.error(f"Failed to record error in context: {ctx_error}")
        
        print(f"❌ An error occurred: {e}")





# Utility functions for context management


def enhanced_context_aware_pipeline(
    prompt: str, 
    context: ConversationContext,
    intent_classifier: EnhancedIntentClassifier,
    tool_selector: SmartToolSelector,
    verbose_output: bool = False
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Enhanced pipeline with context-aware intent classification and tool selection
    
    Returns:
        Tuple of (selected_tool_info, debug_info)
    """
    try:
        # Stage 1: Context-aware intent classification
        intent, confidence, context_info = intent_classifier.classify_with_context(prompt)
        
        # Stage 2: Smart tool selection with context
        tool_selection_result = tool_selector.select_tools_with_context(
            intent, prompt, confidence, context_info
        )
        
        # Stage 3: Enhanced confidence assessment
        enhanced_confidence = _assess_enhanced_confidence(
            tool_selection_result, context_info, context
        )
        
        # Combine results
        selected_tool_info = {
            **tool_selection_result,
            "enhanced_confidence": enhanced_confidence,
            "intent": intent,
            "intent_confidence": confidence
        }
        
        debug_info = {
            "context_info": context_info,
            "tool_selection": tool_selection_result,
            "enhanced_confidence": enhanced_confidence,
            "pipeline_stage": "enhanced_context_aware"
        }
        
        # Show debug information if requested
        if verbose_output:
            _print_enhanced_debug_info(selected_tool_info, debug_info)
        
        return selected_tool_info, debug_info
        
    except Exception as e:
        logger.error(f"Error in enhanced pipeline: {e}")
        # Fallback to basic classification
        from ..enhanced_intent_classifier import IntentClassifier
        from ..tool_selector import ContextWeightedToolSelector
        
        basic_classifier = IntentClassifier()
        basic_selector = ContextWeightedToolSelector()
        
        intent, confidence = basic_classifier.classify_with_confidence(prompt)
        selected_tool = basic_selector.select_tool(intent, prompt, confidence)
        
        return {
            "primary_tool": selected_tool,
            "confidence": confidence,
            "is_multi_step": False,
            "tool_sequence": [selected_tool],
            "fallback_mode": True
        }, {"error": str(e), "fallback_used": True}


def _assess_enhanced_confidence(
    tool_selection_result: Dict[str, Any],
    context_info: Optional[Dict[str, Any]],
    context: ConversationContext
) -> str:
    """Assess confidence level with enhanced criteria"""
    base_confidence = tool_selection_result.get("confidence", 0.0)
    
    # Factors that increase confidence
    confidence_boost = 0.0
    
    # Context factors
    if context_info:
        if context_info.get("input_analysis", {}).get("references_previous"):
            confidence_boost += 0.1  # User is referencing previous work
        
        if context_info.get("multi_step_detected", {}).get("is_multi_step"):
            confidence_boost += 0.05  # Multi-step operations are often deliberate
    
    # User pattern factors
    patterns = context.session.user_patterns
    if "preferred_tools" in patterns:
        primary_tool = tool_selection_result.get("primary_tool")
        if primary_tool in patterns["preferred_tools"]:
            confidence_boost += 0.15  # User has used this tool before
    
    # Recent success factors
    recent_ops = context.get_recent_operations(5)
    recent_successes = [op for op in recent_ops if op.success]
    if len(recent_successes) >= 3:
        confidence_boost += 0.1  # Recent successful operations
    
    # Calculate enhanced confidence
    enhanced_confidence = min(base_confidence + confidence_boost, 1.0)
    
    # Determine confidence level
    if enhanced_confidence > 0.85:
        return "VERY_HIGH_CONFIDENCE"
    elif enhanced_confidence > 0.7:
        return "HIGH_CONFIDENCE"
    elif enhanced_confidence > 0.5:
        return "MEDIUM_CONFIDENCE"
    elif enhanced_confidence > 0.3:
        return "LOW_CONFIDENCE"
    else:
        return "LLM_FALLBACK"


def _execute_with_context_awareness(
    prompt: str,
    model: Optional[str],
    selected_tool_info: Dict[str, Any],
    debug_info: Dict[str, Any],
    context: ConversationContext,
    verbose_output: bool = False
) -> Dict[str, Any]:
    """Execute with context awareness and intelligent fallback"""
    enhanced_confidence = selected_tool_info.get("enhanced_confidence", "LLM_FALLBACK")
    
    if enhanced_confidence in ["VERY_HIGH_CONFIDENCE", "HIGH_CONFIDENCE"]:
        # Try direct execution with high confidence
        return _try_direct_execution(selected_tool_info, prompt, verbose_output)
    
    elif enhanced_confidence == "MEDIUM_CONFIDENCE":
        # Try direct execution but with LLM guidance fallback
        direct_result = _try_direct_execution(selected_tool_info, prompt, verbose_output)
        if direct_result.get("success", False):
            return direct_result
        else:
            # Fall back to LLM guidance
            return _call_ollama_with_enhanced_guidance(
                prompt, model, selected_tool_info, debug_info, context
            )
    
    else:
        # Use LLM guidance for low confidence or fallback cases
        return _call_ollama_with_enhanced_guidance(
            prompt, model, selected_tool_info, debug_info, context
        )


def _try_direct_execution(
    selected_tool_info: Dict[str, Any],
    prompt: str,
    verbose_output: bool = False
) -> Dict[str, Any]:
    """Try direct tool execution without LLM involvement"""
    try:
        if selected_tool_info.get("is_multi_step", False):
            # Execute multi-step operation
            return _execute_multi_step_operation(selected_tool_info, prompt, verbose_output)
        else:
            # Execute single tool
            primary_tool = selected_tool_info.get("primary_tool")
            if not primary_tool:
                return {"success": False, "error": "No primary tool identified"}
            
            executor = get_default_executor()
            result = executor.execute_tool_directly(primary_tool, prompt, selected_tool_info, verbose_output)
            
            if result:
                print(f"\n{result}")
                memory.add_message("assistant", result)
                return {"success": True, "result": result, "execution_type": "direct"}
            else:
                return {"success": False, "error": "Direct execution failed"}
                
    except Exception as e:
        logger.error(f"Direct execution error: {e}")
        return {"success": False, "error": str(e)}


def _execute_multi_step_operation(
    selected_tool_info: Dict[str, Any],
    prompt: str,
    verbose_output: bool = False
) -> Dict[str, Any]:
    """Execute a multi-step operation sequence"""
    try:
        tool_sequence = selected_tool_info.get("tool_sequence", [])
        estimated_steps = selected_tool_info.get("estimated_steps", len(tool_sequence))
        
        if verbose_output:
            print(f"\n🔄 Executing multi-step operation ({estimated_steps} steps)")
        
        results = []
        executor = get_default_executor()
        
        for i, tool_name in enumerate(tool_sequence):
            if verbose_output:
                print(f"Step {i+1}/{len(tool_sequence)}: {tool_name}")
            
            # For multi-step, we'll need LLM guidance for each step
            # This is a simplified implementation
            step_result = executor.execute_tool_directly(tool_name, prompt, selected_tool_info, False)
            
            if step_result:
                results.append(step_result)
                if verbose_output:
                    print(f"✅ Step {i+1} completed")
            else:
                if verbose_output:
                    print(f"❌ Step {i+1} failed")
                break
        
        if results:
            combined_result = "\n".join(results)
            print(f"\n{combined_result}")
            memory.add_message("assistant", combined_result)
            return {"success": True, "result": combined_result, "execution_type": "multi_step", "steps_completed": len(results)}
        else:
            return {"success": False, "error": "Multi-step execution failed"}
            
    except Exception as e:
        logger.error(f"Multi-step execution error: {e}")
        return {"success": False, "error": str(e)}


def _call_ollama_with_enhanced_guidance(
    prompt: str,
    model: Optional[str],
    selected_tool_info: Dict[str, Any],
    debug_info: Dict[str, Any],
    context: ConversationContext
) -> Dict[str, Any]:
    """Call Ollama with enhanced guidance based on context"""
    try:
        client = get_default_client()
        if model:
            client.model = model
        
        # Build enhanced context messages
        context_messages = memory.get_context_messages()
        
        # Create enhanced guidance with context awareness
        guidance = _build_enhanced_guidance(selected_tool_info, debug_info, context)
        
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
            
            return {"success": True, "result": content, "tool_calls": tool_calls, "execution_type": "llm_guided"}
        else:
            print("❌ No response received from Ollama")
            return {"success": False, "error": "No response from Ollama"}
            
    except Exception as e:
        logger.error(f"Error in enhanced guided Ollama call: {e}")
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def _build_enhanced_guidance(
    selected_tool_info: Dict[str, Any],
    debug_info: Dict[str, Any],
    context: ConversationContext
) -> str:
    """Build enhanced guidance string with context awareness"""
    
    # Base guidance
    intent = selected_tool_info.get("intent", "UNKNOWN")
    confidence = selected_tool_info.get("intent_confidence", 0.0)
    primary_tool = selected_tool_info.get("primary_tool", "unknown")
    enhanced_confidence = selected_tool_info.get("enhanced_confidence", "UNKNOWN")
    
    guidance_parts = [
        "ENHANCED CONTEXT-AWARE GUIDANCE:",
        f"- Intent: {intent} (confidence: {confidence:.2f})",
        f"- Recommended tool: {primary_tool}",
        f"- Enhanced confidence: {enhanced_confidence}"
    ]
    
    # Add context information
    context_info = debug_info.get("context_info", {})
    if context_info:
        input_analysis = context_info.get("input_analysis", {})
        
        if input_analysis.get("references_previous"):
            guidance_parts.append("- User is referencing previous work")
        
        if input_analysis.get("mentions_specific_files"):
            files = input_analysis.get("file_references", [])
            if files:
                guidance_parts.append(f"- Mentioned files: {', '.join(files)}")
        
        multi_step = context_info.get("multi_step_detected", {})
        if multi_step.get("is_multi_step"):
            operation_type = multi_step.get("operation_type", "complex")
            estimated_steps = multi_step.get("estimated_steps", "multiple")
            guidance_parts.append(f"- Multi-step operation detected: {operation_type} ({estimated_steps} steps)")
    
    # Add user patterns
    patterns = context.session.user_patterns
    if "preferred_tools" in patterns and patterns["preferred_tools"]:
        top_tools = list(patterns["preferred_tools"].keys())[:3]
        guidance_parts.append(f"- User's preferred tools: {', '.join(top_tools)}")
    
    # Add recent context
    recent_operations = context.get_recent_operations(3)
    if recent_operations:
        recent_files = []
        for op in recent_operations:
            if op.operation_type in ["file_creation", "file_modification"]:
                file_name = op.parameters.get("file_name")
                if file_name and file_name not in recent_files:
                    recent_files.append(file_name)
        
        if recent_files:
            guidance_parts.append(f"- Recent files worked on: {', '.join(recent_files[:3])}")
    
    guidance_parts.append("\nPlease use this context to provide the most appropriate response and tool selection.")
    
    return "\n".join(guidance_parts)





def _generate_simple_response(execution_result: Dict[str, Any]):
    """Generate simple, direct response without conversational fluff"""
    if execution_result.get("success", False):
        print("✅ Operation completed successfully")
    else:
        error_msg = execution_result.get("error", "Unknown error")
        print(f"❌ Operation failed: {error_msg}")


def _enhanced_simple_chat(prompt: str, model: Optional[str], context: ConversationContext, verbose_output: bool = False) -> Dict[str, Any]:
    """Simple chat without conversational enhancement"""
    try:
        client = get_default_client()
        if model:
            client.model = model
        
        response = client.simple_chat(prompt)
        if response:
            print(f"\n{response}")
            memory.add_message("assistant", response)
            return {"success": True, "result": response}
        else:
            print("❌ No response received from Ollama")
            return {"success": False, "error": "No response from Ollama"}
            
    except Exception as e:
        logger.error(f"Simple chat error: {e}")
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}



def _record_operation_in_context(
    prompt: str,
    selected_tool_info: Dict[str, Any],
    execution_result: Dict[str, Any],
    context: ConversationContext
):
    """Record the operation in conversation context for future reference"""
    try:
        operation_type = "llm_request"
        tool_name = selected_tool_info.get("primary_tool", "unknown")
        success = execution_result.get("success", False)
        result_summary = str(execution_result.get("result", ""))[:200]
        
        # Determine context tags
        tags = []
        if selected_tool_info.get("is_multi_step"):
            tags.append("multi_step")
        if selected_tool_info.get("enhanced_confidence") in ["VERY_HIGH_CONFIDENCE", "HIGH_CONFIDENCE"]:
            tags.append("high_confidence")
        if execution_result.get("execution_type"):
            tags.append(execution_result["execution_type"])
        
        context.add_operation(
            operation_type=operation_type,
            tool_name=tool_name,
            parameters={
                "prompt": prompt[:100],
                "confidence": selected_tool_info.get("enhanced_confidence", "unknown"),
                "intent": selected_tool_info.get("intent", "unknown")
            },
            result=result_summary,
            success=success,
            context_tags=tags
        )
        
    except Exception as e:
        logger.error(f"Failed to record operation in context: {e}")


def _print_enhanced_debug_info(selected_tool_info: Dict[str, Any], debug_info: Dict[str, Any]):
    """Print enhanced debug information"""
    print("\n" + "="*50)
    print("ENHANCED CONTEXT-AWARE DEBUG INFO")
    print("="*50)
    
    # Intent and confidence
    intent = selected_tool_info.get("intent", "UNKNOWN")
    intent_confidence = selected_tool_info.get("intent_confidence", 0.0)
    enhanced_confidence = selected_tool_info.get("enhanced_confidence", "UNKNOWN")
    
    print(f"Intent: {intent} (confidence: {intent_confidence:.2f})")
    print(f"Enhanced Confidence: {enhanced_confidence}")
    
    # Tool selection
    primary_tool = selected_tool_info.get("primary_tool", "unknown")
    is_multi_step = selected_tool_info.get("is_multi_step", False)
    
    print(f"Primary Tool: {primary_tool}")
    print(f"Multi-step: {is_multi_step}")
    
    if is_multi_step:
        tool_sequence = selected_tool_info.get("tool_sequence", [])
        print(f"Tool Sequence: {' → '.join(tool_sequence)}")
    
    # Context factors
    context_factors = selected_tool_info.get("context_factors", {})
    if context_factors:
        print("\nContext Factors:")
        for factor, value in context_factors.items():
            print(f"  - {factor}: {value}")
    
    print("="*50)


# Enhanced detection functions
def detect_file_intent_enhanced(prompt: str) -> bool:
    """Enhanced file intent detection with hybrid fallback for accuracy"""
    try:
        context = get_global_context()
        intent_classifier = EnhancedIntentClassifier(context)
        
        intent, confidence, context_info = intent_classifier.classify_with_context(prompt)
        
        # Enhanced file intent detection
        file_intents = ['CONTENT_CREATION', 'FILE_MANAGEMENT', 'CONTENT_CONTINUATION']
        base_file_intent = intent in file_intents and confidence > 0.3
        
        # Context-based enhancement
        if context_info:
            input_analysis = context_info.get("input_analysis", {})
            if input_analysis.get("mentions_specific_files"):
                return True  # Definitely file-related
        
        # HYBRID FALLBACK: If enhanced classifier returns UNCLEAR or low confidence,
        # fall back to basic regex patterns for obvious file operations
        if intent == 'UNCLEAR' or confidence < 0.3:
            return _basic_file_intent_patterns(prompt)
        
        return base_file_intent
        
    except Exception as e:
        logger.error(f"Enhanced file intent detection failed: {e}")
        # Fallback to basic detection
        return _basic_file_intent_patterns(prompt)


def _basic_file_intent_patterns(prompt: str) -> bool:
    """Basic regex pattern matching for clear file operations"""
    import re
    
    # Clear file operation patterns that should always trigger tools
    file_patterns = [
        r'\b(create|make|generate|build)\s+.*\b(file|folder|directory)\b',
        r'\b(save|write|store|put)\s+.*\b(to|in|into)\s+.*\b(workspace|folder|directory)\b', 
        r'\b(read|open|view|show|display)\s+.*\b(file|document)\b',
        r'\b(copy|move|delete|backup|remove)\s+.*\b(file|folder)\b',
        r'\blist\s+(all\s+)?files\b',
        r'\bsearch\s+for\s+.*\bfile',
        r'\bfind\s+.*\bfile',
        r'\bcopy\s+\w+\.\w+\s+to\s+\w+\.\w+',  # copy file.ext to file2.ext
        r'\bmove\s+\w+\.\w+\s+to\s+\w+\.\w+',  # move file.ext to file2.ext  
        r'\bdelete\s+\w+\.\w+',                # delete file.ext
        r'\bremove\s+\w+\.\w+',                # remove file.ext
        r'\bbackup\s+\w+\.\w+',                # backup file.ext
        r'\bcompress\s+.*\bfile',
        r'\bzip\s+.*\bfile'
    ]
    
    prompt_lower = prompt.lower()
    
    # Check for clear file operation patterns
    for pattern in file_patterns:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            return True
    
    # Check for file extensions (strong indicator of file operations)
    if re.search(r'\.\w{2,4}\b', prompt):  # .txt, .json, .py, etc.
        return True
    
    return False


# Backward compatibility function - enhanced version
def call_ollama_with_tools(prompt: str, model: Optional[str] = None, use_tools: bool = True):
    """
    Enhanced backward-compatible interface
    
    This function maintains the original signature but uses the enhanced
    context-aware intelligence under the hood.
    """
    # Check if enhanced mode is enabled in config
    config = load_config()
    use_enhanced = config.get('use_enhanced_intelligence', True)
    
    if use_enhanced:
        # Use the new enhanced interface
        call_ollama_with_enhanced_intelligence(prompt, model, use_tools)
    else:
        # Use the legacy interface
        from .legacy_interface import call_ollama_with_tools as legacy_call
        legacy_call(prompt, model, use_tools)


# Utility functions for context management
def reset_conversation_context():
    """Reset the global conversation context (useful for testing or new sessions)"""
    global _global_context
    _global_context = None
    

def get_conversation_stats() -> Dict[str, Any]:
    """Get statistics about the current conversation context"""
    context = get_global_context()
    
    # Convert start_time if it's a timestamp
    start_time = context.session.start_time
    if isinstance(start_time, (int, float)):
        import datetime
        start_time_str = datetime.datetime.fromtimestamp(start_time).isoformat()
    else:
        start_time_str = str(start_time)
    
    return {
        "session_id": context.session_id,
        "operations_count": len(context.session.operation_history),
        "files_tracked": len(context.session.file_state),
        "user_patterns": dict(context.session.user_patterns),
        "session_start": start_time_str
    }


# Backward compatibility exports
def detect_file_intent(prompt: str) -> bool:
    """
    Backward compatible file intent detection
    Uses the enhanced version but maintains original signature
    """
    return detect_file_intent_enhanced(prompt)


def test_ollama_connection():
    """
    Test Ollama connection with enhanced error handling
    """
    try:
        # Test using the enhanced client
        client = get_default_client()
        return client.test_connection()
    except Exception as e:
        logger.error(f"Enhanced connection test failed: {e}")
        # Fallback to legacy test
        try:
            from .legacy_interface import test_ollama_connection as legacy_test
            return legacy_test()
        except Exception as legacy_error:
            logger.error(f"Legacy connection test also failed: {legacy_error}")
            return False
