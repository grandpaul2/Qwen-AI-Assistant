"""
Software installer module for WorkspaceAI

This module provides cross-platform software installation command generation,
supporting various package managers and installation methods.
"""

import platform
import subprocess
import os
from typing import Dict, Any, Optional

from .utils import detect_linux_package_manager


def generate_install_commands(software: str, method: str = "auto") -> str:
    """
    Generate installation commands for popular software (cross-platform)
    
    Args:
        software: Name of the software to install
        method: Installation method ('auto', 'package_manager', 'official', 'manual')
    
    Returns:
        Formatted installation instructions
    """
    software_lower = software.lower().strip()
    method_lower = method.lower().strip()
    current_os = platform.system()
    
    # Comprehensive software database
    software_db = {
        "python": {
            "description": "Python programming language",
            "windows": {
                "winget": "winget install Python.Python.3.12",
                "direct": "Download from: https://python.org/downloads/\n- Choose 'Add to PATH' during installation",
                "chocolatey": "choco install python3"
            },
            "darwin": {  # macOS
                "brew": "brew install python@3.12",
                "direct": "Download from: https://python.org/downloads/",
                "pyenv": "pyenv install 3.12.0"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install python3 python3-pip python3-venv",
                "dnf": "sudo dnf install python3 python3-pip",
                "yum": "sudo yum install python3 python3-pip", 
                "pacman": "sudo pacman -S python python-pip",
                "zypper": "sudo zypper install python3 python3-pip",
                "snap": "sudo snap install python3 --classic",
                "direct": "Build from source: https://python.org/downloads/source/"
            }
        },
        "nodejs": {
            "description": "Node.js JavaScript runtime",
            "windows": {
                "winget": "winget install OpenJS.NodeJS",
                "direct": "Download from: https://nodejs.org/en/download/",
                "chocolatey": "choco install nodejs"
            },
            "darwin": {
                "brew": "brew install node",
                "direct": "Download from: https://nodejs.org/en/download/",
                "nvm": "nvm install node"
            },
            "linux": {
                "apt": "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs",
                "dnf": "sudo dnf install nodejs npm",
                "yum": "sudo yum install nodejs npm",
                "pacman": "sudo pacman -S nodejs npm",
                "zypper": "sudo zypper install nodejs npm",
                "snap": "sudo snap install node --classic",
                "direct": "Download from: https://nodejs.org/en/download/"
            }
        },
        "git": {
            "description": "Version control system",
            "windows": {
                "winget": "winget install Git.Git",
                "direct": "Download from: https://git-scm.com/downloads",
                "chocolatey": "choco install git"
            },
            "darwin": {
                "brew": "brew install git",
                "direct": "Download from: https://git-scm.com/downloads",
                "xcode": "xcode-select --install"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install git",
                "dnf": "sudo dnf install git",
                "yum": "sudo yum install git",
                "pacman": "sudo pacman -S git",
                "zypper": "sudo zypper install git",
                "snap": "sudo snap install git --classic",
                "direct": "Build from source: https://git-scm.com/downloads"
            }
        },
        "docker": {
            "description": "Containerization platform",
            "windows": {
                "winget": "winget install Docker.DockerDesktop",
                "direct": "Download from: https://docker.com/get-started",
                "chocolatey": "choco install docker-desktop"
            },
            "darwin": {
                "brew": "brew install --cask docker",
                "direct": "Download from: https://docker.com/get-started"
            },
            "linux": {
                "apt": "curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER",
                "dnf": "sudo dnf install docker docker-compose && sudo systemctl enable docker && sudo usermod -aG docker $USER",
                "yum": "sudo yum install docker docker-compose && sudo systemctl enable docker && sudo usermod -aG docker $USER",
                "pacman": "sudo pacman -S docker docker-compose && sudo systemctl enable docker && sudo usermod -aG docker $USER",
                "zypper": "sudo zypper install docker docker-compose && sudo systemctl enable docker && sudo usermod -aG docker $USER",
                "snap": "sudo snap install docker",
                "direct": "curl -fsSL https://get.docker.com | sh"
            }
        },
        "vscode": {
            "description": "Visual Studio Code editor",
            "windows": {
                "winget": "winget install Microsoft.VisualStudioCode",
                "direct": "Download from: https://code.visualstudio.com/download",
                "chocolatey": "choco install vscode"
            },
            "darwin": {
                "brew": "brew install --cask visual-studio-code",
                "direct": "Download from: https://code.visualstudio.com/download"
            },
            "linux": {
                "apt": "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg && sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/ && sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list' && sudo apt update && sudo apt install code",
                "dnf": "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc && sudo sh -c 'echo -e \"[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/yum.repos.d/vscode.repo' && sudo dnf check-update && sudo dnf install code",
                "yum": "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc && sudo sh -c 'echo -e \"[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/yum.repos.d/vscode.repo' && sudo yum check-update && sudo yum install code",
                "pacman": "yay -S visual-studio-code-bin",
                "zypper": "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc && sudo sh -c 'echo -e \"[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ntype=rpm-md\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/zypp/repos.d/vscode.repo' && sudo zypper refresh && sudo zypper install code",
                "snap": "sudo snap install code --classic",
                "direct": "Download .deb/.rpm from: https://code.visualstudio.com/download"
            }
        },
        "ollama": {
            "description": "Local LLM inference server",
            "windows": {
                "direct": "Download from: https://ollama.ai/download/windows"
            },
            "darwin": {
                "brew": "brew install ollama",
                "direct": "Download from: https://ollama.ai/download/mac"
            },
            "linux": {
                "universal": "curl -fsSL https://ollama.ai/install.sh | sh",
                "direct": "curl -fsSL https://ollama.ai/install.sh | sh"
            }
        },
        "chrome": {
            "description": "Google Chrome web browser",
            "windows": {
                "winget": "winget install Google.Chrome",
                "direct": "Download from: https://chrome.google.com/",
                "chocolatey": "choco install googlechrome"
            },
            "darwin": {
                "brew": "brew install --cask google-chrome",
                "direct": "Download from: https://chrome.google.com/"
            },
            "linux": {
                "apt": "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - && sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list' && sudo apt update && sudo apt install google-chrome-stable",
                "dnf": "sudo dnf install fedora-workstation-repositories && sudo dnf config-manager --set-enabled google-chrome && sudo dnf install google-chrome-stable",
                "yum": "sudo yum install google-chrome-stable",
                "direct": "Download .deb/.rpm from: https://chrome.google.com/"
            }
        },
        "firefox": {
            "description": "Mozilla Firefox web browser", 
            "windows": {
                "winget": "winget install Mozilla.Firefox",
                "direct": "Download from: https://firefox.com/",
                "chocolatey": "choco install firefox"
            },
            "darwin": {
                "brew": "brew install --cask firefox",
                "direct": "Download from: https://firefox.com/"
            },
            "linux": {
                "apt": "sudo apt update && sudo apt install firefox",
                "dnf": "sudo dnf install firefox",
                "yum": "sudo yum install firefox",
                "pacman": "sudo pacman -S firefox",
                "zypper": "sudo zypper install firefox",
                "snap": "sudo snap install firefox",
                "direct": "Usually pre-installed on most distros"
            }
        },
        "vim": {
            "description": "Vim text editor",
            "windows": {
                "winget": "winget install vim.vim",
                "chocolatey": "choco install vim",
                "direct": "Download from: https://vim.org/download.php"
            },
            "darwin": {
                "brew": "brew install vim",
                "direct": "Usually pre-installed"
            },
            "linux": {
                "apt": "sudo apt install vim",
                "dnf": "sudo dnf install vim",
                "yum": "sudo yum install vim",
                "pacman": "sudo pacman -S vim",
                "zypper": "sudo zypper install vim",
                "direct": "Usually pre-installed"
            }
        },
        "curl": {
            "description": "Command-line tool for transferring data",
            "windows": {
                "winget": "winget install cURL.cURL",
                "chocolatey": "choco install curl",
                "direct": "Usually included in Windows 10+"
            },
            "darwin": {
                "brew": "brew install curl",
                "direct": "Usually pre-installed"
            },
            "linux": {
                "apt": "sudo apt install curl",
                "dnf": "sudo dnf install curl",
                "yum": "sudo yum install curl",
                "pacman": "sudo pacman -S curl",
                "zypper": "sudo zypper install curl",
                "direct": "Usually pre-installed"
            }
        }
    }
    
    # Find software (flexible matching)
    found_software = None
    for key in software_db:
        if software_lower in key or key in software_lower:
            found_software = key
            break
    
    if not found_software:
        # Generate suggestions for similar software
        suggestions = [key for key in software_db.keys() if any(word in key for word in software_lower.split())]
        suggestion_text = f"\\nDid you mean: {', '.join(suggestions[:5])}" if suggestions else ""
        return f"Software '{software}' not found in database.{suggestion_text}\\n\\nAvailable software: {', '.join(list(software_db.keys())[:10])}..."
    
    sw = software_db[found_software]
    os_key = current_os.lower()
    
    # Map macOS system name
    if os_key == "darwin":
        os_display = "macOS"
    else:
        os_display = current_os
    
    # Get platform-specific commands
    if os_key not in sw:
        return f"Software '{found_software}' is not supported on {current_os}"
    
    platform_commands = sw[os_key]
    result = f"\\n📦 {sw['description']} ({found_software}) - {os_display}\\n" + "="*60 + "\\n"
    
    if method_lower == "auto":
        # Determine best method automatically based on platform
        if current_os == "Windows":
            if "winget" in platform_commands:
                result += f"🚀 RECOMMENDED (Windows Package Manager):\\n{platform_commands['winget']}\\n\\n"
            if "chocolatey" in platform_commands:
                result += f"🍫 Chocolatey:\\n{platform_commands['chocolatey']}\\n\\n"
            if "direct" in platform_commands:
                result += f"🌐 Direct Download:\\n{platform_commands['direct']}\\n\\n"
        
        elif current_os == "Darwin":  # macOS
            if "brew" in platform_commands:
                result += f"🚀 RECOMMENDED (Homebrew):\\n{platform_commands['brew']}\\n\\n"
            if "direct" in platform_commands:
                result += f"🌐 Direct Download:\\n{platform_commands['direct']}\\n\\n"
        
        elif current_os == "Linux":
            # Handle universal installer first
            if "universal" in platform_commands:
                result += f"🚀 RECOMMENDED (Universal):\\n{platform_commands['universal']}\\n\\n"
            else:
                # Detect package manager and recommend it
                detected_pm = detect_linux_package_manager()
                if detected_pm and detected_pm in platform_commands:
                    result += f"🚀 RECOMMENDED ({detected_pm.upper()}):\\n{platform_commands[detected_pm]}\\n\\n"
                
                # Show other available methods
                for pm_name, command in platform_commands.items():
                    if pm_name != detected_pm and pm_name not in ["direct", "snap"]:
                        result += f"📋 {pm_name.upper()}:\\n{command}\\n\\n"
                
                # Show snap and direct options
                if "snap" in platform_commands:
                    result += f"📦 Snap:\\n{platform_commands['snap']}\\n\\n"
                if "direct" in platform_commands:
                    result += f"🌐 Alternative:\\n{platform_commands['direct']}\\n\\n"
    
    elif method_lower in platform_commands:
        result += f"📋 {method_lower.upper()} Install:\\n{platform_commands[method_lower]}\\n"
    else:
        available = list(platform_commands.keys())
        result += f"Method '{method}' not available for {current_os}.\\nAvailable methods: {', '.join(available)}\\n"
        # Show default method
        if current_os == "Windows" and "winget" in platform_commands:
            result += f"🚀 Default method:\\n{platform_commands['winget']}"
        elif current_os == "Darwin" and "brew" in platform_commands:
            result += f"🚀 Default method:\\n{platform_commands['brew']}"
        elif current_os == "Linux":
            detected_pm = detect_linux_package_manager()
            if detected_pm and detected_pm in platform_commands:
                result += f"🚀 Default method:\\n{platform_commands[detected_pm]}"
    
    # Add platform-specific tips
    if current_os == "Windows":
        result += "\\n💡 TIP: Run commands in PowerShell as Administrator if needed"
    elif current_os == "Darwin":
        result += "\\n💡 TIP: Install Homebrew first: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    else:
        result += "\\n💡 TIP: You may need to restart your terminal after installation"
    
    return result


