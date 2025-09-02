"""
Comprehensive Unit Tests for Enhanced Ollama Interface

Tests the enhanced context-aware interface that integrates smart tool selection,
conversation context management, and intelligent execution strategies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from typing import Dict, Any, Optional

from src.ollama.enhanced_interface import (
    call_ollama_with_enhanced_intelligence,
    enhanced_context_aware_pipeline,
    detect_file_intent_enhanced,
    get_conversation_stats,
    reset_conversation_context,
    get_global_context,
    get_enhanced_components
)


class TestEnhancedInterface(unittest.TestCase):
    """Test cases for enhanced Ollama interface functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset global context before each test
        reset_conversation_context()
        
    def tearDown(self):
        """Clean up after each test"""
        reset_conversation_context()

    def test_get_global_context_singleton(self):
        """Test that global context maintains singleton pattern"""
        context1 = get_global_context()
        context2 = get_global_context()
        
        assert context1 is context2
        assert context1 is not None
        assert hasattr(context1, 'session_id')
        
    def test_reset_conversation_context(self):
        """Test conversation context reset functionality"""
        # Get initial context
        context = get_global_context()
        initial_session_id = context.session_id
        
        # Add some operations
        context.add_operation("test", "test_tool", {}, "result", True)
        operations_before = len(context.session.operation_history)
        
        # Reset and verify it's cleaned
        reset_conversation_context()
        new_context = get_global_context()
        
        # Should be a new instance with clean state
        assert new_context is not context  # Different object
        assert len(new_context.session.operation_history) == 0
        assert operations_before > 0  # Verify we had data before reset
        
    def test_get_enhanced_components(self):
        """Test enhanced components initialization"""
        components = get_enhanced_components()
        assert len(components) == 4
        
        context, classifier, selector, formatter = components
        
        assert context is not None
        assert classifier is not None
        assert selector is not None
        assert formatter is not None
        assert hasattr(classifier, 'classify_with_context')
        assert hasattr(selector, 'select_tools_with_context')

    @patch('src.ollama.enhanced_interface.load_config')
    @patch('src.ollama.enhanced_interface.EnhancedIntentClassifier')
    def test_detect_file_intent_enhanced_true(self, mock_classifier_class, mock_config):
        """Test enhanced file intent detection - positive case"""
        mock_config.return_value = {'verbose_output': False}
        
        # Mock the classifier instance
        mock_classifier = Mock()
        mock_classifier.classify_with_context.return_value = (
            "FILE_MANAGEMENT", 
            0.8, 
            {"input_analysis": {"mentions_specific_files": True}}
        )
        mock_classifier_class.return_value = mock_classifier
        
        file_prompts = [
            "create a new file called test.py",
            "read the contents of config.json"
        ]
        
        for prompt in file_prompts:
            with self.subTest(prompt=prompt):
                result = detect_file_intent_enhanced(prompt)
                assert result is True

    @patch('src.ollama.enhanced_interface.load_config')
    @patch('src.ollama.enhanced_interface.EnhancedIntentClassifier')
    def test_detect_file_intent_enhanced_false(self, mock_classifier_class, mock_config):
        """Test enhanced file intent detection - negative case"""
        mock_config.return_value = {'verbose_output': False}
        
        # Mock the classifier instance
        mock_classifier = Mock()
        mock_classifier.classify_with_context.return_value = (
            "CONVERSATION", 
            0.8, 
            {"input_analysis": {"mentions_specific_files": False}}
        )
        mock_classifier_class.return_value = mock_classifier
        
        non_file_prompts = [
            "what is the weather today",
            "explain machine learning"
        ]
        
        for prompt in non_file_prompts:
            with self.subTest(prompt=prompt):
                result = detect_file_intent_enhanced(prompt)
                assert result is False

    def test_get_conversation_stats_empty(self):
        """Test conversation stats with empty context"""
        stats = get_conversation_stats()
        
        assert 'session_id' in stats
        assert 'operations_count' in stats
        assert 'files_tracked' in stats
        assert 'user_patterns' in stats
        assert 'session_start' in stats
        
        assert stats['operations_count'] == 0
        assert stats['files_tracked'] == 0

    def test_get_conversation_stats_with_data(self):
        """Test conversation stats with operation data"""
        context = get_global_context()
        
        # Add some operations
        context.add_operation("file_operation", "create_file", {"filename": "test.py"}, "Created successfully", True)
        context.add_operation("file_operation", "read_file", {"filename": "test.py"}, "File content", True)
        context.add_operation("llm_request", "call_ollama", {"prompt": "test"}, "Error occurred", False)
        
        stats = get_conversation_stats()
        
        assert stats['operations_count'] == 3
        assert stats['files_tracked'] >= 0  # Depends on implementation

    @patch('src.ollama.enhanced_interface._assess_enhanced_confidence')
    @patch('src.ollama.enhanced_interface.get_enhanced_components')
    @patch('src.ollama.enhanced_interface.load_config')
    def test_enhanced_context_aware_pipeline_high_confidence(self, mock_config, mock_components, mock_assess):
        """Test enhanced pipeline with high confidence selection"""
        mock_config.return_value = {'verbose_output': False}
        
        # Mock components
        mock_context = Mock()
        mock_classifier = Mock()
        mock_selector = Mock()
        mock_formatter = Mock()
        mock_components.return_value = (mock_context, mock_classifier, mock_selector, mock_formatter)
        
        # Mock classification and selection
        mock_classifier.classify_with_context.return_value = ("file_operation", 0.95, {"context": "file"})
        mock_selector.select_tools_with_context.return_value = {
            'primary_tool': 'create_file',
            'confidence_level': 'HIGH_CONFIDENCE',
            'confidence_score': 0.95,
            'is_multi_step': False,
            'reasoning': 'Clear file creation intent'
        }
        
        # Mock enhanced confidence assessment
        mock_assess.return_value = "HIGH_CONFIDENCE"
        
        context, intent_classifier, tool_selector, _ = mock_components.return_value
        result, debug_info = enhanced_context_aware_pipeline(
            "create a file called test.py", context, intent_classifier, tool_selector
        )
        
        assert result['primary_tool'] == 'create_file'
        assert result['enhanced_confidence'] == "HIGH_CONFIDENCE"
        assert debug_info is not None

    @patch('src.ollama.enhanced_interface.load_config')
    @patch('src.ollama.enhanced_interface.enhanced_context_aware_pipeline')
    @patch('src.ollama.enhanced_interface.memory')
    def test_call_ollama_with_enhanced_intelligence_success(self, mock_memory, mock_pipeline, mock_config):
        """Test successful enhanced intelligence call"""
        mock_config.return_value = {'verbose_output': False}
        
        # Mock pipeline response
        mock_pipeline.return_value = (
            {
                'primary_tool': 'create_file',
                'confidence_level': 'HIGH_CONFIDENCE',
                'is_multi_step': False
            },
            {'debug': 'info'}
        )
        
        with patch('src.ollama.enhanced_interface._execute_with_context_awareness') as mock_execute:
            mock_execute.return_value = {'success': True, 'result': 'File created'}
            
            with patch('builtins.print') as mock_print:
                call_ollama_with_enhanced_intelligence("create test.py")
                
                mock_pipeline.assert_called_once()
                mock_memory.add_message.assert_called()

    @patch('src.ollama.enhanced_interface.load_config')
    def test_call_ollama_with_enhanced_intelligence_no_tools(self, mock_config):
        """Test enhanced intelligence call with tools disabled"""
        mock_config.return_value = {'verbose_output': False}
        
        with patch('src.ollama.enhanced_interface._enhanced_simple_chat') as mock_simple_chat:
            mock_simple_chat.return_value = {"success": True, "result": "Simple response"}
            
            with patch('builtins.print') as mock_print, \
                 patch('src.ollama.enhanced_interface.memory') as mock_memory:
                
                call_ollama_with_enhanced_intelligence("hello", use_tools=False)
                
                mock_simple_chat.assert_called_once()

    @patch('src.ollama.enhanced_interface.logger')
    def test_error_handling_in_enhanced_call(self, mock_logger):
        """Test error handling in enhanced intelligence call"""
        with patch('src.ollama.enhanced_interface.get_enhanced_components') as mock_components:
            mock_components.side_effect = Exception("Components error")
            
            with patch('builtins.print') as mock_print:
                call_ollama_with_enhanced_intelligence("test prompt")
                
                mock_logger.error.assert_called()
                mock_print.assert_called_with("❌ An error occurred: Components error")

    def test_conversation_context_persistence(self):
        """Test that conversation context persists across calls"""
        context1 = get_global_context()
        context1.add_operation("test", "test_tool", {}, "result", True)
        
        # Get context again - should be same instance with data
        context2 = get_global_context()
        assert context1 is context2
        
        # Reset should clear it
        reset_conversation_context()
        context3 = get_global_context()
        assert context3 is not context1


