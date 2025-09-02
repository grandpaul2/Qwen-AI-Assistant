"""
Universal Tool Handler for WorkspaceAI

This module provides dynamic tool execution capabilities that can handle
any tool call from any LLM model without predefined schemas.
"""

import json
import logging
import subprocess
import os
import importlib
import sys
import shutil
import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .progress import show_progress

logger = logging.getLogger(__name__)


class UniversalToolHandler:
    """
    Handles any tool call dynamically without predefined schemas.
    
    This allows the LLM to call any tool it wants, and we'll attempt
    to execute it using various strategies.
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize with workspace context"""
        if workspace_path is None:
            from .config import get_workspace_path
            self.workspace_path = get_workspace_path()
        else:
            self.workspace_path = workspace_path
        self.file_manager = None
        self._load_file_manager()
    
    def _load_file_manager(self):
        """Load file manager if available"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        try:
            # Try relative import first (preferred)
            from .file_manager import FileManager
            self.file_manager = FileManager()
            logger.info("File manager loaded successfully via relative import")
        except ImportError as e:
            logger.debug(f"Relative import failed: {e}")
            try:
                # Try absolute import with src package
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                from src.file_manager import FileManager
                self.file_manager = FileManager()
                logger.info("File manager loaded successfully via absolute import")
            except ImportError as e2:
                logger.debug(f"Absolute import failed: {e2}")
                try:
                    # Try direct import by adding src to path
                    if current_dir not in sys.path:
                        sys.path.insert(0, current_dir)
                    
                    import file_manager
                    self.file_manager = file_manager.FileManager()
                    logger.info("File manager loaded successfully via direct import")
                except Exception as e3:
                    logger.warning(f"All file manager import attempts failed: {e3}")
                    self.file_manager = None
    
    def handle_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle any tool call dynamically.
        
        Args:
            tool_call: The tool call from the LLM
            
        Returns:
            Result of the tool execution
        """
        function_info = tool_call.get("function", {})
        function_name = function_info.get("name", "")
        arguments = function_info.get("arguments", {})
        
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                return {"error": f"Invalid arguments JSON: {arguments}"}
        
        logger.info(f"Executing dynamic tool: {function_name} with args: {arguments}")
        
        # Show progress for tool execution
        with show_progress("", animated=True):
            # Try different execution strategies in order of sophistication
            strategies = [
                self._try_file_operations,
                self._try_python_operations,  # Try enhanced code execution first
                self._try_calculation,
                self._try_system_operations,  # System info, processes, etc.
                self._try_system_commands,    # Basic system commands last
                self._try_web_operations,
                self._try_generic_function,
            ]
            
            for strategy in strategies:
                try:
                    result = strategy(function_name, arguments)
                    if result is not None:
                        return {"success": True, "result": result}
                except Exception as e:
                    logger.debug(f"Strategy {strategy.__name__} failed: {e}")
                    continue
            
            # If all strategies fail, return helpful error
            return {
                "error": f"Unknown tool '{function_name}'. Available capabilities: file operations, system commands, calculations, web operations.",
                "suggestion": self._suggest_alternative(function_name, arguments)
            }
    
    def _try_file_operations(self, function_name: str, arguments: Dict) -> Optional[str]:
        """Try to execute as file operation"""
        if not self.file_manager:
            return None
        
        # Map common file operation names to our methods
        file_mappings = {
            # Standard names
            "file_operations": self._handle_file_operations,
            "read_file": "read_file",
            "write_file": "write_to_file", 
            "create_file": "create_file",
            "delete_file": "delete_file",
            "list_files": "list_files",
            "copy_file": "copy_file",
            "move_file": "move_file",
            "search_files": "search_files",
            
            # Alternative names models might use
            "read_text_file": "read_file",
            "write_text_file": "write_to_file",
            "save_file": "create_file",
            "remove_file": "delete_file",
            "delete": "delete_file",
            "ls": "list_files",
            "dir": "list_files",
            "cp": "copy_file",
            "mv": "move_file",
            "find": "search_files",
            "grep": "search_files",
        }
        
        if function_name == "file_operations":
            return self._handle_file_operations(arguments)
        
        method_name = file_mappings.get(function_name)
        if method_name and hasattr(self.file_manager, method_name):
            method = getattr(self.file_manager, method_name)
            return method(**arguments)
        
        return None
    
    def _handle_file_operations(self, arguments: Dict) -> str:
        """Handle the standard file_operations tool"""
        action = arguments.get("action", "").lower()
        path = arguments.get("path", arguments.get("file_name", ""))
        content = arguments.get("content", "")
        destination = arguments.get("destination", "")
        
        action_mappings = {
            "create": ("create_file", {"file_name": path, "content": content}),
            "read": ("read_file", {"file_name": path}),
            "write": ("write_to_file", {"file_name": path, "content": content}),
            "delete": ("delete_file", {"file_name": path}),
            "list": ("list_files", {"subdirectory": path}),
            "copy": ("copy_file", {"src_file": path, "dest_file": destination}),
            "move": ("move_file", {"src_file": path, "dest_file": destination}),
            "search": ("search_files", {"keyword": arguments.get("query", content)}),
        }
        
        if action in action_mappings:
            method_name, method_args = action_mappings[action]
            if hasattr(self.file_manager, method_name):
                method = getattr(self.file_manager, method_name)
                return method(**method_args)
        
        return f"Unknown file operation: {action}"
    
    def _try_system_commands(self, function_name: str, arguments: Dict) -> Optional[str]:
        """Try to execute as basic system command (fallback only)"""
        # Only handle generic system commands, not language-specific ones
        command_mappings = {
            "execute_command": arguments.get("command", ""),
            "run_command": arguments.get("command", ""),
            "system": arguments.get("command", ""),
            "execute": arguments.get("command", ""),
        }
        
        # Skip if it's a language-specific command (handled by _try_python_operations)
        if function_name in ["shell", "bash", "cmd", "powershell", "pwsh", "python", "javascript", "js", "node"]:
            return None
        
        command = command_mappings.get(function_name)
        if command:
            try:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    cwd=self.workspace_path
                )
                
                if result.returncode == 0:
                    return result.stdout if result.stdout else "Command executed successfully"
                else:
                    return f"Command error: {result.stderr}"
                    
            except subprocess.TimeoutExpired:
                return "Command timed out"
            except Exception as e:
                return f"Command execution error: {e}"
        
        return None
    
    def _try_python_operations(self, function_name: str, arguments: Dict) -> Optional[str]:
        """Try to execute as code operation (Python, JavaScript, shell) with enhanced cross-platform support"""
        # Enhanced to support multiple languages with smart command detection
        language_mappings = {
            # Python
            "code_interpreter": ("python", arguments.get("code", "")),
            "python": ("python", arguments.get("code", "")),
            "exec": ("python", arguments.get("code", "")),
            "eval": ("python", arguments.get("expression", arguments.get("code", ""))),
            
            # JavaScript
            "javascript": ("javascript", arguments.get("code", "")),
            "js": ("javascript", arguments.get("code", "")),
            "node": ("javascript", arguments.get("code", "")),
            
            # Shell/PowerShell
            "shell": ("shell", arguments.get("command", arguments.get("code", ""))),
            "bash": ("shell", arguments.get("command", arguments.get("code", ""))),
            "powershell": ("powershell", arguments.get("command", arguments.get("code", ""))),
            "pwsh": ("powershell", arguments.get("command", arguments.get("code", ""))),
            "cmd": ("cmd", arguments.get("command", arguments.get("code", ""))),
        }
        
        if function_name in language_mappings:
            language, code = language_mappings[function_name]
            return self._execute_code_enhanced(language, code)
        
        # Also check if arguments specify the language
        if "language" in arguments:
            language = arguments["language"].lower()
            code = arguments.get("code", "")
            return self._execute_code_enhanced(language, code)
        
        return None
    
    def _execute_code_enhanced(self, language: str, code: str) -> str:
        """Execute code in the specified language with enhanced cross-platform support"""
        if not code.strip():
            return "No code provided"
        
        try:
            if language == "python":
                return self._execute_python_enhanced(code)
            elif language == "javascript":
                return self._execute_javascript(code)
            elif language in ["shell", "bash"]:
                return self._execute_shell(code)
            elif language == "powershell":
                return self._execute_powershell(code)
            elif language == "cmd":
                return self._execute_cmd(code)
            else:
                return f"Unsupported language: {language}"
        except Exception as e:
            return f"{language.title()} execution error: {e}"

    def _execute_code(self, language: str, code: str) -> str:
        """Execute code in the specified language"""
        if not code.strip():
            return "No code provided"
        
        try:
            if language == "python":
                return self._execute_python(code)
            elif language == "javascript":
                return self._execute_javascript(code)
            elif language in ["shell", "bash"]:
                return self._execute_shell(code)
            elif language == "powershell":
                return self._execute_powershell(code)
            elif language == "cmd":
                return self._execute_cmd(code)
            else:
                return f"Unsupported language: {language}"
        except Exception as e:
            return f"{language.title()} execution error: {e}"
    
    def _execute_python_enhanced(self, code: str) -> str:
        """Execute Python code safely with enhanced cross-platform command handling"""
        try:
            # Smart command detection for system-related Python code
            if self._is_system_command_in_python(code):
                return self._handle_system_commands_in_python(code)
            
            # Create a safe execution environment with essential imports
            import math
            import random
            import datetime
            import os
            
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "range": range,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "reversed": reversed,
                    "enumerate": enumerate,
                    "zip": zip,
                    "bool": bool,
                    "type": type,
                    "isinstance": isinstance,
                    "hasattr": hasattr,
                    "getattr": getattr,
                    "any": any,
                    "all": all,
                    "__import__": __import__,  # Allow imports
                },
                # Safe imports
                "math": math,
                "random": random,
                "datetime": datetime,
                "os": os,
                "sys": __import__("sys"),
            }
            
            # Capture output
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(code, safe_globals)
            
            result = output.getvalue()
            return result if result else "Code executed successfully"
            
        except Exception as e:
            return f"Python execution error: {e}"

    def _is_system_command_in_python(self, code: str) -> bool:
        """Check if Python code contains system commands that need special handling"""
        system_indicators = [
            "subprocess.run",
            "os.system",
            "pip list",
            "python --version",
            "&&"
        ]
        return any(indicator in code for indicator in system_indicators)

    def _handle_system_commands_in_python(self, code: str) -> str:
        """Handle system commands within Python code with cross-platform support"""
        try:
            # Check for common problematic patterns and provide alternatives
            if "pip list" in code and ("head" in code or "Select-Object" in code):
                return self._get_pip_list_limited()
            
            if "python --version" in code:
                return self._get_python_version_info()
            
            # For other system commands, execute safely
            return self._execute_python_with_subprocess_fix(code)
            
        except Exception as e:
            return f"System command handling error: {e}"

    def _get_pip_list_limited(self) -> str:
        """Get pip list with limited output using Python (cross-platform)"""
        try:
            import subprocess
            import sys
            
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                # Take first 10 lines (header + 8 packages)
                limited_output = '\n'.join(lines[:10])
                return limited_output
            else:
                return f"Pip list error: {result.stderr}"
                
        except Exception as e:
            return f"Pip list execution error: {e}"

    def _get_python_version_info(self) -> str:
        """Get Python version info reliably (cross-platform)"""
        try:
            import sys
            version_info = f"Python {sys.version}"
            
            # Also get pip list
            pip_output = self._get_pip_list_limited()
            return version_info + "\n" + pip_output
            
        except Exception as e:
            return f"Version info error: {e}"

    def _execute_python_with_subprocess_fix(self, code: str) -> str:
        """Execute Python code with subprocess fixes for cross-platform compatibility"""
        try:
            # Replace common Unix commands with cross-platform equivalents
            fixed_code = self._fix_cross_platform_commands(code)
            
            # Execute the fixed code
            import io
            import contextlib
            import math
            import random
            import datetime
            import os
            import sys
            import subprocess
            
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "range": range,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "reversed": reversed,
                    "enumerate": enumerate,
                    "zip": zip,
                    "bool": bool,
                    "type": type,
                    "isinstance": isinstance,
                    "hasattr": hasattr,
                    "getattr": getattr,
                    "any": any,
                    "all": all,
                    "__import__": __import__,
                },
                "math": math,
                "random": random,
                "datetime": datetime,
                "os": os,
                "sys": sys,
                "subprocess": subprocess,
            }
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(fixed_code, safe_globals)
            
            result = output.getvalue()
            return result if result else "Code executed successfully"
            
        except Exception as e:
            return f"Enhanced Python execution error: {e}"

    def _fix_cross_platform_commands(self, code: str) -> str:
        """Fix cross-platform command issues in Python code"""
        import platform
        
        if platform.system() == "Windows":
            # Fix common Unix to Windows command translations
            replacements = {
                "head -10": "Select-Object -First 10",
                "head -5": "Select-Object -First 5", 
                "tail -10": "Select-Object -Last 10",
                "tail -5": "Select-Object -Last 5",
                "| head -10": "[:10]",  # For Python list slicing
                "| head -5": "[:5]",
            }
            
            for unix_cmd, windows_cmd in replacements.items():
                if unix_cmd in code:
                    # If it's in a subprocess call, use Python slicing instead
                    if "subprocess" in code and "head" in unix_cmd:
                        code = code.replace(f"| {unix_cmd}", windows_cmd)
                    else:
                        code = code.replace(unix_cmd, windows_cmd)
        
        return code

    def _execute_python(self, code: str) -> str:
        """Execute Python code safely"""
        try:
            # Create a safe execution environment with essential imports
            import math
            import random
            import datetime
            
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "range": range,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "reversed": reversed,
                    "enumerate": enumerate,
                    "zip": zip,
                    "bool": bool,
                    "type": type,
                    "isinstance": isinstance,
                    "hasattr": hasattr,
                    "getattr": getattr,
                    "any": any,
                    "all": all,
                    "__import__": __import__,  # Allow imports
                },
                # Safe imports
                "math": math,
                "random": random,
                "datetime": datetime,
            }
            
            # Capture output
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(code, safe_globals)
            
            result = output.getvalue()
            return result if result else "Code executed successfully"
            
        except Exception as e:
            return f"Python execution error: {e}"
    
    def _execute_javascript(self, code: str) -> str:
        """Execute JavaScript code using Node.js"""
        try:
            result = subprocess.run(
                ["node", "-e", code],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.workspace_path
            )
            
            if result.returncode == 0:
                return result.stdout if result.stdout else "Code executed successfully"
            else:
                return f"JavaScript error: {result.stderr}"
                
        except FileNotFoundError:
            return "JavaScript execution requires Node.js to be installed"
        except subprocess.TimeoutExpired:
            return "JavaScript execution timed out"
        except Exception as e:
            return f"JavaScript execution error: {e}"
    
    def _execute_shell(self, command: str) -> str:
        """Execute shell command (bash/sh)"""
        try:
            # On Windows, try using Git Bash or WSL, otherwise use cmd
            if os.name == 'nt':  # Windows
                # Try Git Bash first
                git_bash = r"C:\Program Files\Git\bin\bash.exe"
                if os.path.exists(git_bash):
                    shell_cmd = [git_bash, "-c", command]
                else:
                    # Fall back to cmd with shell-like behavior
                    return self._execute_cmd(command)
            else:
                # Unix-like systems
                shell_cmd = ["bash", "-c", command] if shutil.which("bash") else ["sh", "-c", command]
            
            result = subprocess.run(
                shell_cmd,
                capture_output=True,
                text=True,
                timeout=10,  # Reduced timeout
                cwd=self.workspace_path
            )
            
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully"
            else:
                return f"Shell error: {result.stderr}"
            
        except FileNotFoundError:
            return "Shell execution requires bash, sh, or Git Bash to be available"
        except subprocess.TimeoutExpired:
            return "Shell command timed out"
        except Exception as e:
            return f"Shell execution error: {e}"
    
    def _execute_powershell(self, command: str) -> str:
        """Execute PowerShell command"""
        try:
            # Try pwsh first (PowerShell Core), then powershell (Windows PowerShell)
            ps_cmd = "pwsh" if shutil.which("pwsh") else "powershell"
            
            result = subprocess.run(
                [ps_cmd, "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=self.workspace_path
            )
            
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully"
            else:
                return f"PowerShell error: {result.stderr}"
            
        except FileNotFoundError:
            return "PowerShell execution requires PowerShell to be installed"
        except subprocess.TimeoutExpired:
            return "PowerShell command timed out"
        except Exception as e:
            return f"PowerShell execution error: {e}"
    
    def _execute_cmd(self, command: str) -> str:
        """Execute Windows CMD command"""
        try:
            result = subprocess.run(
                ["cmd", "/c", command],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=self.workspace_path
            )
            
            output = result.stdout + result.stderr if result.stderr else result.stdout
            return output if output else "Command executed successfully"
            
        except FileNotFoundError:
            return "CMD execution requires Windows Command Prompt"
        except subprocess.TimeoutExpired:
            return "CMD command timed out"
        except Exception as e:
            return f"CMD execution error: {e}"
    
    def _try_system_operations(self, function_name: str, arguments: Dict) -> Optional[str]:
        """Try to execute as system operation (info, processes, disk, network)"""
        system_mappings = {
            # System Information
            "system_info": self._get_system_info,
            "get_system_info": self._get_system_info,
            "sys_info": self._get_system_info,
            "os_info": self._get_system_info,
            
            # Process Management
            "list_processes": self._list_processes,
            "get_processes": self._list_processes,
            "ps": self._list_processes,
            "kill_process": self._kill_process,
            "process_info": self._get_process_info,
            
            # Disk and Memory
            "disk_usage": self._get_disk_usage,
            "memory_usage": self._get_memory_usage,
            "cpu_usage": self._get_cpu_usage,
            "system_resources": self._get_system_resources,
            
            # Network
            "network_info": self._get_network_info,
            "ping": self._ping_host,
            
            # Environment
            "env_vars": self._get_env_vars,
            "get_env": self._get_env_vars,
            "path_info": self._get_path_info,
        }
        
        method = system_mappings.get(function_name)
        if method:
            return method(arguments)
        
        return None
    
    def _get_system_info(self, arguments: Dict) -> str:
        """Get comprehensive system information"""
        try:
            import platform
            import psutil
            
            info = {
                "Platform": platform.platform(),
                "System": platform.system(),
                "Architecture": platform.architecture()[0],
                "Processor": platform.processor(),
                "Python Version": platform.python_version(),
                "Node": platform.node(),
                "Release": platform.release(),
                "Version": platform.version(),
                "Boot Time": str(datetime.datetime.fromtimestamp(psutil.boot_time())),
            }
            
            result = "🖥️  SYSTEM INFORMATION\n" + "="*40 + "\n"
            for key, value in info.items():
                result += f"{key}: {value}\n"
            
            return result
            
        except ImportError:
            # Fallback without psutil
            import platform
            info = {
                "Platform": platform.platform(),
                "System": platform.system(),
                "Architecture": platform.architecture()[0],
                "Python Version": platform.python_version(),
                "Node": platform.node(),
            }
            
            result = "🖥️  SYSTEM INFORMATION (Basic)\n" + "="*40 + "\n"
            for key, value in info.items():
                result += f"{key}: {value}\n"
            
            return result
        except Exception as e:
            return f"Error getting system info: {e}"
    
    def _list_processes(self, arguments: Dict) -> str:
        """List running processes"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Show top processes
            limit = arguments.get("limit", 10)
            result = f"📊 TOP {limit} PROCESSES (by CPU usage)\n" + "="*50 + "\n"
            result += f"{'PID':<8} {'NAME':<25} {'CPU%':<8} {'MEM%':<8}\n"
            result += "-"*50 + "\n"
            
            for proc in processes[:limit]:
                pid = proc['pid']
                name = (proc['name'] or 'Unknown')[:24]
                cpu = f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] else "0.0"
                mem = f"{proc['memory_percent']:.1f}" if proc['memory_percent'] else "0.0"
                result += f"{pid:<8} {name:<25} {cpu:<8} {mem:<8}\n"
            
            return result
            
        except ImportError:
            return "Process listing requires psutil library (pip install psutil)"
        except Exception as e:
            return f"Error listing processes: {e}"
    
    def _get_system_resources(self, arguments: Dict) -> str:
        """Get overall system resource usage"""
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            result = "📊 SYSTEM RESOURCES OVERVIEW\n" + "="*35 + "\n"
            result += f"🔥 CPU Usage: {cpu_percent:.1f}%\n"
            result += f"🧠 Memory Usage: {memory.percent:.1f}% ({memory.used / (1024**3):.1f}/{memory.total / (1024**3):.1f} GB)\n"
            result += f"💾 Disk Usage: {(disk.used / disk.total * 100):.1f}% ({disk.used / (1024**3):.1f}/{disk.total / (1024**3):.1f} GB)\n"
            
            return result
            
        except ImportError:
            return "System resources requires psutil library"
        except Exception as e:
            return f"Error getting system resources: {e}"
    
    def _get_env_vars(self, arguments: Dict) -> str:
        """Get environment variables"""
        var_name = arguments.get("name", arguments.get("var", ""))
        
        if var_name:
            # Get specific environment variable
            value = os.environ.get(var_name)
            if value:
                return f"Environment variable '{var_name}': {value}"
            else:
                return f"Environment variable '{var_name}' not found"
        else:
            # Get all environment variables
            result = "🌍 ENVIRONMENT VARIABLES\n" + "="*30 + "\n"
            
            # Show important variables first
            important_vars = ['PATH', 'HOME', 'USER', 'USERNAME', 'USERPROFILE', 'TEMP', 'TMP']
            for var in important_vars:
                if var in os.environ:
                    value = os.environ[var]
                    # Truncate very long values
                    if len(value) > 100:
                        value = value[:97] + "..."
                    result += f"{var}: {value}\n"
            
            # Count total variables
            total_vars = len(os.environ)
            result += f"\nTotal environment variables: {total_vars}\n"
            result += "Use 'name' parameter to get specific variable value"
            
            return result

    def _kill_process(self, arguments: Dict) -> str:
        """Kill a process by PID"""
        try:
            import psutil
            
            pid = arguments.get("pid")
            if not pid:
                return "PID required for kill_process"
            
            try:
                pid = int(pid)
                process = psutil.Process(pid)
                process_name = process.name()
                process.terminate()
                return f"Process {pid} ({process_name}) terminated successfully"
            except ValueError:
                return f"Invalid PID: {pid}"
            except psutil.NoSuchProcess:
                return f"No process found with PID: {pid}"
            except psutil.AccessDenied:
                return f"Access denied - cannot terminate process {pid}"
                
        except ImportError:
            return "Process management requires psutil library"
        except Exception as e:
            return f"Error killing process: {e}"
    
    def _get_process_info(self, arguments: Dict) -> str:
        """Get detailed information about a specific process"""
        try:
            import psutil
            
            pid = arguments.get("pid")
            if not pid:
                return "PID required for process_info"
            
            try:
                pid = int(pid)
                process = psutil.Process(pid)
                
                info = {
                    "PID": process.pid,
                    "Name": process.name(),
                    "Status": process.status(),
                    "CPU %": f"{process.cpu_percent():.2f}",
                    "Memory %": f"{process.memory_percent():.2f}",
                    "Created": str(datetime.datetime.fromtimestamp(process.create_time())),
                    "Executable": process.exe(),
                }
                
                result = f"📋 PROCESS {pid} DETAILS\n" + "="*30 + "\n"
                for key, value in info.items():
                    result += f"{key}: {value}\n"
                
                return result
                
            except ValueError:
                return f"Invalid PID: {pid}"
            except psutil.NoSuchProcess:
                return f"No process found with PID: {pid}"
            except psutil.AccessDenied:
                return f"Access denied for process {pid}"
                
        except ImportError:
            return "Process info requires psutil library"
        except Exception as e:
            return f"Error getting process info: {e}"
    
    def _get_disk_usage(self, arguments: Dict) -> str:
        """Get disk usage information"""
        try:
            import psutil
            
            path = arguments.get("path", "/" if os.name != 'nt' else "C:\\")
            usage = psutil.disk_usage(path)
            
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent = (usage.used / usage.total) * 100
            
            result = f"💾 DISK USAGE for {path}\n" + "="*30 + "\n"
            result += f"Total: {total_gb:.2f} GB\n"
            result += f"Used:  {used_gb:.2f} GB ({percent:.1f}%)\n"
            result += f"Free:  {free_gb:.2f} GB\n"
            
            return result
            
        except ImportError:
            return "Disk usage requires psutil library"
        except Exception as e:
            return f"Error getting disk usage: {e}"
    
    def _get_memory_usage(self, arguments: Dict) -> str:
        """Get memory usage information"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            result = "🧠 MEMORY USAGE\n" + "="*20 + "\n"
            result += f"Total RAM: {memory.total / (1024**3):.2f} GB\n"
            result += f"Available: {memory.available / (1024**3):.2f} GB\n"
            result += f"Used: {memory.used / (1024**3):.2f} GB ({memory.percent:.1f}%)\n"
            result += f"Swap Total: {swap.total / (1024**3):.2f} GB\n"
            result += f"Swap Used: {swap.used / (1024**3):.2f} GB ({swap.percent:.1f}%)\n"
            
            return result
            
        except ImportError:
            return "Memory usage requires psutil library"
        except Exception as e:
            return f"Error getting memory usage: {e}"
    
    def _get_cpu_usage(self, arguments: Dict) -> str:
        """Get CPU usage information"""
        try:
            import psutil
            import time
            
            # Get CPU usage over 1 second interval
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            result = "⚡ CPU USAGE\n" + "="*15 + "\n"
            result += f"Overall Usage: {cpu_percent:.1f}%\n"
            result += f"Physical Cores: {cpu_count}\n"
            result += f"Logical Cores: {cpu_count_logical}\n"
            
            # Per-core usage
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)
            result += "\nPer-Core Usage:\n"
            for i, percent in enumerate(per_cpu):
                result += f"  Core {i}: {percent:.1f}%\n"
            
            return result
            
        except ImportError:
            return "CPU usage requires psutil library"
        except Exception as e:
            return f"Error getting CPU usage: {e}"
    
    def _get_network_info(self, arguments: Dict) -> str:
        """Get network interface information"""
        try:
            import psutil
            
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            result = "🌐 NETWORK INTERFACES\n" + "="*25 + "\n"
            
            for interface, addresses in interfaces.items():
                if interface in stats:
                    stat = stats[interface]
                    result += f"\n📡 {interface}\n"
                    result += f"  Status: {'UP' if stat.isup else 'DOWN'}\n"
                    result += f"  Speed: {stat.speed} Mbps\n"
                    
                    for addr in addresses:
                        if hasattr(addr.family, 'name'):
                            if addr.family.name == 'AF_INET':  # IPv4
                                result += f"  IPv4: {addr.address}\n"
                            elif addr.family.name == 'AF_INET6':  # IPv6
                                result += f"  IPv6: {addr.address}\n"
            
            return result
            
        except ImportError:
            return "Network info requires psutil library"
        except Exception as e:
            return f"Error getting network info: {e}"
    
    def _ping_host(self, arguments: Dict) -> str:
        """Ping a host"""
        host = arguments.get("host", arguments.get("hostname", ""))
        if not host:
            return "Host required for ping"
        
        try:
            # Use system ping command
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ["ping", "-n", "4", host],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:  # Unix-like
                result = subprocess.run(
                    ["ping", "-c", "4", host],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode == 0:
                return f"🏓 Ping results for {host}:\n{result.stdout}"
            else:
                return f"Ping failed for {host}: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Ping timeout for {host}"
        except Exception as e:
            return f"Error pinging {host}: {e}"
    
    def _get_path_info(self, arguments: Dict) -> str:
        """Get PATH environment variable information"""
        path_env = os.environ.get('PATH', '')
        if not path_env:
            return "PATH environment variable not found"
        
        paths = path_env.split(os.pathsep)
        
        result = "🛤️  PATH INFORMATION\n" + "="*25 + "\n"
        result += f"Total PATH entries: {len(paths)}\n\n"
        
        for i, path in enumerate(paths, 1):
            # Check if path exists
            exists = "✅" if os.path.exists(path) else "❌"
            result += f"{i:2d}. {exists} {path}\n"
        
        return result

    def _try_web_operations(self, function_name: str, arguments: Dict) -> Optional[str]:
        """Try to execute as web operation"""
        web_mappings = {
            # Web Search
            "web_search": self._web_search,
            "search": self._web_search,
            "google": self._web_search,
            "bing": self._web_search,
            
            # HTTP Operations
            "http_get": self._http_get,
            "http_post": self._http_post,
            "fetch": self._http_get,
            "download": self._download_file,
            "curl": self._http_get,
            
            # Web Scraping
            "scrape": self._scrape_webpage,
            "extract_text": self._scrape_webpage,
            "get_webpage": self._scrape_webpage,
        }
        
        method = web_mappings.get(function_name)
        if method:
            return method(arguments)
        
        return None
    
    def _web_search(self, arguments: Dict) -> str:
        """Perform web search (simulated)"""
        query = arguments.get("query", arguments.get("q", ""))
        engine = arguments.get("engine", "google")
        
        if not query:
            return "Query required for web search"
        
        # Since we can't do real web search without API keys, return helpful info
        return f"""🔍 WEB SEARCH SIMULATION
Query: "{query}"
Engine: {engine}

Note: Real web search requires:
- Search engine API keys (Google, Bing, DuckDuckGo)
- Web scraping libraries (requests, beautifulsoup4)
- Implementation of search result parsing

For now, try using the 'fetch' or 'http_get' operations with specific URLs."""
    
    def _http_get(self, arguments: Dict) -> str:
        """Perform HTTP GET request with enhanced timeout handling"""
        url = arguments.get("url", "")
        headers = arguments.get("headers", {})
        timeout = arguments.get("timeout", 30)  # Default 30 seconds for better reliability
        
        if not url:
            return "URL required for HTTP GET request"
        
        try:
            import requests
            
            with show_progress("", animated=True):
                response = requests.get(url, headers=headers, timeout=timeout)
            
            result = f"🌐 HTTP GET: {url}\n"
            result += f"Status: {response.status_code}\n"
            result += f"Content Type: {response.headers.get('content-type', 'unknown')}\n"
            result += f"Content Length: {len(response.content)} bytes\n"
            result += f"Response Time: {timeout - (timeout if response.status_code == 200 else 0):.2f}s\n\n"
            
            # Show first 500 characters of response
            content = response.text[:500]
            if len(response.text) > 500:
                content += "..."
            
            result += f"Content Preview:\n{content}"
            
            return result
            
        except ImportError:
            return "HTTP operations require 'requests' library (pip install requests)"
        except Exception as e:
            # Handle specific request exceptions if requests is available
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return f"HTTP GET timeout after {timeout}s for URL: {url}"
            elif "connection" in error_msg.lower():
                return f"Connection error for URL: {url} (check network connectivity)"
            else:
                return f"HTTP GET error: {e}"
    
    def _http_post(self, arguments: Dict) -> str:
        """Perform HTTP POST request with enhanced timeout handling"""
        url = arguments.get("url", "")
        data = arguments.get("data", {})
        headers = arguments.get("headers", {})
        timeout = arguments.get("timeout", 30)  # Default 30 seconds for better reliability
        
        if not url:
            return "URL required for HTTP POST request"
        
        try:
            import requests
            
            with show_progress("", animated=True):
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            
            result = f"🌐 HTTP POST: {url}\n"
            result += f"Status: {response.status_code}\n"
            result += f"Content Type: {response.headers.get('content-type', 'unknown')}\n"
            result += f"Response Length: {len(response.content)} bytes\n\n"
            
            # Show response content
            content = response.text[:500]
            if len(response.text) > 500:
                content += "..."
            
            result += f"Response:\n{content}"
            
            return result
            
        except ImportError:
            return "HTTP operations require 'requests' library (pip install requests)"
        except Exception as e:
            # Handle specific request exceptions
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return f"HTTP POST timeout after {timeout}s for URL: {url}"
            elif "connection" in error_msg.lower():
                return f"Connection error for URL: {url} (check network connectivity)"
            else:
                return f"HTTP POST error: {e}"
    
    def _download_file(self, arguments: Dict) -> str:
        """Download a file from URL with enhanced timeout handling"""
        url = arguments.get("url", "")
        filename = arguments.get("filename", "")
        timeout = arguments.get("timeout", 60)  # Longer timeout for downloads
        
        if not url:
            return "URL required for download"
        
        if not filename:
            # Extract filename from URL
            filename = url.split("/")[-1]
            if not filename or "." not in filename:
                filename = "downloaded_file"
        
        try:
            import requests
            
            with show_progress("Downloading...", animated=True):
                response = requests.get(url, timeout=timeout, stream=True)
                response.raise_for_status()
            
            # Use file manager to save to secure workspace
            if self.file_manager:
                # Read content into memory first
                content = b""
                for chunk in response.iter_content(chunk_size=8192):
                    content += chunk
                
                # Save using file manager (note: file_manager expects text, so we need to handle binary)
                # For now, let's use the secure path resolution from file_manager
                secure_path = self.file_manager._resolve(filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(secure_path), exist_ok=True)
                
                with open(secure_path, 'wb') as f:
                    f.write(content)
                
                filepath = secure_path
            else:
                # Fallback: use workspace path directly (still secure)
                filepath = os.path.join(self.workspace_path, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            size_mb = file_size / (1024 * 1024)
            
            return f"📥 Downloaded: {filename}\nSize: {size_mb:.2f} MB\nSaved to: {filepath}"
            
        except ImportError:
            return "Download operations require 'requests' library (pip install requests)"
        except Exception as e:
            # Handle specific request exceptions
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return f"Download timeout after {timeout}s for URL: {url}"
            elif "connection" in error_msg.lower():
                return f"Connection error for URL: {url} (check network connectivity)"
            else:
                return f"Download error: {e}"
    
    def _scrape_webpage(self, arguments: Dict) -> str:
        """Scrape text content from a webpage with enhanced timeout handling"""
        url = arguments.get("url", "")
        selector = arguments.get("selector", "")  # CSS selector
        timeout = arguments.get("timeout", 30)  # Default 30 seconds for web scraping
        
        if not url:
            return "URL required for web scraping"
        
        try:
            import requests
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                # Fallback to basic text extraction without BeautifulSoup
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                
                # Basic text extraction from HTML
                content = response.text
                # Remove HTML tags with simple regex
                import re
                content = re.sub(r'<[^>]+>', ' ', content)
                content = re.sub(r'\s+', ' ', content).strip()
                
                if len(content) > 2000:
                    content = content[:2000] + "...\n[Content truncated]"
                
                return f"🕷️ WEBPAGE CONTENT (basic): {url}\n{'='*50}\n{content}"
            
            with show_progress("Scraping webpage...", animated=True):
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if selector:
                # Extract specific elements
                elements = soup.select(selector)
                if elements:
                    content = "\n".join([elem.get_text().strip() for elem in elements])
                else:
                    content = f"No elements found with selector: {selector}"
            else:
                # Extract all text content
                content = soup.get_text()
            
            # Clean up the text
            lines = content.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            content = '\n'.join(lines)
            
            # Limit output size
            if len(content) > 2000:
                content = content[:2000] + "...\n[Content truncated]"
            
            result = f"🕷️ WEBPAGE CONTENT: {url}\n"
            result += "="*50 + "\n"
            result += content
            
            return result
            
        except ImportError as e:
            missing = []
            if "requests" in str(e):
                missing.append("requests")
            return f"Web scraping requires: {', '.join(missing)} (pip install {' '.join(missing)})\nNote: beautifulsoup4 is optional for enhanced parsing"
        except Exception as e:
            # Handle specific request exceptions
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return f"Web scraping timeout after {timeout}s for URL: {url}"
            elif "connection" in error_msg.lower():
                return f"Connection error for URL: {url} (check network connectivity)"
            else:
                return f"Web scraping error: {e}"
    
    def _try_calculation(self, function_name: str, arguments: Dict) -> Optional[str]:
        """Try to execute as calculation"""
        if function_name in ["calculator", "calc", "math", "calculate"]:
            expression = arguments.get("expression", arguments.get("expr", ""))
            try:
                # Safe math evaluation
                import ast
                import operator
                
                ops = {
                    ast.Add: operator.add,
                    ast.Sub: operator.sub,
                    ast.Mult: operator.mul,
                    ast.Div: operator.truediv,
                    ast.Pow: operator.pow,
                    ast.USub: operator.neg,
                }
                
                def eval_expr(node):
                    if isinstance(node, ast.Num):
                        return node.n
                    elif isinstance(node, ast.BinOp):
                        return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                    elif isinstance(node, ast.UnaryOp):
                        return ops[type(node.op)](eval_expr(node.operand))
                    else:
                        raise TypeError(node)
                
                result = eval_expr(ast.parse(expression, mode='eval').body)
                return str(result)
                
            except Exception as e:
                return f"Calculation error: {e}"
        
        return None
    
    def _try_generic_function(self, function_name: str, arguments: Dict) -> Optional[str]:
        """Try to execute as generic function"""
        # Check if it's a method on file_manager
        if self.file_manager and hasattr(self.file_manager, function_name):
            method = getattr(self.file_manager, function_name)
            try:
                return method(**arguments)
            except Exception as e:
                return f"Function execution error: {e}"
        
        # Check if it's a utility function
        try:
            from utils import generate_install_commands
            if function_name == "generate_install_commands":
                return generate_install_commands(
                    arguments.get("software", ""),
                    arguments.get("method", "auto")
                )
        except ImportError:
            pass
        
        return None
    
    def _suggest_alternative(self, function_name: str, arguments: Dict) -> str:
        """Suggest alternative function names"""
        suggestions = []
        
        # File operation suggestions
        if any(word in function_name.lower() for word in ["file", "read", "write", "create", "delete"]):
            suggestions.append("Try: file_operations with action parameter")
        
        # Command suggestions  
        if any(word in function_name.lower() for word in ["command", "run", "exec", "shell"]):
            suggestions.append("Try: execute_command with command parameter")
        
        # Math suggestions
        if any(word in function_name.lower() for word in ["calc", "math", "compute"]):
            suggestions.append("Try: calculator with expression parameter")
        
        return "; ".join(suggestions) if suggestions else "No suggestions available"


# Global instance
universal_handler = UniversalToolHandler()


def handle_any_tool_call(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public interface for handling any tool call.
    
    This function can handle any tool call from any LLM model.
    """
    return universal_handler.handle_tool_call(tool_call)
