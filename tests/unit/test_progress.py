"""
Unit tests for progress module
Tests progress indicator classes and utilities
"""

import pytest
import time
import sys
import threading
from unittest.mock import patch, MagicMock, call
from src.progress import (
    ProgressIndicator,
    SimpleProgress,
    show_progress
)


class TestProgressIndicator:
    """Test ProgressIndicator class with animated dots"""
    
    def test_initialization(self):
        """Test ProgressIndicator initialization"""
        # Test default values
        progress = ProgressIndicator()
        assert progress.message == ""
        assert progress.max_dots == 3
        assert progress.interval == 0.5
        assert progress.running is False
        assert progress.thread is None
        
        # Test custom values
        progress = ProgressIndicator("Loading", 5, 0.2)
        assert progress.message == "Loading"
        assert progress.max_dots == 5
        assert progress.interval == 0.2
        
    def test_initialization_with_parameters(self):
        """Test ProgressIndicator with custom parameters"""
        progress = ProgressIndicator("Processing files", 4, 1.0)
        assert progress.message == "Processing files"
        assert progress.max_dots == 4
        assert progress.interval == 1.0
        
    @patch('sys.stdout')
    def test_start_and_stop(self, mock_stdout):
        """Test starting and stopping progress indicator"""
        progress = ProgressIndicator("Testing", 2, 0.01)  # Very fast for testing
        
        # Start progress
        progress.start()
        assert progress.running is True
        assert progress.thread is not None
        assert progress.thread.is_alive()
        
        # Let it run briefly
        time.sleep(0.05)
        
        # Stop progress
        progress.stop()
        assert progress.running is False
        
        # Wait for thread to finish
        if progress.thread:
            progress.thread.join(timeout=1.0)
        
        # Should have written progress messages
        assert mock_stdout.write.called
        
    @patch('sys.stdout')
    def test_context_manager(self, mock_stdout):
        """Test ProgressIndicator as context manager"""
        with ProgressIndicator("Context test", 2, 0.01) as progress:
            assert progress.running is True
            time.sleep(0.05)
        
        assert progress.running is False
        assert mock_stdout.write.called
        
    @patch('sys.stdout')
    def test_progress_animation_pattern(self, mock_stdout):
        """Test that progress dots animate correctly"""
        progress = ProgressIndicator("Test", 3, 0.01)
        progress.start()
        time.sleep(0.1)  # Let it cycle a few times
        progress.stop()
        
        if progress.thread:
            progress.thread.join(timeout=1.0)
        
        # Check that write was called multiple times
        assert mock_stdout.write.call_count > 1
        
        # Check that different dot patterns were written
        call_args = [call[0][0] for call in mock_stdout.write.call_args_list]
        
        # Should contain progression like "Test.", "Test..", "Test...", "Test."
        patterns_found = set()
        for arg in call_args:
            if "Test" in str(arg):
                patterns_found.add(str(arg))
        
        # Should have seen at least 2 different patterns
        assert len(patterns_found) >= 2
        
    def test_double_start_prevention(self):
        """Test that starting twice doesn't create multiple threads"""
        progress = ProgressIndicator("Test", 2, 0.01)
        
        progress.start()
        first_thread = progress.thread
        
        # Try to start again
        progress.start()
        second_thread = progress.thread
        
        # Should be the same thread
        assert first_thread is second_thread
        
        progress.stop()
        if progress.thread:
            progress.thread.join(timeout=1.0)
            
    def test_stop_without_start(self):
        """Test that stopping without starting doesn't cause errors"""
        progress = ProgressIndicator("Test")
        progress.stop()  # Should not raise exception
        assert progress.running is False


class TestSimpleProgress:
    """Test SimpleProgress class for non-animated progress"""
    
    def test_initialization(self):
        """Test SimpleProgress initialization"""
        # Test default message
        progress = SimpleProgress()
        assert progress.message == ""
        assert progress.active is False
        
        # Test custom message
        progress = SimpleProgress("Working...")
        assert progress.message == "Working..."
        assert progress.active is False
        
    @patch('sys.stdout')
    def test_show_and_hide(self, mock_stdout):
        """Test showing and hiding simple progress"""
        progress = SimpleProgress("Processing")
        
        # Show progress
        progress.show()
        assert progress.active is True
        mock_stdout.write.assert_called_with("Processing...")
        mock_stdout.flush.assert_called()
        
        # Hide progress
        mock_stdout.reset_mock()
        progress.hide()
        assert progress.active is False
        # hide() should write clear sequence
        assert mock_stdout.write.called
        mock_stdout.flush.assert_called()
        
    @patch('sys.stdout')
    def test_show_twice(self, mock_stdout):
        """Test that showing twice only prints once"""
        progress = SimpleProgress("Test")
        
        progress.show()
        progress.show()  # Second call should be ignored
        
        assert mock_stdout.write.call_count == 1
        
    @patch('sys.stdout')
    def test_hide_without_show(self, mock_stdout):
        """Test hiding without showing doesn't print"""
        progress = SimpleProgress("Test")
        
        progress.hide()
        
        # Should not write anything since it wasn't active
        mock_stdout.write.assert_not_called()
        
    @patch('sys.stdout')
    def test_context_manager(self, mock_stdout):
        """Test SimpleProgress as context manager"""
        with SimpleProgress("Context test") as progress:
            assert progress.active is True
        
        assert progress.active is False
        # Should have called write for both show and hide
        assert mock_stdout.write.call_count >= 1


