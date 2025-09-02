"""
Unit Tests for App Module
Tests the main interface, configuration, and interactive mode functionality
"""

import unittest
import os
from unittest.mock import patch, Mock, MagicMock, call
from io import StringIO
import sys

from src.app import configure_settings, interactive_mode, main


class TestConfigureSettings(unittest.TestCase):
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_exit_without_saving(self, mock_print, mock_load, mock_save, mock_input):
        """Test exiting configuration without saving"""
        mock_load.return_value = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_input.return_value = 'x'  # Exit without saving
        
        configure_settings()
        
        mock_save.assert_not_called()
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_save_and_exit(self, mock_print, mock_load, mock_save, mock_input):
        """Test saving configuration and exiting"""
        mock_load.return_value = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_input.return_value = 's'  # Save and exit
        
        configure_settings()
        
        mock_save.assert_called_once()
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_change_model(self, mock_print, mock_load, mock_save, mock_input):
        """Test changing AI model setting"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['1', 'llama2:7b', 's']  # Change model, then save
        
        configure_settings()
        
        self.assertEqual(config['model'], 'llama2:7b')
        mock_save.assert_called_once_with(config)
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_toggle_safe_mode(self, mock_print, mock_load, mock_save, mock_input):
        """Test toggling safe mode setting"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['2', 's']  # Toggle safe mode, then save
        
        configure_settings()
        
        self.assertEqual(config['safe_mode'], False)
        mock_save.assert_called_once_with(config)
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_change_ollama_host(self, mock_print, mock_load, mock_save, mock_input):
        """Test changing Ollama host setting"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['3', 'remote-host:11434', 's']  # Change host, then save
        
        configure_settings()
        
        self.assertEqual(config['ollama_host'], 'remote-host:11434')
        mock_save.assert_called_once_with(config)
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_toggle_verbose_output(self, mock_print, mock_load, mock_save, mock_input):
        """Test toggling verbose output setting"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['4', 's']  # Toggle verbose, then save
        
        configure_settings()
        
        self.assertEqual(config['verbose_output'], True)
        mock_save.assert_called_once_with(config)
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_change_search_max_kb(self, mock_print, mock_load, mock_save, mock_input):
        """Test changing search max file KB setting"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['5', '2048', 's']  # Change max KB, then save
        
        configure_settings()
        
        self.assertEqual(config['search_max_file_kb'], 2048)  # Should be int, not string
        mock_save.assert_called_once_with(config)
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configure_settings_invalid_choice(self, mock_print, mock_load, mock_save, mock_input):
        """Test handling of invalid menu choices"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['invalid', '9', 'x']  # Invalid choices, then exit
        
        configure_settings()
        
        # Should print invalid choice message
        mock_print.assert_any_call("Invalid choice. Please try again.")


