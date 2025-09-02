"""
Tests for enhanced_interface module (compatibility layer)
"""
import pytest
from unittest.mock import patch, MagicMock
from src.enhanced_interface import (
    detect_file_intent,
    call_ollama_with_enhanced_intelligence,
    get_enhanced_components,
    enhanced_context_aware_pipeline,
    get_conversation_stats,
    reset_conversation_context
)


class TestEnhancedInterface:
    """Test the enhanced interface compatibility layer"""
    
    @patch('src.enhanced_interface._detect_file_intent')
    def test_detect_file_intent_proxy(self, mock_detect):
        """Test detect_file_intent proxies to app module"""
        mock_detect.return_value = True
        
        result = detect_file_intent("create test.py")
        
        assert result is True
        mock_detect.assert_called_once_with("create test.py")
    
    @patch('src.enhanced_interface.call_ollama_with_universal_tools')
    def test_call_ollama_with_enhanced_intelligence_default_params(self, mock_call):
        """Test enhanced intelligence call with default parameters"""
        mock_call.return_value = {"message": "test response"}
        
        result = call_ollama_with_enhanced_intelligence("test prompt")
        
        assert result == {"message": "test response"}
        mock_call.assert_called_once_with("test prompt", None, True, False)
    
    @patch('src.enhanced_interface.call_ollama_with_universal_tools')
    def test_call_ollama_with_enhanced_intelligence_custom_params(self, mock_call):
        """Test enhanced intelligence call with custom parameters"""
        mock_call.return_value = {"success": True}
        
        result = call_ollama_with_enhanced_intelligence(
            "custom prompt", 
            model="llama3.2", 
            use_tools=False, 
            verbose_output=True
        )
        
        assert result == {"success": True}
        mock_call.assert_called_once_with("custom prompt", "llama3.2", False, True)


class TestEnhancedComponents:
    """Test the enhanced components compatibility layer"""
    
    def test_get_enhanced_components_structure(self):
        """Test that enhanced components returns expected structure"""
        context_builder, intent_classifier, tool_selector = get_enhanced_components()
        
        # Test that all components exist
        assert hasattr(context_builder, 'add_operation')
        assert hasattr(intent_classifier, 'classify_with_context')
        assert hasattr(tool_selector, 'select_tools_with_context')
    
    def test_context_builder_add_operation(self):
        """Test context builder add_operation method"""
        context_builder, _, _ = get_enhanced_components()
        
        # Should not raise an exception
        context_builder.add_operation("test", "operation", {"param": "value"})
        context_builder.add_operation()  # No args should also work
    
    @patch('src.enhanced_interface.detect_file_intent')
    def test_intent_classifier_classify_with_context(self, mock_detect):
        """Test intent classifier classify_with_context method"""
        mock_detect.return_value = True
        _, intent_classifier, _ = get_enhanced_components()
        
        intent, confidence, context = intent_classifier.classify_with_context("test prompt")
        
        assert intent is True
        assert confidence == 1.0
        assert context == []
        mock_detect.assert_called_once_with("test prompt")
    
    def test_tool_selector_select_tools_with_context(self):
        """Test tool selector select_tools_with_context method"""
        _, _, tool_selector = get_enhanced_components()
        
        result = tool_selector.select_tools_with_context(
            intent=True, 
            prompt="test", 
            confidence=0.8, 
            context_info={"test": "data"}
        )
        
        expected = {
            'primary_tool': 'none', 
            'suggested_parameters': {}, 
            'confidence': 0.8
        }
        assert result == expected


class TestEnhancedPipeline:
    """Test enhanced pipeline compatibility functions"""
    
    def test_enhanced_context_aware_pipeline(self):
        """Test enhanced context-aware pipeline returns expected structure"""
        result, debug_info = enhanced_context_aware_pipeline(
            "test prompt", 
            context={"test": "context"}, 
            intent_classifier=MagicMock(), 
            tool_selector=MagicMock(),
            verbose_output=True
        )
        
        assert result == {'enhanced_confidence': 1.0}
        assert debug_info == {'context_info': {}}
    
    def test_enhanced_context_aware_pipeline_minimal_params(self):
        """Test pipeline with minimal parameters"""
        result, debug_info = enhanced_context_aware_pipeline(
            "minimal test", 
            None, 
            None, 
            None
        )
        
        assert result == {'enhanced_confidence': 1.0}
        assert debug_info == {'context_info': {}}


class TestConversationFunctions:
    """Test conversation management functions"""
    
    def test_get_conversation_stats(self):
        """Test conversation stats returns expected structure"""
        stats = get_conversation_stats()
        
        expected = {'total_messages': 0, 'tools_used': 0}
        assert stats == expected
    
    def test_reset_conversation_context(self):
        """Test reset conversation context doesn't raise errors"""
        # Should not raise any exceptions
        reset_conversation_context()
        
        # Call multiple times to ensure it's stable
        reset_conversation_context()
        reset_conversation_context()


class TestIntegration:
    """Integration tests for enhanced interface"""
    
    @patch('src.enhanced_interface._detect_file_intent')
    @patch('src.enhanced_interface.call_ollama_with_universal_tools')
    def test_full_workflow_integration(self, mock_call, mock_detect):
        """Test full workflow using enhanced interface"""
        mock_detect.return_value = True
        mock_call.return_value = {"response": "File created successfully"}
        
        # Get components
        context_builder, intent_classifier, tool_selector = get_enhanced_components()
        
        # Simulate workflow
        prompt = "create new_file.py"
        
        # Classify intent
        intent, confidence, context = intent_classifier.classify_with_context(prompt)
        assert intent is True
        
        # Select tools
        tool_selection = tool_selector.select_tools_with_context(intent, prompt, confidence, context)
        assert tool_selection['primary_tool'] == 'none'
        
        # Call enhanced intelligence
        result = call_ollama_with_enhanced_intelligence(prompt, use_tools=True)
        assert result == {"response": "File created successfully"}
        
        # Get stats
        stats = get_conversation_stats()
        assert stats['total_messages'] == 0
        
        # Reset context
        reset_conversation_context()  # Should not raise
