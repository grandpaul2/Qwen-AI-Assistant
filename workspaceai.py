
#!/usr/bin/env python3
"""
WorkspaceAI - AI Assistant with Rolling Memory + File Management (Cross-Platform)
Enhanced chat with persistent memory across sessions

Version: 3.0
Author: Grandpaul
Updated: August 31, 2025
Features: 85-90% tool detection accuracy, rolling memory, advanced file management, software installation commands, Windows/Linux support
"""

# Color constants for terminal output
CYAN = "\033[36m"
LIGHT_GREEN = "\033[92m"
RESET = "\033[0m"

# Imports (move all to top)
import json
import requests
import re
import sys
import os
import time
import platform
from datetime import datetime
import threading
import shutil
import logging
import hashlib
import zipfile
import tarfile
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Optional, List, Union, Dict, Any

# Suppress HTTP library logging noise
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

CONSTANTS = {
    'API_TIMEOUT': 30,
    'API_MAX_RETRIES': 3,
    'SUMMARY_TIMEOUT': 10,
    'MEMORY_CONTEXT_MESSAGES': 10,
    'MAX_RECENT_CONVERSATIONS': 2,
    'MAX_SUMMARIZED_CONVERSATIONS': 20,
    'MAX_FILENAME_LENGTH': 255,
    'PROGRESS_DURATION': 2,
    'SEARCH_MAX_FILE_KB': 1024,
    'VERSION': "3.0",
    'SYSTEM_PROMPT': """You are WorkspaceAI, an intelligent file management assistant with access to file operation tools in a secure workspace environment.

**CRITICAL RULE:** When tools are available and users request file operations, you MUST use the tools immediately. Do not provide explanations or instructions - execute the action directly.

**ABSOLUTE REQUIREMENTS:**
- If user mentions creating, writing, saving, making files → USE TOOLS IMMEDIATELY
- If user says "save that as..." or "create a..." → USE TOOLS IMMEDIATELY  
- If user wants file operations → NO CONVERSATION, JUST USE TOOLS
- Tools are mandatory for all file operations - never explain instead of acting

**Available Tools:**
- File creation, editing, reading, writing
- Folder management and organization  
- File search and navigation
- Compression and backup operations

**MANDATORY Response Pattern:**
1. For file operations: Execute tools IMMEDIATELY → Report results briefly
2. For general questions about files: Provide conversational response
3. For ambiguous requests: If it contains file action words, USE TOOLS

**User Override Commands:**
- "chat:" = Respond conversationally only, no tools
- "tools:" = Force tool usage even for edge cases  
- "install:" = Provide software installation instructions

**Examples of IMMEDIATE tool usage:**
- "create a file" → MUST USE create_file tool
- "save this to workspace" → MUST USE write_file tool  
- "make a folder" → MUST USE create_folder tool
- "call it different name" → MUST USE rename/create tool
- "save that as md" → MUST USE write_md_file tool
- "create a Python script" → MUST USE create_file tool with .py extension
- "find Python files" → MUST USE search_files tool with ".py" keyword
- "read config.json" → MUST USE read_file or read_json_file tool

**Intent Clarification:**
- "Create X script/program" = Make a new file with code (use create_file)
- "Run X operation" = Execute existing functionality (use specific operation tool)
- "Find/Search files" = Locate files by pattern (use search_files)
- "List files" = Show directory contents (use list_files)

**NEVER say you will create something - just create it immediately using tools.**

Work efficiently and execute actions directly."""
}

# Import tqdm with fallback
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Warning: tqdm not installed. Install with: pip install tqdm")
    class TqdmFallback:
        def __init__(self, total=100, desc="Progress", ncols=70, bar_format=None):
            self.total = total
            self.desc = desc
            self.current = 0
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, n):
            self.current += n
            percent = int((self.current / self.total) * 100)
            print(f"{self.desc}: {percent}%", end='\r')
    tqdm = TqdmFallback

# Setup logging (only after config is loaded)
def setup_logging():
    """Setup logging with proper file location from hardcoded paths"""
    log_dir = os.path.dirname(get_config_path())
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'workspaceai.log')
    logging.getLogger().handlers.clear()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ],
        force=True
    )
    return logging.getLogger('WorkspaceAI')

# Configuration Management
def get_script_directory():
    """Get the directory where this script is located"""
    return os.path.dirname(os.path.abspath(__file__))

def get_workspace_path():
    """Get the hardcoded workspace path"""
    return os.path.join(get_script_directory(), "WorkspaceAI", "workspace")

def get_memory_path():
    """Get the hardcoded memory path"""
    return os.path.join(get_script_directory(), "WorkspaceAI", "memory")

def get_config_path():
    """Get the hardcoded config path"""
    return os.path.join(get_script_directory(), "WorkspaceAI", "config.json")

def get_default_config():
    """Get default configuration settings"""
    return {
        "version": CONSTANTS['VERSION'],
        "settings": {
            "model": "qwen2.5:3b",
            "safe_mode": True,
            "ollama_host": "localhost:11434",
            "compress_format": "zip",
            "search_case_sensitive": False,
            "search_content": True,
            "search_max_file_kb": CONSTANTS['SEARCH_MAX_FILE_KB']
        }
    }

def load_config():
    """Load configuration from file or create default"""
    config_path = get_config_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Ensure all required keys exist (for upgrades)
            default_config = get_default_config()
            updated = False
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
                    updated = True
            for section in default_config:
                if isinstance(default_config[section], dict):
                    for subkey in default_config[section]:
                        if subkey not in config[section]:
                            config[section][subkey] = default_config[section][subkey]
                            updated = True
            if updated:
                save_config(config)
            return config
        else:
            return get_default_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        return get_default_config()

