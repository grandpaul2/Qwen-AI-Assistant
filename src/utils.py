"""
Utility functions for WorkspaceAI
"""

import os
import sys
import time
import platform
import logging
import shutil
from tqdm import tqdm
from .config import CONSTANTS

# Import custom exceptions
from .exceptions import (
    WorkspaceAIError,
    handle_exception
)

def detect_linux_package_manager():
    """Detect the available package manager on Linux systems - backward compatible wrapper"""
    try:
        return detect_linux_package_manager_with_exceptions()
    except Exception as e:
        # Log error but return None for backward compatibility
        logging.error(f"Package manager detection failed: {e}")
        print(f"Warning: Package manager detection error: {str(e)}")
        return None

def detect_linux_package_manager_with_exceptions():
    """
    Detect the available package manager on Linux systems - raises exceptions for validation errors
    
    Returns:
        str or None: Package manager name if found, None if none found
        
    Raises:
        WorkspaceAIError: If not on Linux
        WorkspaceAIError: If package manager detection fails
    """
    # Check if we're on Linux
    if platform.system().lower() != 'linux':
        error = WorkspaceAIError(f"Package manager detection only works on Linux, current OS: {platform.system()}")
        logging.error(f"Package manager detection failed: {error}")
        raise error
    
    managers = {
        'apt': ['apt', 'apt-get'],
        'dnf': ['dnf'],
        'yum': ['yum'],
        'pacman': ['pacman'],
        'zypper': ['zypper'],
        'emerge': ['emerge'],
        'apk': ['apk']
    }
    
    try:
        for manager, commands in managers.items():
            for cmd in commands:
                try:
                    # Use shutil.which to check if command exists (cross-platform)
                    if shutil.which(cmd):
                        return manager
                except OSError as e:
                    # Log individual command failures but continue
                    logging.debug(f"Failed to check command {cmd}: {e}")
                    continue
                    
        # No package manager found - this is not an error, just return None
        return None
        
    except Exception as e:
        # Handle unexpected errors
        converted_error = handle_exception("package_manager_detection", e)
        pass  # Simplified
        logging.error(f"Package manager detection failed: {converted_error}")
        raise converted_error

def show_progress(description, duration=None):
    """Show progress bar for operations - backward compatible wrapper"""
    try:
        return show_progress_with_exceptions(description, duration)
    except Exception as e:
        # Log error but continue with minimal output for backward compatibility
        logging.error(f"Progress display failed: {e}")
        print(f"Warning: Progress display error: {str(e)}")
        print(f"\n{description if description else 'Operation'} - Please wait...")

def show_progress_with_exceptions(description, duration=None):
    """
    Show progress bar for operations - raises exceptions for validation errors
    
    Args:
        description: Description of the operation
        duration: Duration in seconds (optional)
        
    Raises:
        WorkspaceAIError: For progress display issues
    """
    # Input validation
    if description is None:
        error = WorkspaceAIError("Description cannot be None for progress display")
        pass  # Simplified
        logging.error(f"Progress display failed: {error}")
        raise error
        
    if not isinstance(description, str):
        error = WorkspaceAIError(f"Description must be a string, got {type(description).__name__}")
        pass  # Simplified
        logging.error(f"Progress display failed: {error}")
        raise error
    
    # Handle duration parameter
    if duration is None:
        try:
            duration = CONSTANTS['PROGRESS_DURATION']
        except KeyError:
            duration = 3.0  # Default fallback
            logging.warning("PROGRESS_DURATION not found in constants, using default 3.0 seconds")
    
    if not isinstance(duration, (int, float)):
        error = WorkspaceAIError(f"Duration must be a number, got {type(duration).__name__}")
        pass  # Simplified
        logging.error(f"Progress display failed: {error}")
        raise error
        
    if duration < 0:
        error = WorkspaceAIError(f"Duration cannot be negative: {duration}")
        pass  # Simplified
        logging.error(f"Progress display failed: {error}")
        raise error
        
    if duration > 300:  # 5 minutes max
        error = WorkspaceAIError(f"Duration too long: {duration} seconds (max 300)")
        pass  # Simplified
        logging.error(f"Progress display failed: {error}")
        raise error

    try:
        print(f"\n{description}")
        
        # Calculate steps for progress bar
        steps = max(1, int(duration * 10))  # Minimum 1 step
        sleep_time = duration / steps
        
        for _ in tqdm(range(steps), desc="Progress", ncols=70):
            time.sleep(sleep_time)
        print()
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        raise
    except Exception as e:
        # Handle unexpected errors
        converted_error = handle_exception("progress_display", e)
        pass  # Simplified
        pass  # Simplified
        logging.error(f"Progress display failed: {converted_error}")
        raise converted_error

