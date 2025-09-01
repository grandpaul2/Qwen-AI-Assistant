"""
Main interface module for WorkspaceAI

This module provides the interactive chat interface and main entry point,
handling user commands and coordinating between different system components.
"""

import os
import platform
import logging

from .config import APP_CONFIG, setup_logging, save_config, get_config_path
from .memory import memory
from .file_manager import file_manager
from .ollama import call_ollama_with_tools, detect_file_intent, test_ollama_connection
from .utils import detect_linux_package_manager, generate_install_commands
from .exceptions import (
    WorkspaceAIError, ConfigurationError, OllamaConnectionError,
    handle_exception, log_and_raise
)

# Configure logging
logger = logging.getLogger(__name__)


def configure_settings():
    """Configuration menu for changing settings - backward compatible wrapper"""
    try:
        return configure_settings_with_exceptions()
    except Exception as e:
        logging.error(f"Configuration settings failed: {e}")
        print(f"Warning: Configuration error: {str(e)}")
        # Return default config on error
        from .config import load_config
        return load_config()

def configure_settings_with_exceptions():
    """
    Configuration menu for changing settings - raises exceptions for validation errors
    
    Returns:
        dict: Updated configuration dictionary
        
    Raises:
        ConfigurationError: For configuration validation issues
        WorkspaceAIError: For general configuration errors
    """
    try:
        from .config import load_config, save_config
        
        config = load_config()
        if config is None:
            error = ConfigurationError("Failed to load configuration")
            error.context["function"] = "configure_settings"
            logging.error(f"Configuration failed: {error}")
            raise error
        
    except Exception as e:
        converted_error = handle_exception("config_loading", e)
        converted_error.context["function"] = "configure_settings"
        logging.error(f"Configuration loading failed: {converted_error}")
        raise converted_error
    
    try:
        while True:
            print("\n" + "="*50)
            print("CONFIGURATION SETTINGS")
            print("="*50)
            print(f"[1] AI Model: {config.get('model', 'qwen2.5:3b')}")
            print(f"[2] Safe mode: {'ON' if config.get('safe_mode', True) else 'OFF'}")
            print(f"[3] Ollama host: {config.get('ollama_host', 'localhost:11434')}")
            print(f"[4] Verbose output: {'ON' if config.get('verbose_output', False) else 'OFF'}")
            print(f"[5] Search max file KB: {config.get('search_max_file_kb', 1024)}")
            print("[S] Save and return")
            print("[X] Return without saving")
            print("="*50)
            
            try:
                choice = input("Choice: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nConfiguration cancelled")
                return load_config()
            
            # Validate choice input
            if not choice:
                print("Please enter a choice")
                continue
            
            if choice == '1':
                try:
                    current_model = config.get('model', 'qwen2.5:3b')
                    new_model = input(f"Enter AI model [{current_model}]: ").strip()
                    if new_model:
                        # Basic validation for model name
                        if len(new_model) > 100:
                            print("Model name too long (max 100 characters)")
                            continue
                        if not all(c.isalnum() or c in '.-_:/' for c in new_model):
                            print("Model name contains invalid characters")
                            continue
                        config['model'] = new_model
                        print(f"Model updated to: {new_model}")
                        logging.info(f"Model updated to: {new_model}")
                except (EOFError, KeyboardInterrupt):
                    print("\nModel update cancelled")
                    continue
                except Exception as e:
                    converted_error = handle_exception("model_update", e)
                    logging.error(f"Model update failed: {converted_error}")
                    print(f"Error updating model: {str(e)}")
                    continue
                    
            elif choice == '2':
                try:
                    config['safe_mode'] = not config.get('safe_mode', True)
                    print(f"Safe mode: {'ON' if config['safe_mode'] else 'OFF'}")
                    logging.info(f"Safe mode toggled to: {config['safe_mode']}")
                except Exception as e:
                    converted_error = handle_exception("safe_mode_toggle", e)
                    logging.error(f"Safe mode toggle failed: {converted_error}")
                    print(f"Error toggling safe mode: {str(e)}")
                    continue
                    
            elif choice == '3':
                try:
                    current_host = config.get('ollama_host', 'localhost:11434')
                    new_host = input(f"Enter Ollama host [{current_host}]: ").strip()
                    if new_host:
                        # Basic validation for host format
                        if len(new_host) > 200:
                            print("Host name too long (max 200 characters)")
                            continue
                        # Simple validation - should contain host and optionally port
                        if not new_host.replace(':', '').replace('.', '').replace('-', '').replace('_', '').isalnum():
                            if not ('localhost' in new_host.lower() or new_host.count('.') >= 3):  # Allow IP addresses
                                print("Invalid host format")
                                continue
                        config['ollama_host'] = new_host
                        print(f"Ollama host updated to: {new_host}")
                        logging.info(f"Ollama host updated to: {new_host}")
                except (EOFError, KeyboardInterrupt):
                    print("\nHost update cancelled")
                    continue
                except Exception as e:
                    converted_error = handle_exception("host_update", e)
                    logging.error(f"Host update failed: {converted_error}")
                    print(f"Error updating host: {str(e)}")
                    continue
                    
            elif choice == '4':
                try:
                    config['verbose_output'] = not config.get('verbose_output', False)
                    print(f"Verbose output: {'ON' if config['verbose_output'] else 'OFF'}")
                    logging.info(f"Verbose output toggled to: {config['verbose_output']}")
                except Exception as e:
                    converted_error = handle_exception("verbose_toggle", e)
                    logging.error(f"Verbose toggle failed: {converted_error}")
                    print(f"Error toggling verbose output: {str(e)}")
                    continue
                    
            elif choice == '5':
                try:
                    current_kb = config.get('search_max_file_kb', 1024)
                    new_kb = input(f"Enter search max file KB [{current_kb}]: ").strip()
                    if new_kb:
                        try:
                            kb_value = int(new_kb)
                            if kb_value < 1:
                                print("Value must be at least 1 KB")
                                continue
                            if kb_value > 100000:  # 100MB limit
                                print("Value too large (max 100,000 KB)")
                                continue
                            config['search_max_file_kb'] = kb_value
                            print(f"Search max file KB updated to: {kb_value}")
                            logging.info(f"Search max file KB updated to: {kb_value}")
                        except ValueError:
                            print("Invalid number entered")
                            continue
                except (EOFError, KeyboardInterrupt):
                    print("\nKB limit update cancelled")
                    continue
                except Exception as e:
                    converted_error = handle_exception("kb_limit_update", e)
                    logging.error(f"KB limit update failed: {converted_error}")
                    print(f"Error updating KB limit: {str(e)}")
                    continue
                    
            elif choice == 's':
                try:
                    save_config(config)
                    print("✅ Configuration saved successfully!")
                    logging.info("Configuration saved successfully")
                    return config
                except Exception as e:
                    converted_error = handle_exception("config_save", e)
                    logging.error(f"Configuration save failed: {converted_error}")
                    print(f"Error saving configuration: {str(e)}")
                    print("Try again or select 'x' to discard changes")
                    continue
                    
            elif choice == 'x':
                print("Configuration changes discarded")
                logging.info("Configuration changes discarded")
                return load_config()
                
            else:
                print("Invalid choice. Please try again.")
                
    except Exception as e:
        converted_error = handle_exception("configuration_menu", e)
        converted_error.context["function"] = "configure_settings"
        logging.error(f"Configuration menu failed: {converted_error}")
        raise converted_error