def setup_directories():
    """Create necessary directories"""
    try:
        os.makedirs(get_workspace_path(), exist_ok=True)
        os.makedirs(get_memory_path(), exist_ok=True)
        os.makedirs(os.path.dirname(get_config_path()), exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directories: {e}")
        return False


# Setup logging (only after config is loaded)

def save_config(config):
    """Save configuration to file"""
    config_path = get_config_path()
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        # Validate config before saving
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Create backup of existing config
        if os.path.exists(config_path):
            backup_path = config_path + ".backup"
            shutil.copy2(config_path, backup_path)
            logger.info(f"Created config backup: {backup_path}")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Configuration saved to {config_path}")
        return True
    except (OSError, IOError) as e:
        logger.error(f"File system error saving config: {e}")
        print(f"Error saving config: {e}")
        return False
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error: {e}")
        print(f"Error encoding config to JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving config: {e}")
        print(f"Error saving config: {e}")
        return False

# Global configuration
APP_CONFIG = load_config()
setup_directories()
# Setup logging after config is loaded
logger = setup_logging()

# Global configuration
APP_CONFIG = load_config()
setup_directories()
# Setup logging after config is loaded
logger = setup_logging()

# File Manager Class - Built into single file
class FileManager:
    """File management tools integrated directly into WorkspaceAI assistant"""
    
    def __init__(self, config=None):
        if config is None:
            config = APP_CONFIG
        
        self.base_path = get_workspace_path()
        self.safe_mode = config["settings"]["safe_mode"]
        self.default_compress_format = config["settings"]["compress_format"]
        self.search_case_sensitive = config["settings"]["search_case_sensitive"]
        self.search_content = config["settings"]["search_content"]
        self.search_max_file_kb = config["settings"]["search_max_file_kb"]
        self.search_exclude_globs = ["*.zip", "*.tar", "*.gz", "*.png", "*.jpg", "*.pdf"]
        self.versions = defaultdict(list)
        self.tags = defaultdict(list)
        
        # Ensure base directory exists
        os.makedirs(self.base_path, exist_ok=True)

    def _resolve(self, *parts: str) -> str:
        """Join workspace base_path with parts and validate for security using pathlib"""
        root = Path(self.base_path)
        
        # Build the full path within workspace
        if parts:
            full_path = root / Path(*[p for p in parts if p])
        else:
            full_path = root
        
        # Resolve to absolute path and normalize
        full_path = full_path.resolve()
        
        # Security check: ensure path doesn't escape workspace directory
        try:
            base_path = Path(self.base_path).resolve()
            # Check if the resolved path is within the workspace directory
            full_path.relative_to(base_path)
        except ValueError:
            logger.warning(f"Path traversal attempt blocked: {full_path}")
            raise ValueError(f"Path '{full_path}' is outside the workspace directory")
        
        return str(full_path)

    def _validate_filename(self, filename: str) -> None:
        """Validate filename for security and filesystem compatibility"""
        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty")
        
        # Check for invalid characters (platform-specific)
        if platform.system() == "Windows":
            invalid_chars = '<>:"|?*'
            if any(char in filename for char in invalid_chars):
                raise ValueError(f"Filename contains invalid characters: {invalid_chars}")
            
            # Check for reserved names on Windows
            reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
            if filename.upper().split('.')[0] in reserved_names:
                raise ValueError(f"Filename '{filename}' is reserved and cannot be used on Windows")
        else:
            # Linux/Unix - only null character is forbidden
            if '\0' in filename:
                raise ValueError("Filename cannot contain null character")
        
        # Check length
        if len(filename) > CONSTANTS['MAX_FILENAME_LENGTH']:
            raise ValueError(f"Filename too long (max {CONSTANTS['MAX_FILENAME_LENGTH']} characters)")

    def _guard_overwrite(self, path: str) -> Optional[str]:
        """Check safe mode for overwriting files"""
        if self.safe_mode and os.path.exists(path):
            return "Safe mode is ON: operation would overwrite an existing file."
        return None

    def _generate_unique_filename(self, file_name: str) -> str:
        """Generate a unique filename by adding numbers if file exists"""
        file_path = self._resolve(file_name)
        
        if not os.path.exists(file_path):
            return file_name
        
        # Split filename and extension
        name, ext = os.path.splitext(file_name)
        counter = 1
        
        while True:
            new_name = f"{name}_{counter}{ext}"
            new_path = self._resolve(new_name)
            if not os.path.exists(new_path):
                return new_name
            counter += 1
            
            # Safety check to avoid infinite loop
            if counter > 999:
                import time
                timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
                return f"{name}_{timestamp}{ext}"

    def create_file(self, file_name: str, content: str = "") -> str:
        """Create a new file with content in workspace - auto-generates unique name if needed"""
        try:
            self._validate_filename(os.path.basename(file_name))
            
            # Auto-generate unique filename to avoid conflicts
            unique_name = self._generate_unique_filename(file_name)
            file_path = self._resolve(unique_name)
            
            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path:  # Only create directory if there is one
                os.makedirs(dir_path, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            
            logger.info(f"Created file: {file_path}")
            
            if unique_name != file_name:
                return f"File created as '{unique_name}' (original name already existed) in workspace!"
            else:
                return f"File '{unique_name}' created successfully in workspace!"
            
        except ValueError as e:
            logger.error(f"Validation error creating file '{file_name}': {e}")
            return f"Error: {e}"
        except (OSError, IOError) as e:
            logger.error(f"File system error creating '{file_name}': {e}")
            return f"Error creating file: {e}"
        except Exception as e:
            logger.error(f"Unexpected error creating file '{file_name}': {e}")
            return f"Error creating file: {e}"

    def read_file(self, file_name: str) -> str:
        """Read file contents from workspace"""
        file_path = self._resolve(file_name)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_to_file(self, file_name: str, content: str) -> str:
        """Write content to file in workspace"""
        original_file_name = file_name
        file_path = self._resolve(file_name)
        
        # Check if file exists and generate unique name if needed
        if os.path.exists(file_path):
            unique_file_name = self._generate_unique_filename(file_name)
            file_path = self._resolve(unique_file_name)
            file_name = unique_file_name
        
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:  # Only create directory if there is one
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            
            if file_name != original_file_name:
                return f"File created as '{file_name}' (original name already existed) in workspace!"
            else:
                return f"Content written to '{file_name}' successfully in workspace!"
        except Exception as e:
            return f"Error writing file: {e}"

    def delete_file(self, file_name: str) -> str:
        """Delete a file from workspace"""
        if self.safe_mode:
            return "Safe mode is ON: delete_file is disabled."
        file_path = self._resolve(file_name)
        try:
            os.remove(file_path)
            return f"File '{file_name}' deleted successfully from workspace!"
        except Exception as e:
            return f"Error deleting file: {e}"

    def list_files(self, subdirectory: str = "") -> str:
        """List files in workspace directory or subdirectory"""
        try:
            if subdirectory:
                directory_path = self._resolve(subdirectory)
            else:
                directory_path = self.base_path
            files = os.listdir(directory_path)
            location = f"workspace/{subdirectory}" if subdirectory else "workspace"
            return f"Files in {location}:\n" + "\n".join(files)
        except Exception as e:
            return f"Error listing files: {e}"

    def create_folder(self, folder_name: str) -> str:
        """Create a new folder in workspace"""
        folder_path = self._resolve(folder_name)
        try:
            os.makedirs(folder_path, exist_ok=True)
            return f"Folder '{folder_name}' created successfully in workspace!"
        except Exception as e:
            return f"Error creating folder: {e}"

    def delete_folder(self, folder_name: str) -> str:
        """Delete a folder from workspace"""
        if self.safe_mode:
            return "Safe mode is ON: delete_folder is disabled."
        folder_path = self._resolve(folder_name)
        try:
            shutil.rmtree(folder_path)
            return f"Folder '{folder_name}' deleted successfully from workspace!"
        except Exception as e:
            return f"Error deleting folder: {e}"

    def copy_folder(self, src_folder: str, dest_folder: str) -> str:
        """Copy a folder and all its contents within workspace"""
        src_folder_path = self._resolve(src_folder)
        dest_folder_path = self._resolve(dest_folder)
        
        if not os.path.exists(src_folder_path):
            return f"Source folder '{src_folder}' does not exist."
        
        if not os.path.isdir(src_folder_path):
            return f"'{src_folder}' is not a folder."
            
        if os.path.exists(dest_folder_path):
            return f"Destination folder '{dest_folder}' already exists. Please choose a different name."
        
        try:
            shutil.copytree(src_folder_path, dest_folder_path)
            return f"Folder '{src_folder}' copied to '{dest_folder}' successfully in workspace!"
        except Exception as e:
            return f"Error copying folder: {e}"

    def copy_file(self, src_file: str, dest_file: str) -> str:
        """Copy a file within workspace"""
        src_file_path = self._resolve(src_file)
        dest_file_path = self._resolve(dest_file)
        guard_result = self._guard_overwrite(dest_file_path)
        if guard_result:
            return guard_result
        try:
            dest_dir = os.path.dirname(dest_file_path)
            if dest_dir:  # Only create directory if there is one
                os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(src_file_path, dest_file_path)
            return f"File '{src_file}' copied to '{dest_file}' successfully in workspace!"
        except Exception as e:
            return f"Error copying file: {e}"

    def move_file(self, src_file: str, dest_file: str) -> str:
        """Move a file within workspace"""
        src_file_path = self._resolve(src_file)
        dest_file_path = self._resolve(dest_file)
        guard_result = self._guard_overwrite(dest_file_path)
        if guard_result:
            return guard_result
        try:
            dest_dir = os.path.dirname(dest_file_path)
            if dest_dir:  # Only create directory if there is one
                os.makedirs(dest_dir, exist_ok=True)
            shutil.move(src_file_path, dest_file_path)
            return f"File '{src_file}' moved to '{dest_file}' successfully in workspace!"
        except Exception as e:
            return f"Error moving file: {e}"

    def search_files(self, keyword: str, subdirectory: str = "") -> List[str]:
        """Search for files by keyword in workspace"""
        import fnmatch
        if subdirectory:
            search_path = self._resolve(subdirectory)
        else:
            search_path = self.base_path
        matching_files = []
        case_kw = keyword if self.search_case_sensitive else keyword.lower()

        def should_skip(name: str) -> bool:
            return any(fnmatch.fnmatch(name, pat) for pat in self.search_exclude_globs)

        try:
            for root, dirs, files in os.walk(search_path):
                files = [f for f in files if not should_skip(f)]
                for file in files:
                    name_check = file if self.search_case_sensitive else file.lower()
                    file_path = os.path.join(root, file)
                    if case_kw in name_check:
                        matching_files.append(file_path)
                        continue
                    if self.search_content:
                        try:
                            if os.path.getsize(file_path) <= self.search_max_file_kb * 1024:
                                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                    text = f.read()
                                text_check = text if self.search_case_sensitive else text.lower()
                                if case_kw in text_check:
                                    matching_files.append(file_path)
                        except:
                            continue
        except Exception as e:
            return [f"Search error: {e}"]
        
        return matching_files

    def compress_file(self, file_name: str, output_filename: str, format: Optional[str] = None) -> str:
        """Compress a file in workspace"""
        fmt = format or self.default_compress_format
        file_path = self._resolve(file_name)
        output_path = self._resolve(output_filename)
        
        guard_result = self._guard_overwrite(output_path)
        if guard_result:
            return guard_result
        try:
            if fmt == "zip":
                with zipfile.ZipFile(output_path, "w") as zipf:
                    zipf.write(file_path, os.path.basename(file_path))
            elif fmt == "tar":
                with tarfile.open(output_path, "w") as tarf:
                    tarf.add(file_path, os.path.basename(file_path))
            elif fmt == "gztar":
                with tarfile.open(output_path, "w:gz") as tarf:
                    tarf.add(file_path, os.path.basename(file_path))
            return f"File '{file_name}' compressed to '{output_filename}' as {fmt} in workspace."
        except Exception as e:
            return f"Error compressing file: {e}"

    def backup_files(self, source_path: str, backup_path: str) -> str:
        """Backup files from source to backup directory"""
        try:
            backed_up_count = 0
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    source_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(source_file_path, source_path)
                    backup_file_path = os.path.join(backup_path, relative_path)
                    os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                    if self._guard_overwrite(backup_file_path):
                        continue
                    shutil.copy2(source_file_path, backup_file_path)
                    backed_up_count += 1
            return f"Backup completed! {backed_up_count} files backed up."
        except Exception as e:
            return f"Backup error: {e}"

    def read_json_file(self, file_name: str) -> Union[Dict[str, Any], str]:
        """Read a JSON file from workspace"""
        file_path = self._resolve(file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            return f"Error reading JSON: {e}"

    def write_json_file(self, file_name: str, content: Dict[str, Any]) -> str:
        """Write data to JSON file in workspace"""
        original_file_name = file_name
        file_path = self._resolve(file_name)
        
        # Check if file exists and generate unique name if needed
        if os.path.exists(file_path):
            unique_file_name = self._generate_unique_filename(file_name)
            file_path = self._resolve(unique_file_name)
            file_name = unique_file_name
        
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:  # Only create directory if there is one
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(content, file, indent=4, ensure_ascii=False)
            
            if file_name != original_file_name:
                return f"JSON file created as '{file_name}' (original name already existed) in workspace!"
            else:
                return f"JSON written to '{file_name}' successfully in workspace!"
        except Exception as e:
            return f"Error writing JSON: {e}"

    def write_txt_file(self, file_name: str, content: str) -> str:
        """Write content to a .txt file in workspace - auto-generates unique name if needed"""
        if not file_name.endswith('.txt'):
            file_name += '.txt'
        
        # Use auto-unique naming
        unique_name = self._generate_unique_filename(file_name)
        file_path = self._resolve(unique_name)
        
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            
            if unique_name != file_name:
                return f"Content written to '{unique_name}' (original name already existed) successfully in workspace!"
            else:
                return f"Content written to '{unique_name}' successfully in workspace!"
        except Exception as e:
            return f"Error writing text file: {e}"

    def write_md_file(self, file_name: str, content: str) -> str:
        """Write content to a .md (markdown) file in workspace - auto-generates unique name if needed"""
        if not file_name.endswith('.md'):
            file_name += '.md'
        
        # Use auto-unique naming instead of standard write_to_file
        unique_name = self._generate_unique_filename(file_name)
        file_path = self._resolve(unique_name)
        
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            
            if unique_name != file_name:
                return f"Content written to '{unique_name}' (original name already existed) successfully in workspace!"
            else:
                return f"Content written to '{unique_name}' successfully in workspace!"
        except Exception as e:
            return f"Error writing markdown file: {e}"

    def write_json_from_string(self, file_name: str, content: str) -> str:
        """Write content to a .json file (string version for AI tools) in workspace"""
        if not file_name.endswith('.json'):
            file_name += '.json'
        try:
            # Try to parse and format as JSON for better formatting
            parsed_content = json.loads(content)
            return self.write_json_file(file_name, parsed_content)
        except json.JSONDecodeError:
            # If it's not valid JSON, write as-is but with .json extension
            return self.write_to_file(file_name, content)

    def get_file_metadata(self, file_name: str) -> Union[Dict[str, str], str]:
        """Get file metadata from workspace"""
        file_path = self._resolve(file_name)
        try:
            metadata = os.stat(file_path)
            return {
                "size": str(metadata.st_size),
                "creation_time": datetime.fromtimestamp(metadata.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                "modification_time": datetime.fromtimestamp(metadata.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "access_time": datetime.fromtimestamp(metadata.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            return f"Error getting metadata: {e}"

# Initialize file manager
file_manager = FileManager()

class MemoryManager:
    def __init__(self, config=None):
        if config is None:
            config = APP_CONFIG
        
        self.memory_file = os.path.join(get_memory_path(), "memory.json")
        self.current_conversation = []
        self.recent_conversations = []  # Last 2 full conversations
        self.summarized_conversations = []  # Next 20 summarized
        self.load_memory()
    
    def load_memory(self):
        """Load persistent memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.current_conversation = data.get('current_conversation', [])
                self.recent_conversations = data.get('recent_conversations', [])
                self.summarized_conversations = data.get('summarized_conversations', [])
                print(f"📖 Loaded memory: {len(self.recent_conversations)} recent + {len(self.summarized_conversations)} summarized conversations")
            except Exception as e:
                print(f"⚠️ Could not load memory: {e}")
                self.reset_memory()
        else:
            self.reset_memory()
    
    def save_memory(self):
        """Save memory to file after each response"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            data = {
                'current_conversation': self.current_conversation,
                'recent_conversations': self.recent_conversations,
                'summarized_conversations': self.summarized_conversations,
                'last_updated': datetime.now().isoformat()
            }
            
            # Create backup before overwriting
            if os.path.exists(self.memory_file):
                backup_file = self.memory_file + ".backup"
                shutil.copy2(self.memory_file, backup_file)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.memory_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            if os.path.exists(self.memory_file):
                os.replace(temp_file, self.memory_file)
            else:
                os.rename(temp_file, self.memory_file)
                
            logger.debug(f"Memory saved successfully - Current: {len(self.current_conversation)}, Recent: {len(self.recent_conversations)}, Summarized: {len(self.summarized_conversations)}")
            
        except (OSError, IOError) as e:
            logger.error(f"File system error saving memory: {e}")
            print(f"⚠️ Could not save memory: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving memory: {e}")
            print(f"⚠️ Could not save memory: {e}")
    
    def add_message(self, role, content, tool_calls=None):
        """Add message to current conversation"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        if tool_calls:
            message['tool_calls'] = tool_calls
        
        self.current_conversation.append(message)
        
        # Auto-save after each message (synchronous for reliability)
        self.save_memory()
        logger.debug(f"Added {role} message to conversation, total messages: {len(self.current_conversation)}")
    
    def start_new_conversation(self):
        """Move current conversation to recent and start fresh"""
        if not self.current_conversation:
            logger.debug("No current conversation to save")
            return
        
        logger.debug(f"Moving conversation with {len(self.current_conversation)} messages to recent")
        
        # Add current to recent conversations
        conversation_data = {
            'date': datetime.now().isoformat(),
            'messages': self.current_conversation.copy()
        }
        self.recent_conversations.insert(0, conversation_data)
        
        # Keep only last 2 recent conversations
        if len(self.recent_conversations) > CONSTANTS['MAX_RECENT_CONVERSATIONS']:
            # Move oldest recent to summarized
            oldest = self.recent_conversations.pop()
            logger.debug(f"Moving oldest recent conversation to summarized (had {len(oldest['messages'])} messages)")
            summary = self.summarize_conversation(oldest['messages'])
            self.summarized_conversations.insert(0, {
                'date': oldest['date'],
                'summary': summary
            })
        
        # Keep only 20 summarized conversations
        self.summarized_conversations = self.summarized_conversations[:CONSTANTS['MAX_SUMMARIZED_CONVERSATIONS']]
        
        # Clear current conversation
        self.current_conversation = []
        self.save_memory()
        print(f"Started new conversation (previous conversation with {len(conversation_data['messages'])} messages saved to memory)")
        logger.info(f"New conversation started - Recent: {len(self.recent_conversations)}, Summarized: {len(self.summarized_conversations)}")
    
    def summarize_conversation(self, messages):
        """Create AI summary of conversation"""
        try:
            # Build summary prompt
            conversation_text = ""
            for msg in messages[-CONSTANTS['MEMORY_CONTEXT_MESSAGES']:]:  # Last 10 messages only
                if msg['role'] in ['user', 'assistant']:
                    conversation_text += f"{msg['role']}: {msg['content'][:200]}\n"
            
            if not conversation_text.strip():
                return "Empty conversation"
            
            summary_prompt = f"Summarize this conversation in 2-3 sentences, focusing on key topics, files created/modified, and important context:\n\n{conversation_text}"
            
            response = requests.post("http://localhost:11434/api/chat", json={
                "model": "qwen2.5:3b",
                "messages": [{"role": "user", "content": summary_prompt}],
                "stream": False
            }, timeout=CONSTANTS['SUMMARY_TIMEOUT'])
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Conversation from {messages[0]['timestamp'][:10]} with {len(messages)} messages"
        except:
            return f"Conversation from {messages[0]['timestamp'][:10]} with {len(messages)} messages"
    
    def get_context_messages(self):
        """Build context from memory for API calls"""
        context_messages = []
        
        # Add system prompt for tool usage
        context_messages.append({
            "role": "system", 
            "content": CONSTANTS['SYSTEM_PROMPT']
        })
        
        # Add summaries as system context
        if self.summarized_conversations:
            summaries_text = "Previous conversation context:\n"
            for conv in reversed(self.summarized_conversations):  # Oldest first
                date = conv['date'][:10]
                summaries_text += f"- {date}: {conv['summary']}\n"
            context_messages.append({"role": "system", "content": summaries_text})
        
        # Add recent conversations
        for conv in reversed(self.recent_conversations):  # Oldest first
            for msg in conv['messages']:
                if msg['role'] in ['user', 'assistant']:
                    context_messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        # Add current conversation
        for msg in self.current_conversation:
            if msg['role'] in ['user', 'assistant']:
                context_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        return context_messages
    
    def reset_memory(self):
        """Reset all memory"""
        self.current_conversation = []
        self.recent_conversations = []
        self.summarized_conversations = []

# Global memory manager
memory = MemoryManager()

def detect_linux_package_manager():
    """Detect the available package manager on Linux systems"""
    if platform.system() != "Linux":
        return None
    
    # Check for package managers in order of preference
    managers = [
        ("apt", ["apt", "--version"]),
        ("dnf", ["dnf", "--version"]), 
        ("yum", ["yum", "--version"]),
        ("pacman", ["pacman", "--version"]),
        ("zypper", ["zypper", "--version"]),
        ("snap", ["snap", "--version"])
    ]
    
    for manager, command in managers:
        try:
            # Try to run the version command to see if manager exists
            result = subprocess.run(command, 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  timeout=5)
            if result.returncode == 0:  # Command succeeded
                return manager
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    return "unknown"

def show_progress(description, duration=None):
    """Show progress bar for operations"""
    if duration is None:
        duration = CONSTANTS['PROGRESS_DURATION']
    with tqdm(total=100, desc=description, ncols=70, bar_format='{desc}: {percentage:3.0f}%|{bar}|') as pbar:
        for i in range(100):
            time.sleep(duration/100)
            pbar.update(1)

def get_all_tool_schemas():
    """Build tool schemas for all file management functions"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a new file with content in workspace. Use for 'create a script', 'make a file', 'generate code', etc. Supports all file types (.py, .txt, .js, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name or path within workspace (e.g., 'backup_script.py' or 'folder/notes.txt')"},
                        "content": {"type": "string", "description": "Text content to write (code, documentation, etc.)"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the entire content of a text file from workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name or path within workspace"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_to_file",
                "description": "Write text content to a file in workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name or path within workspace"},
                        "content": {"type": "string", "description": "Text content to write"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files in workspace directory or subdirectory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subdirectory": {"type": "string", "description": "Subdirectory within workspace to list (optional, defaults to root)"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_folder",
                "description": "Create a new folder in workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder_name": {"type": "string", "description": "Name or path of the folder to create within workspace"}
                    },
                    "required": ["folder_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_file",
                "description": "Delete a file from workspace (blocked when safe_mode is True)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "Name or path of the file to delete within workspace"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_folder",
                "description": "Delete a folder from workspace (blocked when safe_mode is True)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder_name": {"type": "string", "description": "Name or path of the folder to delete within workspace"}
                    },
                    "required": ["folder_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "copy_folder",
                "description": "Copy a folder and all its contents within workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "src_folder": {"type": "string", "description": "Source folder name or path within workspace"},
                        "dest_folder": {"type": "string", "description": "Destination folder name or path within workspace"}
                    },
                    "required": ["src_folder", "dest_folder"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search for files by name pattern or content keyword in workspace. Use for 'find files', 'search for files', 'list Python files', etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "Keyword to search for in filenames (e.g., '.py' for Python files, 'config' for config files) or file contents"},
                        "subdirectory": {"type": "string", "description": "Subdirectory within workspace to search (optional)"}
                    },
                    "required": ["keyword"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compress_file",
                "description": "Compress a file using zip, tar, or gztar format in workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "Source file to compress within workspace"},
                        "output_filename": {"type": "string", "description": "Output archive name within workspace"},
                        "format": {"type": "string", "description": "zip | tar | gztar"}
                    },
                    "required": ["file_name", "output_filename"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "backup_files",
                "description": "Copy existing files from source directory to backup directory. Use ONLY when user wants to backup existing files, NOT for creating new backup scripts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string", "description": "Source directory"},
                        "backup_path": {"type": "string", "description": "Backup directory"}
                    },
                    "required": ["source_path", "backup_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_install_commands",
                "description": "Generate cross-platform installation commands for popular software (Windows/Linux)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "software": {"type": "string", "description": "Software name (e.g., 'python', 'git', 'vscode', 'nodejs')"},
                        "method": {"type": "string", "description": "Installation method: 'winget' (Windows), 'apt'/'dnf'/'pacman' (Linux), 'pip', 'docker', 'auto' (default)"}
                    },
                    "required": ["software"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "copy_file",
                "description": "Copy a file within the workspace folder from source to destination",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "src_file": {"type": "string", "description": "Source file name (workspace-only)"},
                        "dest_file": {"type": "string", "description": "Destination file name (workspace-only)"}
                    },
                    "required": ["src_file", "dest_file"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "move_file",
                "description": "Move a file within the workspace folder from source to destination",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "src_file": {"type": "string", "description": "Source file name (workspace-only)"},
                        "dest_file": {"type": "string", "description": "Destination file name (workspace-only)"}
                    },
                    "required": ["src_file", "dest_file"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_json_file",
                "description": "Read and parse a JSON file from the workspace folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "JSON file name (workspace-only)"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_json_file",
                "description": "Write data to a JSON file in the workspace folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "JSON file name (workspace-only)"},
                        "content": {"type": "object", "description": "Data to write as JSON"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_txt_file",
                "description": "Write content to a .txt file in the workspace folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name (will auto-add .txt extension) (workspace-only)"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_md_file",
                "description": "Write content to a .md (markdown) file in the workspace folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name (will auto-add .md extension) (workspace-only)"},
                        "content": {"type": "string", "description": "Markdown content to write"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_json_from_string",
                "description": "Write content to a .json file from string content in the workspace folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name (will auto-add .json extension) (workspace-only)"},
                        "content": {"type": "string", "description": "JSON content as string"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_file_metadata",
                "description": "Get metadata information about a file (size, dates) from the workspace folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name (workspace-only)"}
                    },
                    "required": ["file_name"]
                }
            }
        }
        # File management tools ready for WorkspaceAI
    ]