class TestInteractiveMode(unittest.TestCase):
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.detect_linux_package_manager')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_interactive_mode_initialization_linux(self, mock_print, mock_input, mock_fm, mock_memory, mock_detect, mock_platform, mock_logger):
        """Test interactive mode initialization on Linux"""
        mock_platform.return_value = 'Linux'
        mock_detect.return_value = 'apt'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_memory.current_conversation = []
        mock_input.side_effect = ['exit']  # Exit immediately with proper command
        
        try:
            interactive_mode()
        except SystemExit:
            pass  # Expected when quitting
        
        # Should show package manager info on Linux
        mock_detect.assert_called_once()
        mock_print.assert_any_call("Package manager: apt")
    
    @patch('src.app.platform.system')
    @patch('src.app.detect_linux_package_manager')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_interactive_mode_initialization_windows(self, mock_print, mock_input, mock_fm, mock_memory, mock_detect, mock_platform):
        """Test interactive mode initialization on Windows"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = False
        mock_memory.recent_conversations = ['conv1']
        mock_memory.summarized_conversations = ['conv2']
        mock_input.side_effect = ['exit']  # Exit immediately
        
        try:
            interactive_mode()
        except SystemExit:
            pass  # Expected when quitting
        
        # Should not call package manager detection on Windows
        mock_detect.assert_not_called()
        mock_print.assert_any_call("Safe mode: OFF")
        mock_print.assert_any_call("Memory: 1 recent + 1 summarized")
        mock_print.assert_any_call("Continuing from previous conversations...")
    
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('src.app.call_ollama_with_tools')
    @patch('builtins.print')
    def test_interactive_mode_user_input_processing(self, mock_print, mock_ollama, mock_input, mock_fm, mock_memory, mock_platform):
        """Test processing of user input in interactive mode"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_input.side_effect = ['hello world', 'exit']
        mock_ollama.return_value = "AI response"
        
        try:
            interactive_mode()
        except SystemExit:
            pass  # Expected when quitting
        
        mock_ollama.assert_called_once_with('hello world', use_tools=False)
    
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('src.app.configure_settings')
    @patch('builtins.print')
    def test_interactive_mode_config_command(self, mock_print, mock_config, mock_input, mock_fm, mock_memory, mock_platform):
        """Test /config command in interactive mode"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        # Mock the configure_settings to return immediately without interactive input
        mock_config.return_value = None
        mock_input.side_effect = ['/config', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass  # Expected when quitting
        
        mock_config.assert_called_once()
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_interactive_mode_new_conversation(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test /new command to start new conversation"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_memory.start_new_conversation = Mock()
        mock_input.side_effect = ['/new', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass  # Expected when quitting
        
        mock_memory.start_new_conversation.assert_called()
        # Should be called at least once for the /new command
        self.assertGreaterEqual(mock_memory.start_new_conversation.call_count, 1)
        mock_print.assert_any_call("✅ Started new conversation")


class TestMainFunction(unittest.TestCase):
    
    @patch('src.app.interactive_mode')
    @patch('src.app.test_ollama_connection')
    @patch('src.app.setup_logging')
    @patch('src.app.save_config')
    @patch('src.app.get_config_path')
    @patch('src.app.os.path.exists')
    @patch('builtins.print')
    def test_main_first_run_config_creation(self, mock_print, mock_exists, mock_get_path, mock_save, mock_setup, mock_test, mock_interactive):
        """Test main function creates config on first run"""
        mock_exists.return_value = False  # Config doesn't exist
        mock_get_path.return_value = '/config/path'
        mock_setup.return_value = Mock()
        mock_test.return_value = True
        
        main()
        
        mock_save.assert_called_once()
        mock_print.assert_any_call("Created default configuration")
        mock_interactive.assert_called_once()
    
    @patch('src.app.interactive_mode')
    @patch('src.app.test_ollama_connection')
    @patch('src.app.setup_logging')
    @patch('src.app.save_config')
    @patch('src.app.get_config_path')
    @patch('src.app.os.path.exists')
    @patch('builtins.print')
    def test_main_existing_config(self, mock_print, mock_exists, mock_get_path, mock_save, mock_setup, mock_test, mock_interactive):
        """Test main function with existing config"""
        mock_exists.return_value = True  # Config exists
        mock_get_path.return_value = '/config/path'
        mock_setup.return_value = Mock()
        mock_test.return_value = True
        
        main()
        
        mock_save.assert_not_called()  # Should not save config if it exists
        mock_interactive.assert_called_once()
    
    @patch('src.app.interactive_mode')
    @patch('src.app.test_ollama_connection')
    @patch('src.app.setup_logging')
    @patch('src.app.save_config')
    @patch('src.app.get_config_path')
    @patch('src.app.os.path.exists')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_main_ollama_connection_failed(self, mock_print, mock_input, mock_exists, mock_get_path, mock_save, mock_setup, mock_test, mock_interactive):
        """Test main function when Ollama connection fails"""
        mock_exists.return_value = True
        mock_get_path.return_value = '/config/path'
        mock_setup.return_value = Mock()
        mock_test.return_value = False  # Connection failed
        mock_input.return_value = ''  # User presses Enter to continue
        
        main()
        
        mock_input.assert_called_once_with("\nPress Enter to continue anyway or Ctrl+C to exit...")
        mock_interactive.assert_called_once()
    
    @patch('src.app.interactive_mode')
    @patch('src.app.test_ollama_connection')
    @patch('src.app.setup_logging')
    @patch('src.app.save_config')
    @patch('src.app.get_config_path')
    @patch('src.app.os.path.exists')
    @patch('builtins.print')
    def test_main_logging_setup(self, mock_print, mock_exists, mock_get_path, mock_save, mock_setup, mock_test, mock_interactive):
        """Test main function sets up logging correctly"""
        mock_exists.return_value = True
        mock_get_path.return_value = '/config/path'
        mock_logger = Mock()
        mock_setup.return_value = mock_logger
        mock_test.return_value = True
        
        main()
        
        mock_setup.assert_called_once()
        mock_logger.info.assert_called_once_with("WorkspaceAI starting up")


class TestMainModuleIntegration(unittest.TestCase):
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_configuration_flow_integration(self, mock_print, mock_load, mock_save, mock_input):
        """Test complete configuration flow"""
        # Test changing multiple settings
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = [
            '1', 'llama3:8b',  # Change model
            '2',              # Toggle safe mode
            '4',              # Toggle verbose
            's'               # Save and exit
        ]
        
        configure_settings()
        
        # Verify all changes were applied
        self.assertEqual(config['model'], 'llama3:8b')
        self.assertEqual(config['safe_mode'], False)
        self.assertEqual(config['verbose_output'], True)
        mock_save.assert_called_once_with(config)
    
    def test_module_imports(self):
        """Test that all required modules can be imported"""
        # This test ensures all dependencies are available
        from src.app import configure_settings, interactive_mode, main
        from src.config import APP_CONFIG, setup_logging, save_config, get_config_path
        from src.memory import memory
        from src.file_manager import file_manager
        
        # Test basic function existence
        self.assertTrue(callable(configure_settings))
        self.assertTrue(callable(interactive_mode))
        self.assertTrue(callable(main))


class TestMainModuleEdgeCases(unittest.TestCase):
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_empty_input_handling(self, mock_print, mock_load, mock_save, mock_input):
        """Test handling of empty input in configuration"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['1', '', 'x']  # Select model, empty input, exit
        
        configure_settings()
        
        # Model should remain unchanged with empty input
        self.assertEqual(config['model'], 'qwen2.5:3b')
        mock_save.assert_not_called()
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_whitespace_input_handling(self, mock_print, mock_load, mock_save, mock_input):
        """Test handling of whitespace-only input"""
        config = {
            'model': 'qwen2.5:3b',
            'safe_mode': True,
            'ollama_host': 'localhost:11434',
            'verbose_output': False,
            'search_max_file_kb': 1024
        }
        mock_load.return_value = config
        mock_input.side_effect = ['3', '   ', 'x']  # Select host, whitespace, exit
        
        configure_settings()
        
        # Host should remain unchanged with whitespace input
        self.assertEqual(config['ollama_host'], 'localhost:11434')
        mock_save.assert_not_called()