class TestEnhancedInterfaceIntegration(unittest.TestCase):
    """Integration tests for enhanced interface components"""

    def setUp(self):
        """Set up integration test fixtures"""
        reset_conversation_context()

    def tearDown(self):
        """Clean up after integration tests"""
        reset_conversation_context()

    @patch('src.ollama.enhanced_interface.load_config')
    def test_full_pipeline_integration(self, mock_config):
        """Test full pipeline integration with real components"""
        mock_config.return_value = {'verbose_output': False}
        
        # Get real components
        context, intent_classifier, tool_selector, _ = get_enhanced_components()
        
        # Test with a clear file operation
        result, debug_info = enhanced_context_aware_pipeline(
            "create a file called integration_test.py", 
            context, intent_classifier, tool_selector
        )
        
        # Should return a well-formed response
        assert 'primary_tool' in result or 'tool_sequence' in result
        assert debug_info is not None

    def test_context_accumulation(self):
        """Test that context accumulates across operations"""
        context = get_global_context()
        
        # Simulate multiple operations
        for i in range(3):
            context.add_operation(
                f"test_operation_{i}", 
                f"test_tool_{i}", 
                {"param": f"value_{i}"}, 
                f"result_{i}", 
                True
            )
        
        stats = get_conversation_stats()
        assert stats['operations_count'] == 3

    @patch('src.ollama.enhanced_interface.load_config')
    def test_enhanced_components_real_integration(self, mock_config):
        """Test that enhanced components work together correctly"""
        mock_config.return_value = {'verbose_output': False}
        
        # Get real components and verify they can work together
        context, intent_classifier, tool_selector, formatter = get_enhanced_components()
        
        # Test intent classification
        intent, confidence, context_info = intent_classifier.classify_with_context("create a file")
        assert intent is not None
        assert isinstance(confidence, (int, float))
        assert context_info is not None
        
        # Test tool selection
        tool_result = tool_selector.select_tools_with_context(intent, "create a file", confidence, context_info)
        assert tool_result is not None
        assert isinstance(tool_result, dict)


if __name__ == '__main__':
    unittest.main()