class TestShowProgressFunction:
    """Test the show_progress utility function"""
    
    @patch('src.progress.ProgressIndicator')
    def test_show_progress_animated(self, mock_progress_class):
        """Test show_progress with animation"""
        mock_instance = MagicMock()
        mock_progress_class.return_value = mock_instance
        
        result = show_progress("Loading", animated=True, max_dots=4, interval=0.3)
        
        # Should create ProgressIndicator
        mock_progress_class.assert_called_once_with("Loading", 4, 0.3)
        assert result is mock_instance
        
    @patch('src.progress.SimpleProgress')
    def test_show_progress_simple(self, mock_progress_class):
        """Test show_progress without animation"""
        mock_instance = MagicMock()
        mock_progress_class.return_value = mock_instance
        
        result = show_progress("Loading", animated=False)
        
        # Should create SimpleProgress
        mock_progress_class.assert_called_once_with("Loading")
        assert result is mock_instance
        
    @patch('src.progress.ProgressIndicator')
    def test_show_progress_default_animated(self, mock_progress_class):
        """Test show_progress defaults to animated"""
        mock_instance = MagicMock()
        mock_progress_class.return_value = mock_instance
        
        result = show_progress("Test")
        
        # Default should be animated=True
        mock_progress_class.assert_called_once_with("Test", 3, 0.5)
        
    @patch('src.progress.SimpleProgress')
    def test_show_progress_empty_message(self, mock_progress_class):
        """Test show_progress with empty message"""
        mock_instance = MagicMock()
        mock_progress_class.return_value = mock_instance
        
        result = show_progress("", animated=False)
        
        mock_progress_class.assert_called_once_with("")


class TestThreadSafety:
    """Test thread safety of progress indicators"""
    
    @patch('sys.stdout')
    def test_concurrent_progress_indicators(self, mock_stdout):
        """Test multiple progress indicators running concurrently"""
        progress1 = ProgressIndicator("Task 1", 2, 0.01)
        progress2 = ProgressIndicator("Task 2", 2, 0.01)
        
        progress1.start()
        progress2.start()
        
        time.sleep(0.05)
        
        progress1.stop()
        progress2.stop()
        
        # Wait for threads to finish
        if progress1.thread:
            progress1.thread.join(timeout=1.0)
        if progress2.thread:
            progress2.thread.join(timeout=1.0)
        
        # Both should have written output
        assert mock_stdout.write.called
        
    def test_thread_cleanup(self):
        """Test that threads are properly cleaned up"""
        progress = ProgressIndicator("Test", 2, 0.01)
        
        progress.start()
        thread = progress.thread
        assert thread is not None
        assert thread.is_alive()
        
        progress.stop()
        
        # Give thread time to finish
        if thread:
            thread.join(timeout=1.0)
            assert not thread.is_alive()


class TestErrorHandling:
    """Test error handling in progress indicators"""
    
    def test_start_with_exception_in_run(self):
        """Test that exceptions in _run method don't crash the program"""
        progress = ProgressIndicator("Test", 2, 0.01)
        
        # Mock the _run method to raise an exception
        original_run = progress._run
        
        def mock_run():
            raise Exception("Test exception")
            
        progress._run = mock_run
        
        # Start should not raise exception
        progress.start()
        
        # Wait briefly then stop
        time.sleep(0.02)
        progress.stop()
        
        # Thread should still exist and can be joined
        if progress.thread:
            progress.thread.join(timeout=1.0)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_interval(self):
        """Test progress with zero interval"""
        progress = ProgressIndicator("Test", 3, 0)
        assert progress.interval == 0
        
        # Should still be able to start/stop without hanging
        progress.start()
        time.sleep(0.01)
        progress.stop()
        
        if progress.thread:
            progress.thread.join(timeout=1.0)
            
    def test_negative_values(self):
        """Test progress with negative values"""
        # Should accept negative values without crashing
        progress = ProgressIndicator("Test", -1, -0.1)
        assert progress.max_dots == -1
        assert progress.interval == -0.1
        
    def test_large_values(self):
        """Test progress with large values"""
        progress = ProgressIndicator("Test", 1000, 10.0)
        assert progress.max_dots == 1000
        assert progress.interval == 10.0
        
    def test_empty_and_special_messages(self):
        """Test progress with various message types"""
        # Empty message
        progress1 = ProgressIndicator("")
        assert progress1.message == ""
        
        # Special characters
        progress2 = ProgressIndicator("Loading... 🔄")
        assert progress2.message == "Loading... 🔄"
        
        # Very long message
        long_msg = "A" * 1000
        progress3 = ProgressIndicator(long_msg)
        assert progress3.message == long_msg


class TestIntegration:
    """Integration tests combining multiple progress features"""
    
    @patch('sys.stdout')
    def test_mixed_progress_types(self, mock_stdout):
        """Test using both progress types together"""
        # Use simple progress first
        with SimpleProgress("Step 1"):
            time.sleep(0.01)
        
        # Then use animated progress
        with ProgressIndicator("Step 2", 2, 0.01):
            time.sleep(0.05)
            
        # Both should have written output
        assert mock_stdout.write.called
        
    def test_show_progress_function_integration(self):
        """Test the show_progress function with real usage"""
        # Animated progress
        progress1 = show_progress("Processing", animated=True, max_dots=2, interval=0.01)
        assert isinstance(progress1, ProgressIndicator)
        
        # Simple progress
        progress2 = show_progress("Saving", animated=False)
        assert isinstance(progress2, SimpleProgress)