class TestInteractiveModeAdvanced(unittest.TestCase):
    """Advanced test cases for interactive mode missing coverage"""
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_tools_command(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test /tools command displays tool list"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_input.side_effect = ['/tools', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_print.assert_any_call("\nAvailable File Management Tools:")
        mock_print.assert_any_call("- create file...")
        mock_print.assert_any_call("- read file...")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_memory_command(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test /memory command shows memory status"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = [{'messages': [1, 2]}, {'messages': [3]}]
        mock_memory.summarized_conversations = [{'id': 1}]
        mock_memory.current_conversation = [1, 2, 3]
        mock_input.side_effect = ['/memory', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_print.assert_any_call("Memory Status:")
        mock_print.assert_any_call("  Current: 3 messages")
        mock_print.assert_any_call("  Recent: 2 full conversations")
        mock_print.assert_any_call("  Summarized: 1 conversations")
        mock_print.assert_any_call("  Total messages: 6")  # 3 + 2 + 1
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_reset_command(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test /reset command clears memory"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = [{'id': 1}]
        mock_memory.summarized_conversations = [{'id': 2}]
        mock_memory.current_conversation = [1, 2]
        mock_memory.save_memory = Mock()
        mock_input.side_effect = ['/reset', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        self.assertEqual(mock_memory.recent_conversations, [])
        self.assertEqual(mock_memory.summarized_conversations, [])
        self.assertEqual(mock_memory.current_conversation, [])
        mock_memory.save_memory.assert_called()
        mock_print.assert_any_call("Memory cleared")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.call_ollama_with_tools')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_chat_prefix_command(self, mock_print, mock_input, mock_ollama, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test chat: prefix forces chat without tools"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_input.side_effect = ['chat: hello world', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_ollama.assert_called_with('hello world', use_tools=False)
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.call_ollama_with_tools')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_tools_prefix_command(self, mock_print, mock_input, mock_ollama, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test tools: prefix forces tool usage"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_input.side_effect = ['tools: create file', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_ollama.assert_called_with('create file', use_tools=True)
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.generate_install_commands')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_install_prefix_command(self, mock_print, mock_input, mock_install, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test install: prefix generates installation commands"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_install.return_value = "choco install python3"
        mock_input.side_effect = ['install: python3', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_install.assert_called_with('python3')
        mock_print.assert_any_call("choco install python3")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.call_ollama_with_tools')
    @patch('src.app.detect_file_intent')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_auto_tool_detection(self, mock_print, mock_input, mock_detect, mock_ollama, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test automatic tool detection for regular prompts"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_detect.return_value = True
        mock_input.side_effect = ['create a file', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_detect.assert_called_with('create a file')
        mock_ollama.assert_called_with('create a file', use_tools=True)
        mock_logger.info.assert_any_call("Tool detection: 'create a file...' -> use_tools=True")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_empty_input_handling(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test handling of empty inputs"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_input.side_effect = ['', '   ', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        # Should continue without error
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_empty_prefix_commands(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test handling of empty prefix commands"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_input.side_effect = ['chat:', 'tools:', 'install:', 'exit']
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_print.assert_any_call("Please provide a question after 'chat:'")
        mock_print.assert_any_call("Please provide a command after 'tools:'")
        mock_print.assert_any_call("Please specify software to install after 'install:'")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_keyboard_interrupt_handling(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test handling of KeyboardInterrupt (Ctrl+C)"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_memory.current_conversation = [1, 2, 3]
        mock_memory.start_new_conversation = Mock()
        mock_memory.save_memory = Mock()
        mock_input.side_effect = KeyboardInterrupt()
        
        interactive_mode()
        
        mock_print.assert_any_call("\nSaving memory and exiting...")
        mock_memory.start_new_conversation.assert_called_once()
        mock_logger.info.assert_any_call("User interrupted with Ctrl+C")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_eof_error_handling(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test handling of EOFError"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_memory.current_conversation = []
        mock_memory.save_memory = Mock()
        mock_input.side_effect = EOFError()
        
        interactive_mode()
        
        mock_print.assert_any_call("\nEOF received, exiting...")
        mock_memory.save_memory.assert_called_once()
        mock_logger.info.assert_any_call("EOF received")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_unexpected_exception_handling(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test handling of unexpected exceptions in interactive loop"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        
        # First call raises exception, second call exits normally
        def side_effect(*args):
            if mock_input.call_count == 1:
                raise ValueError("Test error")
            return 'exit'
        
        mock_input.side_effect = side_effect
        
        try:
            interactive_mode()
        except SystemExit:
            pass
        
        mock_print.assert_any_call("⚠️ An error occurred: Test error")
        mock_print.assert_any_call("You can continue or type 'exit' to quit.")
        mock_logger.error.assert_called_with("Unexpected error in interactive loop: Test error")
    
    @patch('src.app.logger')
    @patch('src.app.platform.system')
    @patch('src.app.memory')
    @patch('src.app.file_manager')
    @patch('src.app.input')
    @patch('builtins.print')
    def test_quit_variations(self, mock_print, mock_input, mock_fm, mock_memory, mock_platform, mock_logger):
        """Test various quit commands (quit, q)"""
        mock_platform.return_value = 'Windows'
        mock_fm.safe_mode = True
        mock_memory.recent_conversations = []
        mock_memory.summarized_conversations = []
        mock_memory.current_conversation = []
        mock_memory.save_memory = Mock()
        
        for quit_cmd in ['quit', 'q']:
            mock_input.side_effect = [quit_cmd]
            mock_memory.reset_mock()
            mock_print.reset_mock()
            mock_logger.reset_mock()
            
            try:
                interactive_mode()
            except SystemExit:
                pass
            
            mock_print.assert_any_call("Exiting WorkspaceAI.")
            mock_memory.save_memory.assert_called_once()
            mock_logger.info.assert_any_call("User exited application")


class TestConfigureSettingsAdvanced(unittest.TestCase):
    """Advanced configuration tests for missing coverage"""
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_model_change_with_value(self, mock_print, mock_load, mock_save, mock_input):
        """Test changing model with actual value"""
        config = {'model': 'qwen2.5:3b'}
        mock_load.return_value = config
        mock_input.side_effect = ['1', 'llama2:7b', 's']
        
        configure_settings()
        
        self.assertEqual(config['model'], 'llama2:7b')
        mock_print.assert_any_call("Model updated to: llama2:7b")
        mock_save.assert_called_once_with(config)
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_safe_mode_toggle_false_to_true(self, mock_print, mock_load, mock_save, mock_input):
        """Test toggling safe mode from False to True"""
        config = {'safe_mode': False}
        mock_load.return_value = config
        mock_input.side_effect = ['2', 's']
        
        configure_settings()
        
        self.assertTrue(config['safe_mode'])
        mock_print.assert_any_call("Safe mode: ON")
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_ollama_host_change_with_value(self, mock_print, mock_load, mock_save, mock_input):
        """Test changing Ollama host with actual value"""
        config = {'ollama_host': 'localhost:11434'}
        mock_load.return_value = config
        mock_input.side_effect = ['3', 'remote:11434', 's']
        
        configure_settings()
        
        self.assertEqual(config['ollama_host'], 'remote:11434')
        mock_print.assert_any_call("Ollama host updated to: remote:11434")
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_verbose_output_toggle_false_to_true(self, mock_print, mock_load, mock_save, mock_input):
        """Test toggling verbose output from False to True"""
        config = {'verbose_output': False}
        mock_load.return_value = config
        mock_input.side_effect = ['4', 's']
        
        configure_settings()
        
        self.assertTrue(config['verbose_output'])
        mock_print.assert_any_call("Verbose output: ON")
    
    @patch('src.app.input')
    @patch('src.config.save_config')
    @patch('src.config.load_config')
    @patch('builtins.print')
    def test_search_max_kb_invalid_input(self, mock_print, mock_load, mock_save, mock_input):
        """Test invalid input for search max KB setting"""
        config = {'search_max_file_kb': 1024}
        mock_load.return_value = config
        mock_input.side_effect = ['5', 'invalid', 's']
        
        configure_settings()
        
        # Should remain unchanged and show error
        self.assertEqual(config['search_max_file_kb'], 1024)
        mock_print.assert_any_call("Invalid number entered")


if __name__ == '__main__':
    unittest.main()