def is_safe_filename(filename):
    """Check if filename is safe (no path traversal) - backward compatible wrapper"""
    try:
        return is_safe_filename_with_exceptions(filename)
    except Exception as e:
        # Log error but return False for safety in backward compatibility
        logging.error(f"Filename safety check failed: {e}")
        print(f"Warning: Filename safety check error: {str(e)}")
        return False

def is_safe_filename_with_exceptions(filename):
    """
    Check if filename is safe (no path traversal) - raises exceptions for validation errors
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if filename is safe, False otherwise
        
    Raises:
        WorkspaceAIError: For filename validation issues
    """
    # Handle None input
    if filename is None:
        return False
    
    # Check type
    if not isinstance(filename, str):
        error = WorkspaceAIError(f"Filename must be a string, got {type(filename).__name__}")
        pass  # Simplified
        logging.error(f"Filename safety check failed: {error}")
        raise error
    
    # Empty filename check
    if not filename:
        return False
    
    try:
        # Check for path traversal attempts
        if '..' in filename or filename.startswith('/') or ':' in filename:
            return False
        
        # Check for reserved names on Windows
        if platform.system() == 'Windows':
            reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
            if filename.upper().split('.')[0] in reserved_names:
                return False
        
        # Check length
        try:
            max_length = CONSTANTS['MAX_FILENAME_LENGTH']
        except KeyError:
            max_length = 255  # Default safe limit
            logging.warning("MAX_FILENAME_LENGTH not found in constants, using default 255")
            
        if len(filename) > max_length:
            return False
        
        return True
        
    except Exception as e:
        # Handle unexpected errors
        converted_error = handle_exception("filename_safety_check", e)
        pass  # Simplified
        logging.error(f"Filename safety check failed: {converted_error}")
        raise converted_error

def sanitize_filename(filename):
    """Sanitize filename for safety - backward compatible wrapper"""
    try:
        return sanitize_filename_with_exceptions(filename)
    except Exception as e:
        # Log error but return safe default in backward compatibility
        logging.error(f"Filename sanitization failed: {e}")
        print(f"Warning: Filename sanitization error: {str(e)}")
        return "safe_file.txt"

def sanitize_filename_with_exceptions(filename):
    """
    Sanitize filename for filesystem use - raises exceptions for validation errors
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: Sanitized filename safe for filesystem use
        
    Raises:
        WorkspaceAIError: For filename processing issues
    """
    # Handle None/empty input
    if not filename:
        return "file"
    
    # Check type
    if not isinstance(filename, str):
        error = WorkspaceAIError(f"Filename must be a string, got {type(filename).__name__}")
        pass  # Simplified
        logging.error(f"Filename sanitization failed: {error}")
        raise error
    
    try:
        # Remove path separators and dangerous characters
        sanitized = filename.replace('/', '_').replace('\\', '_').replace('..', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '._-')
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            return "file"
        
        # Truncate if too long
        try:
            max_length = CONSTANTS['MAX_FILENAME_LENGTH']
        except KeyError:
            max_length = 255  # Default safe limit
            logging.warning("MAX_FILENAME_LENGTH not found in constants, using default 255")
            
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
        
    except Exception as e:
        # Handle unexpected errors
        converted_error = handle_exception("filename_sanitization", e)
        pass  # Simplified
        logging.error(f"Filename sanitization failed: {converted_error}")
        raise converted_error

def get_unique_filename(directory, base_filename):
    """Generate a unique filename by adding numbers if needed - backward compatible wrapper"""
    try:
        return get_unique_filename_with_exceptions(directory, base_filename)
    except Exception as e:
        # Log error but return safe default in backward compatibility
        logging.error(f"Unique filename generation failed: {e}")
        print(f"Warning: Unique filename generation error: {str(e)}")
        import time
        return f"file_{int(time.time())}.txt"

