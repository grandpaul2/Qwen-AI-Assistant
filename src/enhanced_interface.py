"""
Stub for enhanced_interface (previously src.ollama.enhanced_interface)
Provides wrappers to flat detect_file_intent and tool calling API for system scripts.
"""
from src.app import detect_file_intent as _detect_file_intent
from src.ollama_universal_interface import call_ollama_with_universal_tools


def detect_file_intent(prompt: str) -> bool:
    """Proxy detect_file_intent using core app logic"""
    return _detect_file_intent(prompt)


def call_ollama_with_enhanced_intelligence(prompt: str, model: str = None, use_tools: bool = True, verbose_output: bool = False):
    """Proxy to call the universal tools interface"""
    return call_ollama_with_universal_tools(prompt, model, use_tools, verbose_output)


def get_enhanced_components():
    """Provide dummy components for system scripts"""
    class ContextBuilder:
        def add_operation(self, *args, **kwargs):
            pass
    class IntentClassifier:
        def classify_with_context(self, prompt: str) -> tuple[bool, float, list]:
            return detect_file_intent(prompt), 1.0, []
    class ToolSelector:
        def select_tools_with_context(self, intent, prompt, confidence, context_info) -> dict:
            return {'primary_tool': 'none', 'suggested_parameters': {}, 'confidence': confidence}
    return ContextBuilder(), IntentClassifier(), ToolSelector()

def enhanced_context_aware_pipeline(prompt: str, context, intent_classifier, tool_selector, verbose_output: bool = False):
    """Stub for enhanced context-aware pipeline"""
    # Return dummy result and debug info
    result = {'enhanced_confidence': 1.0}
    debug_info = {'context_info': {}}
    return result, debug_info

def get_conversation_stats():
    """Stub for conversation stats"""
    return {'total_messages': 0, 'tools_used': 0}

def reset_conversation_context():
    """Stub to reset conversation context"""
    pass