def call_ollama_with_tools(prompt: str, model: Optional[str] = None, use_tools: bool = True):
    """Call Ollama with conversation memory and tools"""
    
    if model is None:
        model = APP_CONFIG['settings']['model']
    
    # Add user message to memory
    memory.add_message("user", prompt)
    
    # Build request with conversation context
    messages = memory.get_context_messages()
    
    # If tools should be used, add enforcement message
    if use_tools:
        # Check for specific ambiguous patterns and provide targeted guidance
        prompt_lower = prompt.lower()
        enforcement_msg = "TOOLS ARE AVAILABLE AND REQUIRED: The user request requires file operations. You MUST use the available tools immediately. Do not provide explanations or alternatives - execute the file operation directly using the appropriate tool."
        
        # Add specific guidance for common confusions
        if "create" in prompt_lower and "script" in prompt_lower:
            enforcement_msg += "\n\nSPECIFIC GUIDANCE: 'Create a script' means make a NEW FILE with code - use create_file tool, NOT backup_files or other operation tools."
        elif "find" in prompt_lower and "files" in prompt_lower:
            enforcement_msg += "\n\nSPECIFIC GUIDANCE: 'Find files' means search for existing files - use search_files tool with appropriate keyword (e.g. '.py' for Python files)."
        
        messages.append({
            "role": "system", 
            "content": enforcement_msg
        })
    
    messages.append({"role": "user", "content": prompt})
    
    request_data = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    if use_tools:
        request_data["tools"] = get_all_tool_schemas()
    
    # Show progress for API call if it might be slow
    progress_thread = None
    if len(messages) > 10:  # Lots of context
        progress_thread = threading.Thread(target=show_progress, args=("Processing with context", 3), daemon=True)
        progress_thread.start()
    
    # Ollama API call with timeout and retry logic
    host = APP_CONFIG['settings']['ollama_host']
    max_retries = CONSTANTS['API_MAX_RETRIES']
    timeout = CONSTANTS['API_TIMEOUT']
    response = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Ollama API (attempt {attempt + 1}/{max_retries})")
            response = requests.post(
                f"http://{host}/api/chat", 
                json=request_data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                break
            else:
                logger.warning(f"Ollama API returned status {response.status_code}: {response.text}")
                if attempt == max_retries - 1:
                    print(f"Error: {response.status_code} - {response.text}")
                    return
                
        except requests.exceptions.Timeout:
            logger.warning(f"Ollama API timeout (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                print(f"Error: Ollama API timeout after {timeout}s")
                return
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"Ollama connection failed (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                print("Error: Could not connect to Ollama. Is it running?")
                return
                
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            if attempt == max_retries - 1:
                print(f"Error: {e}")
                return
        
        # Wait before retry
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    if progress_thread:
        progress_thread.join()
    
    # Check if we got a valid response
    if response is None or response.status_code != 200:
        logger.error("Failed to get valid response from Ollama after all retries")
        print("Error: Could not get response from Ollama")
        return
    
    try:
        result = response.json()
        message = result["message"]
        
        # Add space before assistant response
        print()
        assistant_content = message.get('content', '')
        print(f"{CYAN}Assistant: {assistant_content}{RESET}")
        
        # Add assistant message to memory
        tool_calls_data = message.get('tool_calls', None)
        memory.add_message("assistant", assistant_content, tool_calls_data)
        
        # Validate tool usage when expected
        if use_tools and not tool_calls_data and assistant_content:
            logger.warning(f"Expected tools but got conversational response: '{assistant_content[:100]}...'")
            print(f"{CYAN}⚠️  Note: Expected file operation but got conversational response. Try 'tools: {prompt}' to force tool usage.{RESET}")
        elif use_tools and tool_calls_data:
            logger.info(f"Tools used correctly: {len(tool_calls_data)} tool calls")
        
        # Handle tool calls
        if tool_calls_data:
            for tool_call in tool_calls_data:
                function_name = tool_call["function"]["name"]
                function_args = tool_call["function"]["arguments"]
                
                print(f"\n🔧 Tool Call: {function_name}")
                print(f"Arguments: {json.dumps(function_args, indent=2)}")
                
                # Show progress for potentially slow operations
                slow_operations = ['search_files', 'backup_files', 'compress_file']
                progress_thread = None
                if function_name in slow_operations:
                    progress_thread = threading.Thread(target=show_progress, args=(f"Running {function_name}", 2), daemon=True)
                    progress_thread.start()
                
                # Execute the tool function
                try:
                    if hasattr(file_manager, function_name):
                        result = getattr(file_manager, function_name)(**function_args)
                        print(f"✅ Result: {result}")
                        memory.add_message("tool", f"{function_name}: {result}")
                    elif function_name == "generate_install_commands":
                        result = generate_install_commands(**function_args)
                        print(f"✅ Generated Commands:")
                        print(result)
                        memory.add_message("tool", f"Generated install commands: {result}")
                    else:
                        error_msg = f"Unknown function: {function_name}"
                        logger.error(error_msg)
                        print(f"❌ {error_msg}")
                        memory.add_message("tool", f"Error: {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Error executing {function_name}: {e}"
                    logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    memory.add_message("tool", error_msg)
                
                if progress_thread is not None:
                    progress_thread.join()
                    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from Ollama: {e}")
        print("Error: Invalid response from Ollama")
    except KeyError as e:
        logger.error(f"Missing expected field in Ollama response: {e}")
        print("Error: Unexpected response format from Ollama")
    except Exception as e:
        logger.error(f"Error processing Ollama response: {e}")
        print(f"Error processing response: {e}")

def generate_install_commands(software, method="auto"):
    """Generate installation commands for popular software (cross-platform)"""
    
    software = software.lower().strip()
    method = method.lower().strip()
    current_os = platform.system()
    
    # Cross-platform software database
    software_db = {
        "python": {
            "description": "Python programming language",
            "windows": {
                "winget": "winget install Python.Python.3.12",
                "direct": "Download from: https://python.org/downloads/\n- Choose 'Add to PATH' during installation"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install python3 python3-pip",
                "dnf": "sudo dnf install python3 python3-pip",
                "yum": "sudo yum install python3 python3-pip", 
                "pacman": "sudo pacman -S python python-pip",
                "zypper": "sudo zypper install python3 python3-pip",
                "snap": "sudo snap install python3 --classic",
                "direct": "Download from: https://python.org/downloads/"
            }
        },
        "git": {
            "description": "Version control system",
            "windows": {
                "winget": "winget install Git.Git",
                "direct": "Download from: https://git-scm.com/downloads"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install git",
                "dnf": "sudo dnf install git",
                "yum": "sudo yum install git",
                "pacman": "sudo pacman -S git",
                "zypper": "sudo zypper install git",
                "snap": "sudo snap install git --classic",
                "direct": "sudo apt install git  # or use your distro's package manager"
            }
        },
        "vscode": {
            "description": "Code editor",
            "windows": {
                "winget": "winget install Microsoft.VisualStudioCode",
                "direct": "Download from: https://code.visualstudio.com/download"
            },
            "linux": {
                "apt": "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg\nsudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/\nsudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'\nsudo apt update && sudo apt install code",
                "dnf": "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc\nsudo sh -c 'echo -e \"[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/yum.repos.d/vscode.repo'\nsudo dnf install code",
                "snap": "sudo snap install code --classic",
                "direct": "Download .deb/.rpm from: https://code.visualstudio.com/download"
            }
        },
        "nodejs": {
            "description": "JavaScript runtime",
            "windows": {
                "winget": "winget install OpenJS.NodeJS",
                "direct": "Download from: https://nodejs.org/en/download/"
            },
            "linux": {
                "apt": "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -\nsudo apt-get install -y nodejs",
                "dnf": "sudo dnf install nodejs npm",
                "yum": "sudo yum install nodejs npm",
                "pacman": "sudo pacman -S nodejs npm",
                "zypper": "sudo zypper install nodejs npm",
                "snap": "sudo snap install node --classic",
                "direct": "Download from: https://nodejs.org/en/download/"
            }
        },
        "chrome": {
            "description": "Web browser",
            "windows": {
                "winget": "winget install Google.Chrome",
                "direct": "Download from: https://chrome.google.com/"
            },
            "linux": {
                "apt": "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -\nsudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'\nsudo apt update && sudo apt install google-chrome-stable",
                "dnf": "sudo dnf install fedora-workstation-repositories\nsudo dnf config-manager --set-enabled google-chrome\nsudo dnf install google-chrome-stable",
                "yum": "sudo yum install google-chrome-stable",
                "direct": "Download .deb/.rpm from: https://chrome.google.com/"
            }
        },
        "firefox": {
            "description": "Web browser", 
            "windows": {
                "winget": "winget install Mozilla.Firefox",
                "direct": "Download from: https://firefox.com/"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install firefox",
                "dnf": "sudo dnf install firefox",
                "yum": "sudo yum install firefox",
                "pacman": "sudo pacman -S firefox",
                "zypper": "sudo zypper install firefox",
                "snap": "sudo snap install firefox",
                "direct": "sudo apt install firefox  # Usually pre-installed on most distros"
            }
        },
        "discord": {
            "description": "Communication platform",
            "windows": {
                "winget": "winget install Discord.Discord",
                "direct": "Download from: https://discord.com/download"
            },
            "linux": {
                "apt": "wget -O discord.deb \"https://discordapp.com/api/download?platform=linux&format=deb\"\nsudo dpkg -i discord.deb\nsudo apt-get install -f",
                "snap": "sudo snap install discord",
                "direct": "Download .deb/.tar.gz from: https://discord.com/download"
            }
        },
        "vlc": {
            "description": "Media player",
            "windows": {
                "winget": "winget install VideoLAN.VLC",
                "direct": "Download from: https://videolan.org/vlc/"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install vlc",
                "dnf": "sudo dnf install vlc",
                "yum": "sudo yum install vlc",
                "pacman": "sudo pacman -S vlc",
                "zypper": "sudo zypper install vlc",
                "snap": "sudo snap install vlc",
                "direct": "sudo apt install vlc  # Available in most distro repos"
            }
        },
        "7zip": {
            "description": "File archiver",
            "windows": {
                "winget": "winget install 7zip.7zip",
                "direct": "Download from: https://7-zip.org/"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install p7zip-full",
                "dnf": "sudo dnf install p7zip p7zip-plugins",
                "yum": "sudo yum install p7zip p7zip-plugins",
                "pacman": "sudo pacman -S p7zip",
                "zypper": "sudo zypper install p7zip",
                "direct": "sudo apt install p7zip-full  # Cross-platform 7zip"
            }
        },
        "open-webui": {
            "description": "Web UI for LLMs",
            "windows": {
                "pip": "pip install open-webui\n# Then run with: open-webui serve",
                "docker": "docker run -d --name open-webui -p 3000:8080 ghcr.io/open-webui/open-webui:main",
                "direct": "Download from: https://github.com/open-webui/open-webui"
            },
            "linux": {
                "pip": "pip install open-webui\n# Then run with: open-webui serve",
                "docker": "docker run -d --name open-webui -p 3000:8080 ghcr.io/open-webui/open-webui:main",
                "direct": "pip install open-webui  # Recommended method"
            }
        },
        "ollama": {
            "description": "Run LLMs locally",
            "windows": {
                "direct": "Download from: https://ollama.ai/download\n# After install: ollama run llama2"
            },
            "linux": {
                "curl": "curl -fsSL https://ollama.ai/install.sh | sh",
                "direct": "curl -fsSL https://ollama.ai/install.sh | sh\n# After install: ollama run llama2"
            }
        }
    }
    
    # Find software (flexible matching)
    found_software = None
    for key in software_db:
        if software in key or key in software:
            found_software = key
            break
    
    if not found_software:
        # Generate suggestions for similar software
        suggestions = [key for key in software_db.keys() if any(word in key for word in software.split())]
        suggestion_text = f"\nDid you mean: {', '.join(suggestions[:5])}" if suggestions else ""
        return f"Software '{software}' not found in database.{suggestion_text}\n\nAvailable software: {', '.join(list(software_db.keys())[:10])}..."
    
    sw = software_db[found_software]
    os_key = current_os.lower()
    
    # Get platform-specific commands
    if os_key not in sw:
        return f"Software '{found_software}' is not supported on {current_os}"
    
    platform_commands = sw[os_key]
    result = f"\n📦 {sw['description']} ({found_software}) - {current_os}\n" + "="*60 + "\n"
    
    if method == "auto":
        # Determine best method automatically based on platform
        if current_os == "Windows":
            if "winget" in platform_commands:
                result += f"🚀 RECOMMENDED (Windows Package Manager):\n{platform_commands['winget']}\n\n"
            if "direct" in platform_commands:
                result += f"🌐 Direct Download:\n{platform_commands['direct']}\n\n"
        
        elif current_os == "Linux":
            # Detect package manager and recommend it
            detected_pm = detect_linux_package_manager()
            if detected_pm and detected_pm in platform_commands:
                result += f"🚀 RECOMMENDED ({detected_pm.upper()}):\n{platform_commands[detected_pm]}\n\n"
            
            # Show other available methods
            for pm_name, command in platform_commands.items():
                if pm_name != detected_pm and pm_name != "direct":
                    result += f"📋 {pm_name.upper()}:\n{command}\n\n"
            
            if "direct" in platform_commands:
                result += f"🌐 Alternative:\n{platform_commands['direct']}\n\n"
        
        # Show pip/docker if available
        if "pip" in platform_commands:
            result += f"🐍 PIP Install:\n{platform_commands['pip']}\n\n"
        if "docker" in platform_commands:
            result += f"🐳 Docker:\n{platform_commands['docker']}\n\n"
    
    elif method in platform_commands:
        result += f"📋 {method.upper()} Install:\n{platform_commands[method]}\n"
    else:
        available = list(platform_commands.keys())
        available.remove("description") if "description" in available else None
        result += f"Method '{method}' not available for {current_os}.\nAvailable methods: {', '.join(available)}\n"
        # Show default method
        if current_os == "Windows" and "winget" in platform_commands:
            result += f"🚀 Default method:\n{platform_commands['winget']}"
        elif current_os == "Linux":
            detected_pm = detect_linux_package_manager()
            if detected_pm in platform_commands:
                result += f"🚀 Default method:\n{platform_commands[detected_pm]}"
    
    if current_os == "Windows":
        result += "\n💡 TIP: Run commands in PowerShell as Administrator if needed"
    else:
        result += "\n💡 TIP: You may need sudo privileges for system package installation"
    
    return result

def detect_file_intent(prompt: str) -> bool:
    """Enhanced contextual detection for file operations"""
    prompt_lower = prompt.lower()
    
    # File action patterns (contextual)
    file_action_patterns = [
        # Direct commands
        r'\b(create|make|generate|build)\s+.*\b(file|folder|directory)\b',
        r'\b(save|write|store|put)\s+.*\b(to|in|into)\s+.*\b(workspace|folder|directory)\b',
        r'\b(read|open|view|show|display)\s+.*\b(file|document)\b',
        
        # Search and find operations
        r'\b(find|search|list|show)\s+.*\b(files?|folders?|directories?)\b',
        r'\b(find|search)\s+.*\b(in|within)\s+.*\b(workspace|folder|directory)\b',
        
        # Conversational requests  
        r'\b(can you|could you|please)\s+.*(create|save|make|generate|find|search)\b',
        r'(i need|i want|i would like)\s+.*\b(file|folder|document)\b',
        
        # File extensions and workspace references
        r'\.(md|txt|json|csv|py|js|html|css)\b',
        r'\b(workspace|project|repository)\s+(folder|directory)\b',
        
        # File naming and renaming context
        r'\b(call it|name it|rename)\s+.*\b(different|another|new)\b',  # "call it different name"
        r'\b(save.*as|export.*as)\b',
        
        # File operation context
        r'\b(overwrite|replace|update)\s+.*\b(file|document)\b'
    ]
    
    # Exclude conversational questions (stronger patterns)
    exclusion_patterns = [
        r'\b(what is|what are|what\'s|how do|how does|explain|describe|tell me about|why)\b',
        r'\b(difference between|compare|versus|vs\.)\b',  # Comparison questions
        r'\b(i read|i saw|i heard|reading about)\b',
        r'\b(book|article|story|tutorial)\b',
        r'\b(have you|did you)\s+(created|made|saved|written|finished)\b',  # "have you created"
        r'\b(where is|can i see|do you see)\b',  # Location/visibility questions
        r'\b(learn|understand|know|help me understand)\b'  # Learning/educational context
    ]
    
    # Check exclusions first (status questions should not trigger tools)
    if any(re.search(pattern, prompt_lower) for pattern in exclusion_patterns):
        return False
    
    # Special case: "call it a different name" should trigger tools
    if "call it" in prompt_lower and ("different" in prompt_lower or "another" in prompt_lower):
        return True
    
    # Check for file action patterns
    if any(re.search(pattern, prompt_lower) for pattern in file_action_patterns):
        return True
    
    # Fallback to enhanced keyword detection with context awareness
    enhanced_keywords = [
        'file', 'folder', 'directory', 'create', 'make', 'generate', 'build',
        'save', 'write', 'edit', 'copy', 'move', 'list', 'search', 'find',
        'compress', 'backup', 'json', 'txt', 'md', 'workspace', 'put', 'store'
    ]
    
    # Only trigger on keywords if there's action context
    has_keywords = any(keyword in prompt_lower for keyword in enhanced_keywords)
    has_action_words = any(word in prompt_lower for word in ['create', 'make', 'save', 'write', 'generate', 'build', 'put', 'find', 'search', 'list', 'show', 'delete', 'remove'])
    
    return has_keywords and has_action_words

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
                logger.info("Memory status displayed")
            elif prompt == '/config':
                configure_settings()
            elif prompt == '/reset':
                memory.reset_memory()
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

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        logger.info("Testing Ollama connection...")
        host = APP_CONFIG['settings']['ollama_host']
        response = requests.get(f"http://{host}/api/tags", timeout=CONSTANTS['SUMMARY_TIMEOUT'])
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            qwen_models = [m['name'] for m in models if 'qwen' in m['name'].lower()]
            
            if qwen_models:
                print(f"✅ Ollama connected! Available Qwen models: {', '.join(qwen_models)}")
                logger.info(f"Ollama connection successful. Qwen models: {qwen_models}")
                return True
            else:
                print("⚠️  Ollama connected but no Qwen models found!")
                print(f"💡 Run: ollama pull {APP_CONFIG['settings']['model']}")
                logger.warning("No Qwen models found in Ollama")
                return False
        else:
            logger.error(f"Ollama returned status {response.status_code}: {response.text}")
            print(f"❌ Ollama error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Ollama connection timeout")
        print(f"❌ Ollama connection timeout ({CONSTANTS['SUMMARY_TIMEOUT']}s)")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
        
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to Ollama")
        print("❌ Could not connect to Ollama")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from Ollama: {e}")
        print("❌ Invalid response from Ollama")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error testing Ollama connection: {e}")
        print(f"❌ Ollama connection failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def configure_settings():
    """Configuration menu for changing settings"""
    global APP_CONFIG, file_manager, memory
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
                setup_directories()
                print("✅ Configuration saved successfully!")
                APP_CONFIG = config
                file_manager = FileManager()
                # Use global memory manager instead of creating new one
            else:
                print("❌ Failed to save configuration")
            break
        elif choice == 'x':
            print("Configuration cancelled")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    """Setup and start enhanced interactive mode"""
    global file_manager, memory, logger
    
    print("Initializing WorkspaceAI...")
    
    # Ensure config is saved if this is first run
    if not os.path.exists(get_config_path()):
        save_config(APP_CONFIG)
        print("Created default configuration")
    
    # Reconfigure logging with proper location
    logger = setup_logging()
    logger.info("WorkspaceAI starting up")
    
    # Initialize managers
    file_manager = FileManager()
    # Use global memory manager instead of creating a new one
    
    # Test Ollama connection
    if not test_ollama_connection():
        input("\nPress Enter to continue anyway or Ctrl+C to exit...")
    
    # Start interactive mode directly
    interactive_mode()

if __name__ == "__main__":
    main()