def get_unique_filename_with_exceptions(directory, base_filename):
    """
    Generate a unique filename by adding numbers if needed - raises exceptions for validation errors
    
    Args:
        directory: Directory to check for existing files
        base_filename: Base filename to make unique
        
    Returns:
        str: Unique filename that doesn't exist in the directory
        
    Raises:
        WorkspaceAIError: For directory or filename issues
        WorkspaceAIError: For validation errors
    """
    # Validate inputs
    if directory is None:
        error = WorkspaceAIError("Directory cannot be None")
        pass  # Simplified
        logging.error(f"Unique filename generation failed: {error}")
        raise error
        
    if base_filename is None:
        error = WorkspaceAIError("Base filename cannot be None")
        pass  # Simplified
        logging.error(f"Unique filename generation failed: {error}")
        raise error
    
    # Check types
    if not isinstance(directory, str):
        error = WorkspaceAIError(f"Directory must be a string, got {type(directory).__name__}")
        pass  # Simplified
        logging.error(f"Unique filename generation failed: {error}")
        raise error
        
    if not isinstance(base_filename, str):
        error = WorkspaceAIError(f"Base filename must be a string, got {type(base_filename).__name__}")
        pass  # Simplified
        logging.error(f"Unique filename generation failed: {error}")
        raise error
    
    try:
        # Check if directory exists
        if not os.path.exists(directory):
            error = WorkspaceAIError(f"Directory does not exist: {directory}")
            pass  # Simplified
            logging.error(f"Unique filename generation failed: {error}")
            raise error
            
        if not os.path.isdir(directory):
            error = WorkspaceAIError(f"Path is not a directory: {directory}")
            pass  # Simplified
            logging.error(f"Unique filename generation failed: {error}")
            raise error
        
        # If base filename doesn't exist, return it
        if not os.path.exists(os.path.join(directory, base_filename)):
            return base_filename
        
        name, ext = os.path.splitext(base_filename)
        counter = 1
        max_attempts = 10000  # Prevent infinite loops
        
        while counter <= max_attempts:
            new_filename = f"{name}_{counter}{ext}"
            if not os.path.exists(os.path.join(directory, new_filename)):
                return new_filename
            counter += 1
        
        # If we've tried too many times, use timestamp
        import time
        timestamp_filename = f"{name}_{int(time.time())}{ext}"
        return timestamp_filename
        
    except Exception as e:
        # Handle unexpected errors
        converted_error = handle_exception("unique_filename_generation", e)
        pass  # Simplified
        pass  # Simplified
        logging.error(f"Unique filename generation failed: {converted_error}")
        raise converted_error

def bytes_to_human_readable(size_bytes):
    """Convert bytes to human readable format - backward compatible wrapper"""
    try:
        return bytes_to_human_readable_with_exceptions(size_bytes)
    except Exception as e:
        # Log error but return safe default in backward compatibility
        logging.error(f"Bytes to human readable conversion failed: {e}")
        print(f"Warning: Bytes conversion error: {str(e)}")
        return "Unknown size"

def bytes_to_human_readable_with_exceptions(size_bytes):
    """
    Convert bytes to human readable format - raises exceptions for validation errors
    
    Args:
        size_bytes: Number of bytes to convert
        
    Returns:
        str: Human readable size format (e.g., "1.5 MB")
        
    Raises:
        WorkspaceAIError: For input validation issues
    """
    # Handle None input
    if size_bytes is None:
        error = WorkspaceAIError("Size bytes cannot be None")
        pass  # Simplified
        logging.error(f"Bytes conversion failed: {error}")
        raise error
    
    # Check if it's a number
    if not isinstance(size_bytes, (int, float)):
        error = WorkspaceAIError(f"Size bytes must be a number, got {type(size_bytes).__name__}")
        pass  # Simplified
        logging.error(f"Bytes conversion failed: {error}")
        raise error
    
    # Check for negative values
    if size_bytes < 0:
        error = WorkspaceAIError(f"Size bytes cannot be negative: {size_bytes}")
        pass  # Simplified
        logging.error(f"Bytes conversion failed: {error}")
        raise error
    
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]  # Added PB for very large files
        import math
        
        # Prevent overflow for very large numbers
        if size_bytes > 1024**6:  # Larger than 1024 PB
            return f"{size_bytes:.2e} B"  # Scientific notation
        
        i = int(math.floor(math.log(size_bytes, 1024)))
        
        # Ensure index is within bounds
        if i >= len(size_names):
            i = len(size_names) - 1
        
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
        
    except Exception as e:
        # Handle unexpected errors
        converted_error = handle_exception("bytes_conversion", e)
        pass  # Simplified
        logging.error(f"Bytes conversion failed: {converted_error}")
        raise converted_error

def validate_json_string(json_str):
    """Validate if string is valid JSON - backward compatible wrapper"""
    try:
        return validate_json_string_with_exceptions(json_str)
    except Exception as e:
        # Log error but return False for safety in backward compatibility
        logging.error(f"JSON validation failed: {e}")
        print(f"Warning: JSON validation error: {str(e)}")
        return False