def interactive_mode():
    """Interactive chat mode with rolling memory - backward compatible wrapper"""
    try:
        return interactive_mode_with_exceptions()
    except Exception as e:
        logging.error(f"Interactive mode failed: {e}")
        print(f"Critical error in interactive mode: {str(e)}")
        print("Application will exit")

def interactive_mode_with_exceptions():
    """
    Interactive chat mode with rolling memory - raises exceptions for critical errors
    
    Raises:
        WorkspaceAIError: For critical application errors
        OllamaConnectionError: For Ollama connectivity issues
    """
    try:
        print("\n" + "="*70)
        print("WorkspaceAI v3.0")
        print("="*70)
        print(f"Safe mode: {'ON' if file_manager.safe_mode else 'OFF'}")
        print(f"Memory: {len(memory.recent_conversations)} recent + {len(memory.summarized_conversations)} summarized")
        print("Workspace: \\WorkspaceAI\\workspace")
        
        # Show detected package manager on Linux with error handling
        if platform.system() == "Linux":
            try:
                detected_pm = detect_linux_package_manager()
                print(f"Package manager: {detected_pm if detected_pm else 'Not detected'}")
            except Exception as e:
                logging.warning(f"Package manager detection failed: {e}")
                print("Package manager: Detection failed")

        if memory.recent_conversations or memory.summarized_conversations:
            print("Continuing from previous conversations...")

        print("\n- 'chat: question...' - force chat without using tools")
        print("- 'tools: command...' - force file management tools")
        print("- 'install: software...' - get installation commands")

        print("\n- /new        Start new conversation")
        print("- /tools      List available tools")
        print("- /memory     Show memory status")
        print("- /config     Configure settings")
        print("- /reset      Clear all memory")
        print("- exit        Quit")
        print("="*70)
        print("Ready for your input...")

    except Exception as e:
        converted_error = handle_exception("interactive_mode_setup", e)
        converted_error.context["function"] = "interactive_mode"
        logging.error(f"Interactive mode setup failed: {converted_error}")
        raise converted_error

    # Main interactive loop with enhanced error handling
    max_consecutive_errors = 5
    error_count = 0
    
    while True:
        try:
            # Reset error count on successful iteration
            error_count = 0
            
            # Get user input with timeout protection
            try:
                prompt = input(f"\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSaving memory and exiting...")
                logger.info("User interrupted with Ctrl+C or EOF")
                # Move current conversation to recent before exiting
                try:
                    if memory.current_conversation:
                        memory.start_new_conversation()
                    else:
                        memory.save_memory()
                except Exception as mem_error:
                    logging.error(f"Error saving memory on exit: {mem_error}")
                break
            
            # Validate input length
            if len(prompt) > 10000:  # 10KB limit
                print("Input too long (max 10,000 characters). Please shorten your request.")
                continue
            
            # Handle empty input
            if not prompt:
                continue
                
            # Process user commands with validation
            if prompt.lower() in ['exit', 'quit', 'q']:
                print("Exiting WorkspaceAI.")
                logger.info("User exited application")
                try:
                    # Move current conversation to recent before exiting
                    if memory.current_conversation:
                        memory.start_new_conversation()
                    else:
                        memory.save_memory()
                except Exception as mem_error:
                    logging.error(f"Error saving memory on exit: {mem_error}")
                break
                
            elif prompt == '/new':
                try:
                    memory.start_new_conversation()
                    print("✅ Started new conversation")
                    logger.info("User started new conversation")
                except Exception as e:
                    converted_error = handle_exception("new_conversation", e)
                    logging.error(f"New conversation failed: {converted_error}")
                    print(f"Error starting new conversation: {str(e)}")
                    
            elif prompt == '/tools':
                try:
                    print("\nAvailable File Management Tools:")
                    print("- create file...")
                    print("- read file...")
                    print("- write to file...")
                    print("- delete file...")
                    print("- copy file...")
                    print("- move file...")
                    print("- get file info...")
                    print("- list files...")
                    print("- search files...")
                    print("- compress files...")
                    print("- create folder...")
                    print("- copy folder...")
                    print("- delete folder...")
                    print("- write .json...")
                    print("- write .txt...")
                    print("- write .md...")
                    print("\nUse 'tools: <command>' to force the use of that tool")
                except Exception as e:
                    converted_error = handle_exception("tools_display", e)
                    logging.error(f"Tools display failed: {converted_error}")
                    print(f"Error displaying tools: {str(e)}")
                    
            elif prompt == '/memory':
                try:
                    print(f"Memory Status:")
                    print(f"  Current: {len(memory.current_conversation)} messages")
                    print(f"  Recent: {len(memory.recent_conversations)} full conversations")
                    print(f"  Summarized: {len(memory.summarized_conversations)} conversations")
                    total_messages = len(memory.current_conversation)
                    for conv in memory.recent_conversations:
                        total_messages += len(conv.get("messages", []))
                    print(f"  Total messages: {total_messages}")
                    logger.info("Memory status displayed")
                except Exception as e:
                    converted_error = handle_exception("memory_status", e)
                    logging.error(f"Memory status display failed: {converted_error}")
                    print(f"Error displaying memory status: {str(e)}")
                    
            elif prompt == '/config':
                try:
                    configure_settings()
                except Exception as e:
                    converted_error = handle_exception("configuration", e)
                    logging.error(f"Configuration failed: {converted_error}")
                    print(f"Error in configuration: {str(e)}")
                    
            elif prompt == '/reset':
                try:
                    memory.recent_conversations = []
                    memory.summarized_conversations = []
                    memory.current_conversation = []
                    memory.save_memory()
                    print("Memory cleared")
                    logger.info("Memory reset by user")
                except Exception as e:
                    converted_error = handle_exception("memory_reset", e)
                    logging.error(f"Memory reset failed: {converted_error}")
                    print(f"Error resetting memory: {str(e)}")
                    
            elif prompt.lower().startswith('chat:'):
                actual_prompt = prompt[5:].strip()
                if actual_prompt:
                    try:
                        call_ollama_with_tools(actual_prompt, use_tools=False)
                    except Exception as e:
                        converted_error = handle_exception("chat_mode", e)
                        logging.error(f"Chat mode failed: {converted_error}")
                        print(f"Error in chat mode: {str(e)}")
                else:
                    print("Please provide a question after 'chat:'")
                    
            elif prompt.lower().startswith('tools:'):
                actual_prompt = prompt[6:].strip()
                if actual_prompt:
                    try:
                        call_ollama_with_tools(actual_prompt, use_tools=True)
                    except Exception as e:
                        converted_error = handle_exception("tools_mode", e)
                        logging.error(f"Tools mode failed: {converted_error}")
                        print(f"Error in tools mode: {str(e)}")
                else:
                    print("Please provide a command after 'tools:'")
                    
            elif prompt.lower().startswith('install:'):
                software = prompt[8:].strip()
                if software:
                    try:
                        print(generate_install_commands(software))
                    except Exception as e:
                        converted_error = handle_exception("install_commands", e)
                        logging.error(f"Install commands failed: {converted_error}")
                        print(f"Error generating install commands: {str(e)}")
                else:
                    print("Please specify software to install after 'install:'")
                    
            else:
                # Enhanced tool detection with logging and error handling
                try:
                    looks_like_file_task = detect_file_intent(prompt)
                    logger.info(f"Tool detection: '{prompt[:50]}...' -> use_tools={looks_like_file_task}")
                    call_ollama_with_tools(prompt, use_tools=looks_like_file_task)
                except Exception as e:
                    converted_error = handle_exception("tool_detection_or_execution", e)
                    logging.error(f"Tool detection or execution failed: {converted_error}")
                    print(f"Error processing request: {str(e)}")
                    print("You can try rephrasing your request or use specific commands like 'chat:' or 'tools:'")
                
        except Exception as e:
            error_count += 1
            converted_error = handle_exception("interactive_loop", e)
            logging.error(f"Unexpected error in interactive loop: {converted_error}")
            print(f"⚠️ An error occurred: {str(e)}")
            
            if error_count >= max_consecutive_errors:
                print(f"Too many consecutive errors ({error_count}). Application will exit for safety.")
                logging.critical(f"Maximum consecutive errors reached: {error_count}")
                break
            else:
                print("You can continue or type 'exit' to quit.")
                
    # Cleanup on exit
    try:
        if memory.current_conversation:
            memory.start_new_conversation()
        else:
            memory.save_memory()
    except Exception as cleanup_error:
        logging.error(f"Error during cleanup: {cleanup_error}")


