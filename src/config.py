"""
Configuration and constants for WorkspaceAI
"""

import platform
import os
import json
import logging
from pathlib import Path


# Version
VERSION = "3.0"

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Application constants
CONSTANTS = {
    'VERSION': VERSION,
    'MODEL': 'qwen2.5:3b',
    'BASE_URL': 'http://127.0.0.1:11434',
    'MEMORY_LOCATION': 'WorkspaceAI/memory',
    'WORKSPACE_LOCATION': 'WorkspaceAI/workspace',
    'CONFIG_FILE': 'WorkspaceAI/config.json',
    'LOG_FILE': 'WorkspaceAI/workspaceai.log',
    'RECENT_CONVERSATIONS': 2,
    'SUMMARIZED_CONVERSATIONS': 8,
    'API_TIMEOUT': 30,
    'API_MAX_RETRIES': 3,
    'SUMMARY_TIMEOUT': 10,
    'MEMORY_CONTEXT_MESSAGES': 10,
    'MAX_RECENT_CONVERSATIONS': 2,
    'MAX_SUMMARIZED_CONVERSATIONS': 20,
    'MAX_FILENAME_LENGTH': 255,
    'PROGRESS_DURATION': 2,
    'SEARCH_MAX_FILE_KB': 1024,
    'SYSTEM_PROMPT': """You are WorkspaceAI, an intelligent file management assistant.

When tools are available and users request file operations, you MUST use the tools immediately.

Your tool selection has been enhanced with advanced intent classification and context weighting. Trust the system's tool recommendations and execute them directly.

For non-file requests (general questions, conversations), respond normally without tools."""
}

# Default application configuration
APP_CONFIG = {
    'model': CONSTANTS['MODEL'],
    'safe_mode': True,
    'ollama_host': 'localhost:11434',
    'search_max_file_kb': CONSTANTS['SEARCH_MAX_FILE_KB'],
    'verbose_output': False
}

def get_config_path():
    """Get the path to the config file"""
    return CONSTANTS['CONFIG_FILE']

def get_workspace_path():
    """Get the path to the workspace directory"""
    return CONSTANTS['WORKSPACE_LOCATION']

def get_memory_path():
    """Get the path to the memory directory"""
    return CONSTANTS['MEMORY_LOCATION']

def get_log_path():
    """Get the path to the log file"""
    return CONSTANTS['LOG_FILE']

def save_config(config):
    """Save configuration to file"""
    try:
        os.makedirs(os.path.dirname(get_config_path()), exist_ok=True)
        with open(get_config_path(), 'w', encoding='utf-8') as f:
            json.dump({
                "version": CONSTANTS['VERSION'],
                "settings": config
            }, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config: {e}")

def load_config():
    """Load configuration from file"""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('settings', APP_CONFIG)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
    return APP_CONFIG.copy()

def setup_logging():
    """Setup logging configuration"""
    try:
        os.makedirs(os.path.dirname(get_log_path()), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(get_log_path(), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger
    except Exception as e:
        print(f"Warning: Could not setup logging: {e}")
        return logging.getLogger(__name__)