def validate_json_string_with_exceptions(json_str):
    """
    Validate if string is valid JSON - raises exceptions for validation errors
    
    Args:
        json_str: String to validate as JSON
        
    Returns:
        bool: True if valid JSON, False otherwise
        
    Raises:
        WorkspaceAIError: For input validation issues
    """
    import json  # Import at function level for consistency
    
    # Handle None input
    if json_str is None:
        return False
    
    # Check type
    if not isinstance(json_str, str):
        error = WorkspaceAIError(f"JSON string must be a string, got {type(json_str).__name__}")
        pass  # Simplified
        logging.error(f"JSON validation failed: {error}")
        raise error
    
    # Check size limit to prevent memory issues
    max_size = 10 * 1024 * 1024  # 10MB limit
    if len(json_str) > max_size:
        error = WorkspaceAIError(f"JSON string too large: {len(json_str)} bytes (max {max_size})")
        pass  # Simplified
        logging.error(f"JSON validation failed: {error}")
        raise error
    
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        # This is expected for invalid JSON, return False
        return False
    except TypeError:
        # This is expected for non-string input, return False
        return False
    except Exception as e:
        # Handle unexpected errors
        converted_error = handle_exception("json_validation", e)
        pass  # Simplified
        logging.error(f"JSON validation failed: {converted_error}")
        raise converted_error


def generate_install_commands(software, method="auto"):
    """Generate installation commands for popular software (cross-platform) - backward compatible wrapper"""
    try:
        return generate_install_commands_with_exceptions(software, method)
    except Exception as e:
        # Log error but return helpful message in backward compatibility
        logging.error(f"Install command generation failed: {e}")
        print(f"Warning: Install command generation error: {str(e)}")
        return f"Error generating install commands for {software}. Please check the software name and try again."