def check_software_installed(software: str) -> Dict[str, Any]:
    """
    Check if software is installed on the system
    
    Args:
        software: Name of the software to check
    
    Returns:
        Dictionary with installation status and version info
    """
    software_lower = software.lower()
    
    # Common command patterns for checking software
    check_commands = {
        "python": ["python3", "--version"],
        "python3": ["python3", "--version"],
        "nodejs": ["node", "--version"],
        "node": ["node", "--version"],
        "git": ["git", "--version"],
        "docker": ["docker", "--version"],
        "ollama": ["ollama", "--version"],
        "curl": ["curl", "--version"],
        "vim": ["vim", "--version"],
        "code": ["code", "--version"],
        "vscode": ["code", "--version"]
    }
    
    result = {
        "software": software,
        "installed": False,
        "version": None,
        "path": None,
        "error": None
    }
    
    if software_lower not in check_commands:
        result["error"] = f"Don't know how to check for {software}"
        return result
    
    try:
        command = check_commands[software_lower]
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if process.returncode == 0:
            result["installed"] = True
            result["version"] = process.stdout.strip()
            
            # Try to get the path
            try:
                which_cmd = "where" if platform.system() == "Windows" else "which"
                path_process = subprocess.run(
                    [which_cmd, command[0]],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if path_process.returncode == 0:
                    result["path"] = path_process.stdout.strip()
            except:
                pass  # Path detection is optional
        else:
            result["error"] = process.stderr.strip()
            
    except subprocess.TimeoutExpired:
        result["error"] = "Command timed out"
    except FileNotFoundError:
        result["error"] = "Command not found"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information for installation guidance
    
    Returns:
        Dictionary with system details
    """
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "package_manager": None,
        "shell": os.environ.get("SHELL", "unknown"),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
    }
    
    # Detect package manager on Linux
    if info["os"] == "Linux":
        info["package_manager"] = detect_linux_package_manager()
        
        # Try to get Linux distribution info
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        info["distribution"] = line.split("=", 1)[1].strip().strip('"')
                        break
        except:
            info["distribution"] = "Unknown Linux"
    
    # Check for common package managers/tools
    tools_to_check = ["git", "curl", "docker", "node", "python3"]
    info["available_tools"] = {}
    
    for tool in tools_to_check:
        check_result = check_software_installed(tool)
        info["available_tools"][tool] = check_result["installed"]
    
    return info