def main():
    """Setup and start enhanced interactive mode - backward compatible wrapper"""
    try:
        return main_with_exceptions()
    except Exception as e:
        logging.error(f"Main application failed: {e}")
        print(f"Critical application error: {str(e)}")
        print("Please check the logs and try again")
        return 1  # Return error code

def main_with_exceptions():
    """
    Setup and start enhanced interactive mode - raises exceptions for critical errors
    
    Returns:
        int: Exit code (0 for success, 1 for error)
        
    Raises:
        ConfigurationError: For configuration setup issues
        OllamaConnectionError: For Ollama connectivity issues
        WorkspaceAIError: For critical application errors
    """
    global logger
    
    try:
        print("Initializing WorkspaceAI...")
        
        # Ensure config is saved if this is first run with error handling
        config_path = get_config_path()
        if not os.path.exists(config_path):
            try:
                save_config(APP_CONFIG)
                print("Created default configuration")
                logging.info("Created default configuration file")
            except Exception as e:
                error = ConfigurationError(f"Failed to create default configuration: {str(e)}")
                error.context["config_path"] = config_path
                error.context["app_config"] = str(APP_CONFIG)
                logging.error(f"Configuration creation failed: {error}")
                raise error
        
        # Setup logging with error handling
        try:
            logger = setup_logging()
            logger.info("WorkspaceAI starting up")
        except Exception as e:
            # If logging setup fails, continue with basic logging
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            logger.warning(f"Advanced logging setup failed, using basic logging: {e}")
        
        # Test Ollama connection with enhanced error handling
        try:
            if not test_ollama_connection():
                print("\n⚠️ Ollama connection test failed!")
                print("The application will continue, but AI features may not work.")
                print("Please ensure Ollama is running and accessible.")
                
                try:
                    response = input("\nPress Enter to continue anyway or Ctrl+C to exit...")
                    if response.lower() in ['exit', 'quit', 'q']:
                        return 0
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting...")
                    return 0
                    
        except Exception as e:
            converted_error = handle_exception("ollama_connection_test", e)
            logging.error(f"Ollama connection test failed: {converted_error}")
            print(f"Error testing Ollama connection: {str(e)}")
            print("Continuing without Ollama verification...")
        
        # Start interactive mode with error handling
        try:
            interactive_mode()
            return 0  # Success
            
        except Exception as e:
            converted_error = handle_exception("interactive_mode", e)
            converted_error.context["function"] = "main"
            logging.error(f"Interactive mode failed: {converted_error}")
            raise converted_error
            
    except Exception as e:
        converted_error = handle_exception("main_application", e)
        converted_error.context["function"] = "main"
        logging.critical(f"Main application failed: {converted_error}")
        raise converted_error