def generate_install_commands_with_exceptions(software, method="auto"):
    """
    Generate installation commands for popular software (cross-platform) - raises exceptions for validation errors
    
    Args:
        software: Name of software to install
        method: Installation method ("auto", "manual", or specific package manager)
        
    Returns:
        str: Installation commands and instructions
        
    Raises:
        WorkspaceAIError: For input validation issues
        WorkspaceAIError: For unsupported operating systems
    """
    # Validate inputs
    if software is None:
        error = WorkspaceAIError("Software name cannot be None")
        pass  # Simplified
        logging.error(f"Install command generation failed: {error}")
        raise error
        
    if not isinstance(software, str):
        error = WorkspaceAIError(f"Software name must be a string, got {type(software).__name__}")
        pass  # Simplified
        logging.error(f"Install command generation failed: {error}")
        raise error
    
    if method is None:
        method = "auto"
        
    if not isinstance(method, str):
        error = WorkspaceAIError(f"Method must be a string, got {type(method).__name__}")
        pass  # Simplified
        logging.error(f"Install command generation failed: {error}")
        raise error
    
    try:
        os_type = platform.system().lower()
        
        # Software installation database
        install_db = {
            "python": {
                "windows": "winget install Python.Python.3.12",
                "macos": "brew install python@3.12",
                "linux": {
                    "apt": "sudo apt update && sudo apt install python3 python3-pip",
                    "dnf": "sudo dnf install python3 python3-pip",
                    "pacman": "sudo pacman -S python python-pip",
                    "zypper": "sudo zypper install python3 python3-pip"
                },
                "manual": "Download from https://python.org/downloads/"
            },
            "nodejs": {
                "windows": "winget install OpenJS.NodeJS",
                "macos": "brew install node",
                "linux": {
                    "apt": "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs",
                    "dnf": "sudo dnf install npm nodejs",
                    "pacman": "sudo pacman -S nodejs npm",
                    "zypper": "sudo zypper install nodejs18 npm18"
                },
                "manual": "Download from https://nodejs.org/"
            },
            "git": {
                "windows": "winget install Git.Git",
                "macos": "brew install git",
                "linux": {
                    "apt": "sudo apt update && sudo apt install git",
                    "dnf": "sudo dnf install git",
                    "pacman": "sudo pacman -S git",
                    "zypper": "sudo zypper install git"
                },
                "manual": "Download from https://git-scm.com/"
            },
            "docker": {
                "windows": "winget install Docker.DockerDesktop",
                "macos": "brew install --cask docker",
                "linux": {
                    "apt": "curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER",
                    "dnf": "sudo dnf install docker docker-compose && sudo systemctl enable docker",
                    "pacman": "sudo pacman -S docker docker-compose && sudo systemctl enable docker",
                    "zypper": "sudo zypper install docker docker-compose && sudo systemctl enable docker"
                },
                "manual": "Download from https://docker.com/get-started"
            },
            "vscode": {
                "windows": "winget install Microsoft.VisualStudioCode",
                "macos": "brew install --cask visual-studio-code",
                "linux": {
                    "apt": "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg && sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/ && sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list' && sudo apt update && sudo apt install code",
                    "dnf": "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc && sudo sh -c 'echo -e \"[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/yum.repos.d/vscode.repo' && sudo dnf check-update && sudo dnf install code",
                    "pacman": "yay -S visual-studio-code-bin",
                    "zypper": "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc && sudo sh -c 'echo -e \"[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ntype=rpm-md\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/zypp/repos.d/vscode.repo' && sudo zypper refresh && sudo zypper install code"
                },
                "manual": "Download from https://code.visualstudio.com/"
            },
            "ollama": {
                "windows": "Download from https://ollama.ai/download/windows",
                "macos": "Download from https://ollama.ai/download/mac",
                "linux": {
                    "universal": "curl -fsSL https://ollama.ai/install.sh | sh"
                },
                "manual": "Visit https://ollama.ai/download"
            }
        }
        
        software_lower = software.lower().strip()
        
        # Check if software exists in database
        if software_lower not in install_db:
            error = WorkspaceAIError(f"Software '{software}' not found in database")
            logging.error(f"Install command generation failed: {error}")
            raise error
        
        software_data = install_db[software_lower]
        
        # Handle manual method
        if method == "manual":
            manual_info = software_data.get("manual", f"Manual installation info not available for {software}")
            return f"Manual installation for {software}:\n{manual_info}"
        
        # Generate commands based on OS
        result = f"Installation commands for {software}:\n\n"
        
        if os_type == "windows":
            cmd = software_data.get("windows", "Not available for Windows")
            result += f"Windows:\n  {cmd}\n\n"
            result += f"Alternative: {software_data.get('manual', 'Download manually')}\n"
            
        elif os_type == "darwin":  # macOS
            cmd = software_data.get("macos", "Not available for macOS")
            result += f"macOS:\n  {cmd}\n\n"
            result += f"Alternative: {software_data.get('manual', 'Download manually')}\n"
            
        elif os_type == "linux":
            linux_cmds = software_data.get("linux", {})
            
            if isinstance(linux_cmds, dict):
                if "universal" in linux_cmds:
                    result += f"Linux (Universal):\n  {linux_cmds['universal']}\n\n"
                else:
                    # Detect package manager if method is auto
                    if method == "auto":
                        try:
                            pkg_manager = detect_linux_package_manager_with_exceptions()
                            if pkg_manager and pkg_manager in linux_cmds:
                                result += f"Linux ({pkg_manager}):\n  {linux_cmds[pkg_manager]}\n\n"
                            else:
                                result += "Linux - Available package managers:\n"
                                for pm, cmd in linux_cmds.items():
                                    result += f"  {pm}: {cmd}\n"
                                result += "\n"
                        except Exception as e:
                            # Fallback to showing all available package managers
                            logging.warning(f"Package manager detection failed: {e}")
                            result += "Linux - Available package managers:\n"
                            for pm, cmd in linux_cmds.items():
                                result += f"  {pm}: {cmd}\n"
                            result += "\n"
                    else:
                        # Specific package manager requested
                        if method in linux_cmds:
                            result += f"Linux ({method}):\n  {linux_cmds[method]}\n\n"
                        else:
                            error = WorkspaceAIError(f"Package manager '{method}' not supported for {software}")
                            logging.error(f"Install command generation failed: {error}")
                            raise error
            else:
                result += f"Linux:\n  {linux_cmds}\n\n"
                
            result += f"Alternative: {software_data.get('manual', 'Download manually')}\n"
        
        else:
            error = WorkspaceAIError(f"Unsupported operating system: {os_type}")
            logging.error(f"Install command generation failed: {error}")
            raise error
        
        return result
        
    except Exception as e:
        # Handle unexpected errors (but not our custom exceptions)
        if isinstance(e, (WorkspaceAIError, WorkspaceAIError)):
            raise  # Re-raise our custom exceptions
            
        converted_error = handle_exception("install_command_generation", e)
        logging.error(f"Install command generation failed: {converted_error}")
        raise converted_error
