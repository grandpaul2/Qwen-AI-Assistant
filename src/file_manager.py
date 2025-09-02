"""
File management system for WorkspaceAI
Handles all file operations within the secure workspace
"""

import os
import json
import shutil
import zipfile
import tarfile
import platform
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Union, Optional

from .config import CONSTANTS, APP_CONFIG, get_workspace_path
from .exceptions import (
    WorkspaceAIError, 
    ToolParameterError,
    handle_exception
)

logger = logging.getLogger(__name__)

class FileManager:
    """File management tools integrated directly into WorkspaceAI assistant"""
    
    def __init__(self, config=None):
        if config is None:
            config = APP_CONFIG
        
        self.base_path = get_workspace_path()
        self.safe_mode = config.get("safe_mode", True)
        self.default_compress_format = config.get("compress_format", "zip")
        self.search_case_sensitive = config.get("search_case_sensitive", False)
        self.search_content = config.get("search_content", True)
        self.search_max_file_kb = config.get("search_max_file_kb", CONSTANTS['SEARCH_MAX_FILE_KB'])
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
            raise WorkspaceAIError(
                f"Path traversal attempt: {full_path}",
                attempted_path=str(full_path)
            )
        
        return str(full_path)

    def _validate_filename(self, filename: str) -> None:
        """Validate filename for security and filesystem compatibility"""
        if not filename or not filename.strip():
            raise ToolParameterError(
                "Filename validation failed: empty filename",
                # user_message="Filename cannot be empty"
            )
        
        # Check for invalid characters (platform-specific)
        if platform.system() == "Windows":
            invalid_chars = '<>:"|?*'
            if any(char in filename for char in invalid_chars):
                raise ToolParameterError(
                    f"Filename validation failed: invalid characters in '{filename}'",
                    # user_message=f"Filename contains invalid characters: {invalid_chars}"
                )
            
            # Check for reserved names on Windows
            reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
            if filename.upper().split('.')[0] in reserved_names:
                raise ToolParameterError(
                    f"Filename validation failed: reserved name '{filename}'",
                    # user_message=f"Filename '{filename}' is reserved and cannot be used on Windows"
                )
        else:
            # Linux/Unix - only null character is forbidden
            if '\0' in filename:
                raise ToolParameterError(
                    "Filename validation failed: null character",
                    # user_message="Filename cannot contain null character"
                )
        
        # Check length
        if len(filename) > CONSTANTS['MAX_FILENAME_LENGTH']:
            raise ToolParameterError(
                f"Filename validation failed: too long ({len(filename)} chars)",
                # user_message=f"Filename too long (max {CONSTANTS['MAX_FILENAME_LENGTH']} characters)"
            )

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
            
        except (WorkspaceAIError, ToolParameterError) as e:
            # Return user-friendly error messages for custom exceptions
            logger.error(f"Error creating file '{file_name}': {e}")
            return f"Error: {e}"
        except Exception as e:
            # Convert any other exception to appropriate custom exception
            converted_error = handle_exception("create_file", e)
            logger.error(f"Error creating file '{file_name}': {converted_error}")
            return f"Error: {converted_error}"

    def read_file(self, file_name: str) -> str:
        """Read file contents from workspace"""
        try:
            file_path = self._resolve(file_name)
            
            if not os.path.exists(file_path):
                raise WorkspaceAIError(
                    f"File not found: {file_name}",
                    # file_path=file_name
                )
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                return file.read()
                
        except (WorkspaceAIError, WorkspaceAIError) as e:
            logger.error(f"Error reading file '{file_name}': {e}")
            return f"Error: {e}"
        except Exception as e:
            converted_error = handle_exception("read_file", e)
            logger.error(f"Error reading file '{file_name}': {converted_error}")
            return f"Error: {converted_error}"

    def write_to_file(self, file_name: str, content: str) -> str:
        """Write content to file in workspace"""
        try:
            original_file_name = file_name
            file_path = self._resolve(file_name)
            
            # Check if file exists and generate unique name if needed
            if os.path.exists(file_path):
                unique_file_name = self._generate_unique_filename(file_name)
                file_path = self._resolve(unique_file_name)
                file_name = unique_file_name
            
            dir_path = os.path.dirname(file_path)
            if dir_path:  # Only create directory if there is one
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            
            if file_name != original_file_name:
                return f"File created as '{file_name}' (original name already existed) in workspace!"
            else:
                return f"Content written to '{file_name}' successfully in workspace!"
                
        except WorkspaceAIError as e:
            logger.error(f"Error writing to file '{file_name}': {e}")
            return f"Error: {e}"
        except Exception as e:
            converted_error = handle_exception("write_to_file", e)
            logger.error(f"Error writing to file '{file_name}': {converted_error}")
            return f"Error: {converted_error}"

    def delete_file(self, file_name: str) -> str:
        """Delete a file from workspace"""
        if self.safe_mode:
            return "Safe mode is ON: delete_file is disabled."
            
        try:
            file_path = self._resolve(file_name)
            
            if not os.path.exists(file_path):
                raise WorkspaceAIError(
                    f"File not found: {file_name}",
                    # file_path=file_name
                )
            
            os.remove(file_path)
            return f"File '{file_name}' deleted successfully from workspace!"
            
        except (WorkspaceAIError, WorkspaceAIError) as e:
            logger.error(f"Error deleting file '{file_name}': {e}")
            return f"Error: {e}"
        except Exception as e:
            converted_error = handle_exception("delete_file", e)
            logger.error(f"Error deleting file '{file_name}': {converted_error}")
            return f"Error: {converted_error}"

    def list_files(self, subdirectory: str = "") -> str:
        """List files in workspace directory or subdirectory"""
        try:
            if subdirectory:
                directory_path = self._resolve(subdirectory)
            else:
                directory_path = self.base_path
                
            if not os.path.exists(directory_path):
                raise WorkspaceAIError(
                    f"Directory not found: {subdirectory}",
                    # file_path=subdirectory
                )
                
            files = os.listdir(directory_path)
            location = f"workspace/{subdirectory}" if subdirectory else "workspace"
            return f"Files in {location}:\n" + "\n".join(files)
            
        except (WorkspaceAIError, WorkspaceAIError) as e:
            logger.error(f"Error listing files in '{subdirectory}': {e}")
            return f"Error: {e}"
        except Exception as e:
            converted_error = handle_exception("list_files", e)
            logger.error(f"Error listing files in '{subdirectory}': {converted_error}")
            return f"Error: {converted_error}"

    # Additional methods... (continuing with all the other file operations)
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

    def copy_file(self, src_file: str, dest_file: str) -> str:
        """Copy a file within workspace"""
        src_file_path = self._resolve(src_file)
        dest_file_path = self._resolve(dest_file)
        guard_result = self._guard_overwrite(dest_file_path)
        if guard_result:
            return guard_result
        try:
            dest_dir = os.path.dirname(dest_file_path)
            if dest_dir:
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
            if dest_dir:
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

    def write_txt_file(self, file_name: str, content: str) -> str:
        """Write content to a .txt file in workspace - auto-generates unique name if needed"""
        if not file_name.endswith('.txt'):
            file_name += '.txt'
        
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
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(content, file, indent=4, ensure_ascii=False)
            
            if file_name != original_file_name:
                return f"JSON file created as '{file_name}' (original name already existed) in workspace!"
            else:
                return f"JSON written to '{file_name}' successfully in workspace!"
        except Exception as e:
            return f"Error writing JSON: {e}"

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


# Global file manager instance
file_manager = FileManager()
