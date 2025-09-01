"""
Utility functions for WorkspaceAI
"""

import os
import sys
import time
import platform
from tqdm import tqdm
from .config import CONSTANTS

def detect_linux_package_manager():
    """Detect the available package manager on Linux systems"""
    managers = {
        'apt': ['apt', 'apt-get'],
        'dnf': ['dnf'],
        'yum': ['yum'],
        'pacman': ['pacman'],
        'zypper': ['zypper'],
        'emerge': ['emerge'],
        'apk': ['apk']
    }
    
    for manager, commands in managers.items():
        for cmd in commands:
            if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
                return manager
    return None

def show_progress(description, duration=None):
    """Show progress bar for operations"""
    if duration is None:
        duration = CONSTANTS['PROGRESS_DURATION']
    
    print(f"\n{description}")
    for _ in tqdm(range(int(duration * 10)), desc="Progress", ncols=70):
        time.sleep(0.1)
    print()

def is_safe_filename(filename):
    """Check if filename is safe (no path traversal)"""
    if not filename:
        return False
    
    # Check for path traversal attempts
    if '..' in filename or filename.startswith('/') or ':' in filename:
        return False
    
    # Check for reserved names on Windows
    if platform.system() == 'Windows':
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
        if filename.upper().split('.')[0] in reserved_names:
            return False
    
    # Check length
    if len(filename) > CONSTANTS['MAX_FILENAME_LENGTH']:
        return False
    
    return True

def sanitize_filename(filename):
    """Sanitize filename for safety"""
    if not filename:
        return "file"
    
    # Remove path separators and dangerous characters
    filename = filename.replace('/', '_').replace('\\', '_').replace('..', '_')
    filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
    
    # Ensure it's not empty after sanitization
    if not filename:
        return "file"
    
    # Truncate if too long
    if len(filename) > CONSTANTS['MAX_FILENAME_LENGTH']:
        filename = filename[:CONSTANTS['MAX_FILENAME_LENGTH']]
    
    return filename

def get_unique_filename(directory, base_filename):
    """Generate a unique filename by adding numbers if needed"""
    if not os.path.exists(os.path.join(directory, base_filename)):
        return base_filename
    
    name, ext = os.path.splitext(base_filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not os.path.exists(os.path.join(directory, new_filename)):
            return new_filename
        counter += 1

def bytes_to_human_readable(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def validate_json_string(json_str):
    """Validate if string is valid JSON"""
    import json
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def generate_install_commands(software, method="auto"):
    """Generate installation commands for popular software (cross-platform)"""
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
    
    software_lower = software.lower()
    
    if software_lower not in install_db:
        return f"Software '{software}' not found in database. Available: {', '.join(install_db.keys())}"
    
    software_data = install_db[software_lower]
    
    # Handle manual method
    if method == "manual":
        return software_data.get("manual", f"Manual installation info not available for {software}")
    
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
                    pkg_manager = detect_linux_package_manager()
                    if pkg_manager and pkg_manager in linux_cmds:
                        result += f"Linux ({pkg_manager}):\n  {linux_cmds[pkg_manager]}\n\n"
                    else:
                        result += "Linux - Available package managers:\n"
                        for pm, cmd in linux_cmds.items():
                            result += f"  {pm}: {cmd}\n"
                        result += "\n"
                else:
                    # Specific package manager requested
                    if method in linux_cmds:
                        result += f"Linux ({method}):\n  {linux_cmds[method]}\n\n"
                    else:
                        result += f"Package manager '{method}' not supported for {software}\n"
                        result += f"Available: {', '.join(linux_cmds.keys())}\n"
        else:
            result += f"Linux:\n  {linux_cmds}\n\n"
            
        result += f"Alternative: {software_data.get('manual', 'Download manually')}\n"
    
    else:
        result += f"Unsupported OS: {os_type}\n"
        result += f"Manual installation: {software_data.get('manual', 'Check official website')}\n"
    
    return result
