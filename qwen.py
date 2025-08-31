#!/usr/bin/env python3
"""
Qwen with Rolling Memory + Supreme File Management
Enhanced chat with persistent memory across sessions

Version: 2.1
Author: Grandpaul
Updated: August 30, 2025
Features: Rolling memory, file management, software installation commands
"""

import json
import requests
import sys
import os
import time
from datetime import datetime
from tqdm import tqdm
import threading
import shutil
import logging
import hashlib
import zipfile
import tarfile
from collections import defaultdict
from typing import Optional, List, Union, Dict, Any

logging.basicConfig(level=logging.INFO)

# File Manager Class - Built into single file
class FileManager:
    """File management tools integrated directly into Qwen assistant"""
    
    def __init__(self):
        self.base_path = "C:\\Users\\Grandpaul\\.ollama\\outputs"
        self.safe_mode = True
        self.default_compress_format = "zip"
        self.search_case_sensitive = False
        self.search_content = True
        self.search_max_file_kb = 1024
        self.search_exclude_globs = ["*.zip", "*.tar", "*.gz", "*.png", "*.jpg", "*.pdf"]
        self.versions = defaultdict(list)
        self.tags = defaultdict(list)
        
        # Ensure base directory exists
        os.makedirs(self.base_path, exist_ok=True)

    def _resolve(self, path: Optional[str], *parts: str) -> str:
        """Join base_path with parts"""
        root = path if path else self.base_path
        return os.path.join(root, *[p for p in parts if p])

    def _guard_overwrite(self, path: str) -> Optional[str]:
        """Check safe mode for overwriting files"""
        if self.safe_mode and os.path.exists(path):
            return "Safe mode is ON: operation would overwrite an existing file."
        return None

    def create_file(self, file_name: str, content: str = "", path: Optional[str] = None) -> str:
        """Create a new file with content"""
        file_path = self._resolve(path, file_name)
        guard_result = self._guard_overwrite(file_path)
        if guard_result:
            return guard_result
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return f"File '{file_name}' created successfully!"
        except Exception as e:
            return f"Error creating file: {e}"

    def read_file(self, file_name: str, path: Optional[str] = None) -> str:
        """Read file contents"""
        file_path = self._resolve(path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_to_file(self, file_name: str, content: str, path: Optional[str] = None) -> str:
        """Write content to file"""
        file_path = self._resolve(path, file_name)
        guard_result = self._guard_overwrite(file_path)
        if guard_result:
            return guard_result
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return f"Content written to '{file_name}' successfully!"
        except Exception as e:
            return f"Error writing file: {e}"

    def delete_file(self, file_name: str, path: Optional[str] = None) -> str:
        """Delete a file"""
        if self.safe_mode:
            return "Safe mode is ON: delete_file is disabled."
        file_path = self._resolve(path, file_name)
        try:
            os.remove(file_path)
            return f"File '{file_name}' deleted successfully!"
        except Exception as e:
            return f"Error deleting file: {e}"

    def list_files(self, path: Optional[str] = None) -> str:
        """List files in directory"""
        directory_path = path if path else self.base_path
        try:
            files = os.listdir(directory_path)
            return "Files in directory:\n" + "\n".join(files)
        except Exception as e:
            return f"Error listing files: {e}"

    def create_folder(self, folder_name: str, path: Optional[str] = None) -> str:
        """Create a new folder"""
        folder_path = self._resolve(path, folder_name)
        try:
            os.makedirs(folder_path, exist_ok=True)
            return f"Folder '{folder_name}' created successfully!"
        except Exception as e:
            return f"Error creating folder: {e}"

    def delete_folder(self, folder_name: str, path: Optional[str] = None) -> str:
        """Delete a folder"""
        if self.safe_mode:
            return "Safe mode is ON: delete_folder is disabled."
        folder_path = self._resolve(path, folder_name)
        try:
            shutil.rmtree(folder_path)
            return f"Folder '{folder_name}' deleted successfully!"
        except Exception as e:
            return f"Error deleting folder: {e}"

    def copy_file(self, src_file: str, dest_file: str, src_path: Optional[str] = None, dest_path: Optional[str] = None) -> str:
        """Copy a file"""
        src_file_path = self._resolve(src_path, src_file)
        dest_file_path = self._resolve(dest_path, dest_file)
        guard_result = self._guard_overwrite(dest_file_path)
        if guard_result:
            return guard_result
        try:
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
            shutil.copy2(src_file_path, dest_file_path)
            return f"File '{src_file}' copied to '{dest_file}' successfully!"
        except Exception as e:
            return f"Error copying file: {e}"

    def move_file(self, src_file: str, dest_file: str, src_path: Optional[str] = None, dest_path: Optional[str] = None) -> str:
        """Move a file"""
        src_file_path = self._resolve(src_path, src_file)
        dest_file_path = self._resolve(dest_path, dest_file)
        guard_result = self._guard_overwrite(dest_file_path)
        if guard_result:
            return guard_result
        try:
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
            shutil.move(src_file_path, dest_file_path)
            return f"File '{src_file}' moved to '{dest_file}' successfully!"
        except Exception as e:
            return f"Error moving file: {e}"

    def search_files(self, keyword: str, path: Optional[str] = None) -> List[str]:
        """Search for files by keyword"""
        import fnmatch
        search_path = path if path else self.base_path
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

    def compress_file(self, file_name: str, output_filename: str, format: Optional[str] = None, path: Optional[str] = None) -> str:
        """Compress a file"""
        fmt = format or self.default_compress_format
        file_path = self._resolve(path, file_name)
        output_path = self._resolve(path, output_filename)
        
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
            return f"File '{file_name}' compressed to '{output_filename}' as {fmt}."
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

    def read_json_file(self, file_name: str, path: Optional[str] = None) -> Union[Dict[str, Any], str]:
        """Read a JSON file"""
        file_path = self._resolve(path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            return f"Error reading JSON: {e}"

    def write_json_file(self, file_name: str, content: Dict[str, Any], path: Optional[str] = None) -> str:
        """Write data to JSON file"""
        file_path = self._resolve(path, file_name)
        guard_result = self._guard_overwrite(file_path)
        if guard_result:
            return guard_result
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(content, file, indent=4)
            return f"JSON written to '{file_name}' successfully!"
        except Exception as e:
            return f"Error writing JSON: {e}"

    def get_file_metadata(self, file_name: str, path: Optional[str] = None) -> Union[Dict[str, str], str]:
        """Get file metadata"""
        file_path = self._resolve(path, file_name)
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
MEMORY_FILE = r'C:\Users\Grandpaul\.ollama\memory\memory.json'

class MemoryManager:
    def __init__(self):
        self.current_conversation = []
        self.recent_conversations = []  # Last 2 full conversations
        self.summarized_conversations = []  # Next 8 summarized
        self.load_memory()
    
    def load_memory(self):
        """Load persistent memory from file"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
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
            os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
            data = {
                'current_conversation': self.current_conversation,
                'recent_conversations': self.recent_conversations,
                'summarized_conversations': self.summarized_conversations,
                'last_updated': datetime.now().isoformat()
            }
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
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
        
        # Auto-save after each message
        threading.Thread(target=self.save_memory, daemon=True).start()
    
    def start_new_conversation(self):
        """Move current conversation to recent and start fresh"""
        if not self.current_conversation:
            return
        
        # Add current to recent conversations
        conversation_data = {
            'date': datetime.now().isoformat(),
            'messages': self.current_conversation.copy()
        }
        self.recent_conversations.insert(0, conversation_data)
        
        # Keep only last 2 recent conversations
        if len(self.recent_conversations) > 2:
            # Move oldest recent to summarized
            oldest = self.recent_conversations.pop()
            summary = self.summarize_conversation(oldest['messages'])
            self.summarized_conversations.insert(0, {
                'date': oldest['date'],
                'summary': summary
            })
        
        # Keep only 8 summarized conversations
        self.summarized_conversations = self.summarized_conversations[:8]
        
        # Clear current conversation
        self.current_conversation = []
        self.save_memory()
        print("Started new conversation (previous saved to memory)")
    
    def summarize_conversation(self, messages):
        """Create AI summary of conversation"""
        try:
            # Build summary prompt
            conversation_text = ""
            for msg in messages[-10:]:  # Last 10 messages only
                if msg['role'] in ['user', 'assistant']:
                    conversation_text += f"{msg['role']}: {msg['content'][:200]}\n"
            
            if not conversation_text.strip():
                return "Empty conversation"
            
            summary_prompt = f"Summarize this conversation in 2-3 sentences, focusing on key topics, files created/modified, and important context:\n\n{conversation_text}"
            
            response = requests.post("http://localhost:11434/api/chat", json={
                "model": "qwen2.5:3b",
                "messages": [{"role": "user", "content": summary_prompt}],
                "stream": False
            }, timeout=10)
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Conversation from {messages[0]['timestamp'][:10]} with {len(messages)} messages"
        except:
            return f"Conversation from {messages[0]['timestamp'][:10]} with {len(messages)} messages"
    
    def get_context_messages(self):
        """Build context from memory for API calls"""
        context_messages = []
        
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

def show_progress(description, duration=2):
    """Show progress bar for operations"""
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
                "description": "Create a new file with optional content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "Target file path"},
                        "content": {"type": "string", "description": "Text content to write"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the entire content of a text file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File path to read"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_to_file",
                "description": "Write text content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File path to write"},
                        "content": {"type": "string", "description": "Text content to write"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory to list"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_folder",
                "description": "Create a new folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder_name": {"type": "string", "description": "Name of the folder to create"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["folder_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_file",
                "description": "Delete a file (blocked when safe_mode is True)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "Path to the file to delete"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_folder",
                "description": "Delete a folder (blocked when safe_mode is True)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder_name": {"type": "string", "description": "Name of the folder to delete"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["folder_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search filenames and optionally contents for a keyword",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "Keyword to search for"},
                        "path": {"type": "string", "description": "Directory root to search"}
                    },
                    "required": ["keyword"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compress_file",
                "description": "Compress a file using zip, tar, or gztar format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "Source file to compress"},
                        "output_filename": {"type": "string", "description": "Output archive name"},
                        "format": {"type": "string", "description": "zip | tar | gztar"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name", "output_filename"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "backup_files",
                "description": "Full copy from source to backup directory",
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
                "description": "Generate installation commands for popular software",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "software": {"type": "string", "description": "Software name (e.g., 'python', 'git', 'vscode', 'nodejs')"},
                        "method": {"type": "string", "description": "Installation method: 'winget', 'pip', 'npm', 'auto' (default)"}
                    },
                    "required": ["software"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "copy_file",
                "description": "Copy a file from source to destination",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "src_file": {"type": "string", "description": "Source file name"},
                        "dest_file": {"type": "string", "description": "Destination file name"},
                        "src_path": {"type": "string", "description": "Source directory path"},
                        "dest_path": {"type": "string", "description": "Destination directory path"}
                    },
                    "required": ["src_file", "dest_file"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "move_file",
                "description": "Move a file from source to destination",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "src_file": {"type": "string", "description": "Source file name"},
                        "dest_file": {"type": "string", "description": "Destination file name"},
                        "src_path": {"type": "string", "description": "Source directory path"},
                        "dest_path": {"type": "string", "description": "Destination directory path"}
                    },
                    "required": ["src_file", "dest_file"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_json_file",
                "description": "Read and parse a JSON file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "JSON file name"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_json_file",
                "description": "Write data to a JSON file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "JSON file name"},
                        "content": {"type": "object", "description": "Data to write as JSON"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_file_metadata",
                "description": "Get metadata information about a file (size, dates)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "File name"},
                        "path": {"type": "string", "description": "Override working directory"}
                    },
                    "required": ["file_name"]
                }
            }
        }
        # File management tools ready for Qwen 2.5:3B
    ]

def call_ollama_with_tools(prompt: str, model: str = "qwen2.5:3b", use_tools: bool = True):
    """Call Ollama with conversation memory and tools"""
    
    # Add user message to memory
    memory.add_message("user", prompt)
    
    # Build request with conversation context
    messages = memory.get_context_messages()
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
    
    # Ollama API call
    response = requests.post("http://localhost:11434/api/chat", json=request_data)
    
    if progress_thread:
        progress_thread.join()
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    message = result["message"]
    
    # Add space before assistant response
    print()
    assistant_content = message.get('content', '')
    print(f"Assistant: {assistant_content}")
    
    # Add assistant message to memory
    tool_calls_data = message.get('tool_calls', None)
    memory.add_message("assistant", assistant_content, tool_calls_data)
    
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
            if hasattr(file_manager, function_name):
                try:
                    result = getattr(file_manager, function_name)(**function_args)
                    print(f"✅ Result: {result}")
                    
                    # Add tool result to memory
                    memory.add_message("tool", f"{function_name}: {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    memory.add_message("tool", f"{function_name} error: {e}")
            elif function_name == "generate_install_commands":
                try:
                    result = generate_install_commands(**function_args)
                    print(f"✅ Generated Commands:")
                    print(result)
                    memory.add_message("tool", f"Generated install commands: {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    memory.add_message("tool", f"Command generation error: {e}")
            else:
                print(f"❌ Unknown function: {function_name}")
            
            if progress_thread is not None:
                progress_thread.join()

def generate_install_commands(software, method="auto"):
    """Generate installation commands for popular software"""
    
    software = software.lower().strip()
    method = method.lower().strip()
    
    # Software database with multiple installation methods
    software_db = {
        "python": {
            "winget": "winget install Python.Python.3.12",
            "direct": "Download from: https://python.org/downloads/\n- Choose 'Add to PATH' during installation",
            "description": "Python programming language"
        },
        "git": {
            "winget": "winget install Git.Git",
            "direct": "Download from: https://git-scm.com/downloads",
            "description": "Version control system"
        },
        "vscode": {
            "winget": "winget install Microsoft.VisualStudioCode",
            "direct": "Download from: https://code.visualstudio.com/download",
            "description": "Code editor"
        },
        "nodejs": {
            "winget": "winget install OpenJS.NodeJS",
            "direct": "Download from: https://nodejs.org/en/download/",
            "description": "JavaScript runtime"
        },
        "chrome": {
            "winget": "winget install Google.Chrome",
            "direct": "Download from: https://chrome.google.com/",
            "description": "Web browser"
        },
        "firefox": {
            "winget": "winget install Mozilla.Firefox",
            "direct": "Download from: https://firefox.com/",
            "description": "Web browser"
        },
        "7zip": {
            "winget": "winget install 7zip.7zip",
            "direct": "Download from: https://7-zip.org/",
            "description": "File archiver"
        },
        "discord": {
            "winget": "winget install Discord.Discord",
            "direct": "Download from: https://discord.com/download",
            "description": "Communication platform"
        },
        "vlc": {
            "winget": "winget install VideoLAN.VLC",
            "direct": "Download from: https://videolan.org/vlc/",
            "description": "Media player"
        },
        "notepad++": {
            "winget": "winget install Notepad++.Notepad++",
            "direct": "Download from: https://notepad-plus-plus.org/downloads/",
            "description": "Text editor"
        },
        "open-webui": {
            "pip": "pip install open-webui\n# Then run with: open-webui serve",
            "docker": "docker run -d --name open-webui -p 3000:8080 ghcr.io/open-webui/open-webui:main",
            "direct": "Download from: https://github.com/open-webui/open-webui",
            "description": "Web UI for LLMs"
        },
        "ollama": {
            "direct": "Download from: https://ollama.ai/download\n# After install: ollama run llama2",
            "description": "Run LLMs locally"
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
    result = f"\n📦 {sw['description']} ({found_software})\n" + "="*50 + "\n"
    
    if method == "auto":
        # Determine best method automatically
        if "winget" in sw:
            result += f"🚀 RECOMMENDED (Windows Package Manager):\n{sw['winget']}\n\n"
        
        if "pip" in sw:
            result += f"🐍 PIP Install:\n{sw['pip']}\n\n"
        
        if "direct" in sw:
            result += f"🌐 Direct Download:\n{sw['direct']}\n\n"
            
        if "docker" in sw:
            result += f"🐳 Docker:\n{sw['docker']}\n\n"
    
    elif method in sw:
        result += f"📋 {method.upper()} Install:\n{sw[method]}\n"
    else:
        available = list(sw.keys())
        available.remove("description")
        result += f"Method '{method}' not available.\nAvailable methods: {', '.join(available)}\n"
        result += f"🚀 Default method:\n{sw.get('winget', sw.get('direct', 'No installation method available'))}"
    
    result += "\n💡 TIP: Run commands in PowerShell as Administrator if needed"
    return result

def interactive_mode():
    """Interactive chat mode with rolling memory"""
    print("\n" + "="*70)
    print("QWEN 2.5 ASSISTANT with File Management v2.1")
    print("="*70)
    print(f"Base path: {file_manager.base_path}")
    print(f"Safe mode: {'ON' if file_manager.safe_mode else 'OFF'}")
    print(f"Memory: {len(memory.recent_conversations)} recent + {len(memory.summarized_conversations)} summarized")

    if memory.recent_conversations or memory.summarized_conversations:
        print("Continuing from previous conversations...")

    print("\nAvailable Commands:")
    print("- Normal questions and file operations")
    print("- 'chat: question' - force normal chat mode")
    print("- 'tools: command' - force file tools mode")
    print("- 'install python' - software installation commands")

    print("\nControl Commands:")
    print("- /new        Start new conversation")
    print("- /memory     Show memory status")
    print("- /reset      Clear all memory")
    print("- exit        Quit")
    print("="*70)
    print("Ready for your questions...")

    while True:
        try:
            prompt = input("\nYou: ").strip()
            if prompt.lower() in ['exit', 'quit', 'q']:
                print("Exiting Qwen Assistant.")
                break
            elif prompt == '/new':
                memory.start_new_conversation()
            elif prompt == '/memory':
                print(f"Memory Status:")
                print(f"  Current: {len(memory.current_conversation)} messages")
                print(f"  Recent: {len(memory.recent_conversations)} full conversations")
                print(f"  Summarized: {len(memory.summarized_conversations)} conversations")
            elif prompt == '/reset':
                memory.reset_memory()
                memory.save_memory()
                print("Memory cleared")
            elif not prompt:
                continue
            elif prompt.lower().startswith('chat:'):
                actual_prompt = prompt[5:].strip()
                call_ollama_with_tools(actual_prompt, use_tools=False)
            elif prompt.lower().startswith('tools:'):
                actual_prompt = prompt[6:].strip()
                call_ollama_with_tools(actual_prompt, use_tools=True)
            else:
                file_keywords = ['file', 'folder', 'create', 'delete', 'read', 'write',
                                 'copy', 'move', 'list', 'search', 'compress', 'backup',
                                 'json', 'metadata', 'sync']
                looks_like_file_task = any(keyword in prompt.lower() for keyword in file_keywords)
                call_ollama_with_tools(prompt, use_tools=looks_like_file_task)
        except KeyboardInterrupt:
            print("\nSaving memory and exiting...")
            memory.save_memory()
            break

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            qwen_models = [m['name'] for m in models if 'qwen' in m['name'].lower()]
            if qwen_models:
                print(f"✅ Ollama connected! Available Qwen models: {', '.join(qwen_models)}")
                return True
            else:
                print("⚠️  Ollama connected but no Qwen models found!")
                print("💡 Run: ollama pull qwen2.5:3b")
                return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def main():
    """Setup and start enhanced interactive mode"""
    # Test Ollama connection first
    if not test_ollama_connection():
        input("\nPress Enter to continue anyway or Ctrl+C to exit...")
    
    # Install progress bar library if needed
    try:
        pass  # tqdm is already imported at the top
    except ImportError:
        print("Installing progress bar library...")
        os.system("pip install tqdm")
    
    # Configure file manager
    file_manager.base_path = "C:\\Users\\Grandpaul\\.ollama\\outputs"
    file_manager.safe_mode = True
    os.makedirs(file_manager.base_path, exist_ok=True)
    
    # Start interactive mode
    interactive_mode()

if __name__ == "__main__":
    main()
