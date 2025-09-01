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
from .ollama_client import call_ollama_with_tools, detect_file_intent, test_ollama_connection
from .utils import detect_linux_package_manager, generate_install_commands

# Configure logging
logger = logging.getLogger(__name__)


def configure_settings():
    """Configuration menu for changing settings"""
    global APP_CONFIG
    config = APP_CONFIG.copy()
    
    while True:
        print("\n" + "="*50)
        print("CONFIGURATION SETTINGS")
        print("="*50)
        print(f"[1] Output folder: {config['paths']['outputs']}")
        print(f"[2] Memory folder: {config['paths']['memory']}")
        print(f"[3] AI Model: {config['settings']['model']}")
        print(f"[4] Safe mode: {'ON' if config['settings']['safe_mode'] else 'OFF'}")
        print(f"[5] Ollama host: {config['settings']['ollama_host']}")
        print("[S] Save and return")
        print("[X] Return without saving")
        print("="*50)
        
        choice = input("Choice: ").strip().lower()
        
        if choice == '1':
            new_path = input(f"Enter new output folder [{config['paths']['outputs']}]: ").strip()
            if new_path:
                config['paths']['outputs'] = new_path
                print(f"Output folder updated to: {new_path}")
        elif choice == '2':
            new_path = input(f"Enter new memory folder [{config['paths']['memory']}]: ").strip()
            if new_path:
                config['paths']['memory'] = new_path
                print(f"Memory folder updated to: {new_path}")
        elif choice == '3':
            new_model = input(f"Enter AI model [{config['settings']['model']}]: ").strip()
            if new_model:
                config['settings']['model'] = new_model
                print(f"Model updated to: {new_model}")
        elif choice == '4':
            config['settings']['safe_mode'] = not config['settings']['safe_mode']
            print(f"Safe mode: {'ON' if config['settings']['safe_mode'] else 'OFF'}")
        elif choice == '5':
            new_host = input(f"Enter Ollama host [{config['settings']['ollama_host']}]: ").strip()
            if new_host:
                config['settings']['ollama_host'] = new_host
                print(f"Ollama host updated to: {new_host}")
        elif choice == 's':
            if save_config(config):
                print("✅ Configuration saved successfully!")
                # Update global config
                APP_CONFIG.update(config)
            else:
                print("❌ Failed to save configuration")
            break
        elif choice == 'x':
            print("Configuration cancelled")
            break
        else:
            print("Invalid choice. Please try again.")


def interactive_mode():
    """Interactive chat mode with rolling memory"""
    print("\n" + "="*70)
    print("WorkspaceAI v3.0")
    print("="*70)
    print(f"Safe mode: {'ON' if file_manager.safe_mode else 'OFF'}")
    print(f"Memory: {len(memory.recent_conversations)} recent + {len(memory.summarized_conversations)} summarized")
    print("Workspace: \\WorkspaceAI\\workspace")
    
    # Show detected package manager on Linux
    if platform.system() == "Linux":
        detected_pm = detect_linux_package_manager()
        print(f"Package manager: {detected_pm if detected_pm else 'Not detected'}")

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

    while True:
        try:
            prompt = input(f"\nYou: ").strip()
            if prompt.lower() in ['exit', 'quit', 'q']:
                print("Exiting WorkspaceAI.")
                logger.info("User exited application")
                # Move current conversation to recent before exiting
                if memory.current_conversation:
                    memory.start_new_conversation()
                else:
                    memory.save_memory()
                break
            elif prompt == '/new':
                memory.start_new_conversation()
                print("✅ Started new conversation")
                logger.info("User started new conversation")
            elif prompt == '/tools':
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
            elif prompt == '/memory':
                print(f"Memory Status:")
                print(f"  Current: {len(memory.current_conversation)} messages")
                print(f"  Recent: {len(memory.recent_conversations)} full conversations")
                print(f"  Summarized: {len(memory.summarized_conversations)} conversations")
                total_messages = len(memory.current_conversation)
                for conv in memory.recent_conversations:
                    total_messages += len(conv.get("messages", []))
                print(f"  Total messages: {total_messages}")
                logger.info("Memory status displayed")
            elif prompt == '/config':
                configure_settings()
            elif prompt == '/reset':
                memory.recent_conversations = []
                memory.summarized_conversations = []
                memory.current_conversation = []
                memory.save_memory()
                print("Memory cleared")
                logger.info("Memory reset by user")
            elif not prompt:
                continue
            elif prompt.lower().startswith('chat:'):
                actual_prompt = prompt[5:].strip()
                if actual_prompt:
                    call_ollama_with_tools(actual_prompt, use_tools=False)
                else:
                    print("Please provide a question after 'chat:'")
            elif prompt.lower().startswith('tools:'):
                actual_prompt = prompt[6:].strip()
                if actual_prompt:
                    call_ollama_with_tools(actual_prompt, use_tools=True)
                else:
                    print("Please provide a command after 'tools:'")
            elif prompt.lower().startswith('install:'):
                software = prompt[8:].strip()
                if software:
                    print(generate_install_commands(software))
                else:
                    print("Please specify software to install after 'install:'")
            else:
                # Enhanced tool detection with logging
                looks_like_file_task = detect_file_intent(prompt)
                logger.info(f"Tool detection: '{prompt[:50]}...' -> use_tools={looks_like_file_task}")
                call_ollama_with_tools(prompt, use_tools=looks_like_file_task)
                
        except KeyboardInterrupt:
            print("\nSaving memory and exiting...")
            logger.info("User interrupted with Ctrl+C")
            # Move current conversation to recent before exiting
            if memory.current_conversation:
                memory.start_new_conversation()
            else:
                memory.save_memory()
            break
        except EOFError:
            print("\nEOF received, exiting...")
            logger.info("EOF received")
            # Move current conversation to recent before exiting
            if memory.current_conversation:
                memory.start_new_conversation()
            else:
                memory.save_memory()
            break
        except Exception as e:
            logger.error(f"Unexpected error in interactive loop: {e}")
            print(f"⚠️ An error occurred: {e}")
            print("You can continue or type 'exit' to quit.")


def main():
    """Setup and start enhanced interactive mode"""
    global logger
    
    print("Initializing WorkspaceAI...")
    
    # Ensure config is saved if this is first run
    if not os.path.exists(get_config_path()):
        save_config(APP_CONFIG)
        print("Created default configuration")
    
    # Setup logging
    logger = setup_logging()
    logger.info("WorkspaceAI starting up")
    
    # Test Ollama connection
    if not test_ollama_connection():
        input("\nPress Enter to continue anyway or Ctrl+C to exit...")
    
    # Start interactive mode directly
    interactive_mode()
