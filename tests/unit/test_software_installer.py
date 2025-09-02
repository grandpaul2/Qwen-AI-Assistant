"""
Unit tests for src/software_installer.py

Tests software installation command generation and checking functionality
"""

import pytest
import platform
import subprocess
from unittest.mock import patch, MagicMock, mock_open

# Import required modules
from src.software_installer import (
    generate_install_commands_with_exceptions,
    check_software_installed_with_exceptions,
    get_system_info_with_exceptions
)
from src.utils import detect_linux_package_manager, generate_install_commands
from src.exceptions import WorkspaceAIError, UnsupportedPlatformError


class TestWrapperExceptionHandling:
    """Test exception handling in wrapper functions"""
    
    @patch('src.software_installer.generate_install_commands_with_exceptions')
    def test_generate_install_commands_wrapper_exception(self, mock_generate):
        """Test wrapper function handles exceptions from main function"""
        from src.software_installer import generate_install_commands
        
        # Make the main function raise an exception
        mock_generate.side_effect = Exception("Test error")
        
        result = generate_install_commands("python", "auto")
        
        assert "Error generating install commands for 'python'" in result
        assert "Please check manually" in result


class TestGenerateInstallCommands:
    """Test install command generation functionality"""
    
    def test_method_none_defaults_to_auto(self):
        """Test that method=None defaults to auto"""
        with patch('platform.system', return_value='Windows'):
            result = generate_install_commands_with_exceptions("python", None)
            
            assert isinstance(result, str)
            assert "python" in result.lower()
            assert "Windows" in result
    
    def test_python_windows_auto(self):
        """Test Python installation commands for Windows with auto method"""
        with patch('platform.system', return_value='Windows'):
            result = generate_install_commands_with_exceptions("python", "auto")
            
            assert isinstance(result, str)
            assert "python" in result.lower()
            assert "winget" in result
            assert "Windows" in result
    
    def test_python_macos_auto(self):
        """Test Python installation commands for macOS with auto method"""
        with patch('platform.system', return_value='Darwin'):
            result = generate_install_commands_with_exceptions("python", "auto")
            
            assert isinstance(result, str)
            assert "python" in result.lower()
            assert "brew" in result
            assert "macOS" in result
    
    @patch('src.software_installer.detect_linux_package_manager')
    def test_python_linux_auto(self, mock_detect_pm):
        """Test Python installation commands for Linux with auto method"""
        mock_detect_pm.return_value = "apt"
        
        with patch('platform.system', return_value='Linux'):
            result = generate_install_commands_with_exceptions("python", "auto")
            
            assert isinstance(result, str)
            assert "python" in result.lower()
            assert "apt" in result
            assert "Linux" in result
    
    def test_nodejs_specific_method(self):
        """Test NodeJS installation with specific method"""
        with patch('platform.system', return_value='Windows'):
            result = generate_install_commands_with_exceptions("nodejs", "winget")
            
            assert isinstance(result, str)
            assert "nodejs" in result.lower() or "node" in result.lower()
            assert "winget" in result
    
    def test_vscode_installation(self):
        """Test VS Code installation commands"""
        with patch('platform.system', return_value='Windows'):
            result = generate_install_commands_with_exceptions("vscode", "auto")
            
            assert isinstance(result, str)
            assert "visual studio code" in result.lower() or "code" in result.lower()
    
    def test_ollama_installation(self):
        """Test Ollama installation commands"""
        with patch('platform.system', return_value='Windows'):
            result = generate_install_commands_with_exceptions("ollama", "auto")
            
            assert isinstance(result, str)
            assert "ollama" in result.lower()
    
    def test_invalid_software_name(self):
        """Test handling of invalid software names"""
        with pytest.raises(WorkspaceAIError) as exc_info:
            generate_install_commands_with_exceptions("", "auto")
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_software_name_too_long(self):
        """Test handling of overly long software names"""
        long_name = "a" * 150
        
        with pytest.raises(WorkspaceAIError) as exc_info:
            generate_install_commands_with_exceptions(long_name, "auto")
        
        assert "too long" in str(exc_info.value)
    
    def test_invalid_method(self):
        """Test handling of invalid installation methods"""
        with pytest.raises(WorkspaceAIError) as exc_info:
            generate_install_commands_with_exceptions("python", "invalid_method")
        
        assert "Invalid method" in str(exc_info.value)
    
    def test_none_inputs(self):
        """Test handling of None inputs"""
        with pytest.raises(WorkspaceAIError):
            generate_install_commands_with_exceptions(None, "auto")  # type: ignore
    
    def test_non_string_method(self):
        """Test handling of non-string method parameter"""
        with pytest.raises(WorkspaceAIError) as exc_info:
            generate_install_commands_with_exceptions("python", 123)  # type: ignore
        
        assert "Method must be a string" in str(exc_info.value)
    
    def test_unknown_software(self):
        """Test handling of unknown software"""
        with patch('platform.system', return_value='Windows'):
            result = generate_install_commands_with_exceptions("unknown_software_xyz", "auto")
            
            assert "not found in database" in result
            assert "Available software:" in result
    
    @patch('platform.system')
    def test_unsupported_platform(self, mock_system):
        """Test handling of unsupported platforms"""
        mock_system.return_value = ""
        
        with pytest.raises(UnsupportedPlatformError):
            generate_install_commands_with_exceptions("python", "auto")
    
    def test_case_insensitive_software_matching(self):
        """Test case-insensitive software name matching"""
        with patch('platform.system', return_value='Windows'):
            result1 = generate_install_commands_with_exceptions("PYTHON", "auto")
            result2 = generate_install_commands_with_exceptions("python", "auto")
            result3 = generate_install_commands_with_exceptions("Python", "auto")
            
            # All should succeed and contain similar content
            assert all("python" in r.lower() for r in [result1, result2, result3])
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in inputs"""
        with patch('platform.system', return_value='Windows'):
            result = generate_install_commands_with_exceptions("  python  ", "  auto  ")
            
            assert isinstance(result, str)
            assert "python" in result.lower()


class TestCheckSoftwareInstalled:
    """Test software installation checking functionality"""
    
    @patch('subprocess.run')
    def test_software_installed_success(self, mock_run):
        """Test checking installed software (success case)"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Python 3.9.0"
        mock_run.return_value = mock_process
        
        result = check_software_installed_with_exceptions("python")
        
        assert result["installed"] is True
        assert result["version"] == "Python 3.9.0"
        assert result["software"] == "python"
    
    @patch('subprocess.run')
    def test_software_not_installed(self, mock_run):
        """Test checking non-installed software"""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "command not found"
        mock_run.return_value = mock_process
        
        result = check_software_installed_with_exceptions("python")
        
        assert result["installed"] is False
        assert result["error"] is not None
    
    @patch('subprocess.run')
    def test_software_check_timeout(self, mock_run):
        """Test handling of subprocess timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("python3", 10)
        
        result = check_software_installed_with_exceptions("python")
        
        assert result["installed"] is False
        assert "timed out" in result["error"]
    
    @patch('subprocess.run')
    def test_software_check_file_not_found(self, mock_run):
        """Test handling of command not found"""
        mock_run.side_effect = FileNotFoundError()
        
        result = check_software_installed_with_exceptions("python")
        
        assert result["installed"] is False
        assert "Command not found" in result["error"]
    
    @patch('subprocess.run')
    def test_software_check_subprocess_error(self, mock_run):
        """Test handling of subprocess errors"""
        mock_run.side_effect = subprocess.SubprocessError("Process error")
        
        result = check_software_installed_with_exceptions("python")
        
        assert result["installed"] is False
        assert "Subprocess error" in result["error"]
    
    def test_unknown_software_check(self):
        """Test checking unknown software"""
        result = check_software_installed_with_exceptions("unknown_software_xyz")
        
        assert result["installed"] is False
        assert "Don't know how to check" in result["error"]
    
    def test_empty_software_name_check(self):
        """Test checking with empty software name"""
        with pytest.raises(WorkspaceAIError):
            check_software_installed_with_exceptions("")
    
    def test_none_software_name_check(self):
        """Test checking with None software name"""
        with pytest.raises(WorkspaceAIError):
            check_software_installed_with_exceptions(None)  # type: ignore
    
    @patch('subprocess.run')
    def test_software_path_detection(self, mock_run):
        """Test software path detection"""
        # Mock the version check
        mock_process_version = MagicMock()
        mock_process_version.returncode = 0
        mock_process_version.stdout = "Python 3.9.0"
        
        # Mock the path check
        mock_process_path = MagicMock()
        mock_process_path.returncode = 0
        mock_process_path.stdout = "/usr/bin/python3"
        
        mock_run.side_effect = [mock_process_version, mock_process_path]
        
        result = check_software_installed_with_exceptions("python")
        
        assert result["installed"] is True
        assert result["path"] == "/usr/bin/python3"
    
    @patch('subprocess.run')
    def test_software_path_detection_failure(self, mock_run):
        """Test software path detection failure"""
        # Mock successful version check
        mock_process_version = MagicMock()
        mock_process_version.returncode = 0
        mock_process_version.stdout = "Python 3.9.0"
        
        # Mock failed path check
        mock_run.side_effect = [mock_process_version, FileNotFoundError()]
        
        result = check_software_installed_with_exceptions("python")
        
        assert result["installed"] is True
        assert result["path"] is None  # Should still succeed without path


class TestDetectLinuxPackageManager:
    """Test Linux package manager detection"""
    
    @patch('shutil.which')
    @patch('platform.system')
    def test_detect_apt(self, mock_system, mock_which):
        """Test detecting apt package manager"""
        mock_system.return_value = "Linux"
        mock_which.side_effect = lambda x: "/usr/bin/apt" if x == "apt" else None
        
        with patch('src.utils.platform.system', return_value="Linux"):
            result = detect_linux_package_manager()
        
        assert result == "apt"
    
    @patch('shutil.which')
    @patch('platform.system')
    def test_detect_dnf(self, mock_system, mock_which):
        """Test detecting dnf package manager"""
        mock_system.return_value = "Linux"
        mock_which.side_effect = lambda x: "/usr/bin/dnf" if x == "dnf" else None
        
        result = detect_linux_package_manager()
        
        assert result == "dnf"
    
    @patch('shutil.which')
    @patch('platform.system')
    def test_detect_yum(self, mock_system, mock_which):
        """Test detecting yum package manager"""
        mock_system.return_value = "Linux"
        mock_which.side_effect = lambda x: "/usr/bin/yum" if x == "yum" else None
        
        result = detect_linux_package_manager()
        
        assert result == "yum"
    
    @patch('shutil.which')
    @patch('platform.system')
    def test_detect_pacman(self, mock_system, mock_which):
        """Test detecting pacman package manager"""
        mock_system.return_value = "Linux"
        mock_which.side_effect = lambda x: "/usr/bin/pacman" if x == "pacman" else None
        
        result = detect_linux_package_manager()
        
        assert result == "pacman"
    
    @patch('shutil.which')
    @patch('platform.system')
    def test_no_package_manager_found(self, mock_system, mock_which):
        """Test when no package manager is found"""
        mock_system.return_value = "Linux"
        mock_which.return_value = None
        
        result = detect_linux_package_manager()
        
        assert result is None


class TestGetSystemInfo:
    """Test system information collection"""
    
    @patch('platform.system')
    @patch('platform.release')
    @patch('platform.machine')
    @patch('platform.python_version')
    def test_basic_system_info(self, mock_python_ver, mock_machine, mock_release, mock_system):
        """Test basic system information collection"""
        mock_system.return_value = "Linux"
        mock_release.return_value = "5.4.0"
        mock_machine.return_value = "x86_64"
        mock_python_ver.return_value = "3.9.0"
        
        with patch('os.environ.get') as mock_env, \
             patch('src.software_installer.check_software_installed') as mock_check:
            mock_env.side_effect = lambda key, default="unknown": {
                "SHELL": "/bin/bash",
                "USER": "testuser"
            }.get(key, default)
            mock_check.return_value = {"installed": True}
            
            result = get_system_info_with_exceptions()
            
            assert result["os"] == "Linux"
            assert result["release"] == "5.4.0"
            assert result["architecture"] == "x86_64"
            assert result["python_version"] == "3.9.0"
            assert result["shell"] == "/bin/bash"
            assert result["user"] == "testuser"
    
    @patch('platform.system')
    def test_windows_system_info(self, mock_system):
        """Test Windows system information"""
        mock_system.return_value = "Windows"
        
        with patch('os.environ.get') as mock_env, \
             patch('src.software_installer.check_software_installed') as mock_check:
            mock_env.side_effect = lambda key, default="unknown": {
                "COMSPEC": "cmd.exe",
                "USERNAME": "testuser"
            }.get(key, default)
            mock_check.return_value = {"installed": False}
            
            result = get_system_info_with_exceptions()
            
            assert result["os"] == "Windows"
            assert result["shell"] == "cmd.exe"
            assert result["user"] == "testuser"
    
    @patch('platform.system')
    @patch('builtins.open', mock_open(read_data='PRETTY_NAME="Ubuntu 20.04 LTS"'))
    @patch('os.path.exists')
    def test_linux_distribution_info(self, mock_exists, mock_system):
        """Test Linux distribution information extraction"""
        mock_system.return_value = "Linux"
        mock_exists.return_value = True
        
        with patch('src.software_installer.detect_linux_package_manager') as mock_detect, \
             patch('src.software_installer.check_software_installed') as mock_check:
            mock_detect.return_value = "apt"
            mock_check.return_value = {"installed": True}
            
            result = get_system_info_with_exceptions()
            
            assert result["distribution"] == "Ubuntu 20.04 LTS"
            assert result["package_manager"] == "apt"
    
    @patch('platform.system')
    @patch('os.path.exists')
    def test_linux_no_os_release(self, mock_exists, mock_system):
        """Test Linux without /etc/os-release file"""
        mock_system.return_value = "Linux"
        mock_exists.return_value = False
        
        with patch('src.software_installer.check_software_installed') as mock_check:
            mock_check.return_value = {"installed": False}
            
            result = get_system_info_with_exceptions()
            
            assert result["distribution"] == "Unknown Linux"
    
    @patch('platform.system')
    def test_system_info_exception_handling(self, mock_system):
        """Test exception handling in system info collection"""
        mock_system.side_effect = Exception("Platform error")
        
        with pytest.raises(WorkspaceAIError):
            get_system_info_with_exceptions()
    
    @patch('platform.system')
    def test_available_tools_check(self, mock_system):
        """Test available tools checking"""
        mock_system.return_value = "Linux"
        
        with patch('src.software_installer.check_software_installed') as mock_check:
            # Mock different tools having different availability
            def mock_check_side_effect(tool):
                return {"installed": tool in ["git", "curl"]}
            
            mock_check.side_effect = mock_check_side_effect
            
            result = get_system_info_with_exceptions()
            
            assert "available_tools" in result
            assert result["available_tools"]["git"] is True
            assert result["available_tools"]["curl"] is True
            assert result["available_tools"]["docker"] is False


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_generate_commands_with_exception_conversion(self):
        """Test exception conversion in generate_install_commands"""
        with patch('platform.system', side_effect=OSError("System error")):
            with pytest.raises(WorkspaceAIError):
                generate_install_commands_with_exceptions("python", "auto")
    
    @patch('subprocess.run')
    def test_check_software_general_exception(self, mock_run):
        """Test general exception handling in software checking"""
        mock_run.side_effect = Exception("Unexpected error")
        
        with pytest.raises(WorkspaceAIError):
            check_software_installed_with_exceptions("python")
    
    def test_fuzzy_software_matching(self):
        """Test fuzzy software name matching"""
        with patch('platform.system', return_value='Windows'):
            # Test partial matches
            result = generate_install_commands_with_exceptions("py", "auto")
            assert "python" in result.lower()
            
            # Test containing matches
            result = generate_install_commands_with_exceptions("visual studio", "auto")
            assert "code" in result.lower()
    
    def test_method_validation_comprehensive(self):
        """Test comprehensive method validation"""
        valid_methods = ["auto", "winget", "brew", "apt", "manual"]
        
        with patch('platform.system', return_value='Windows'):
            for method in valid_methods:
                try:
                    generate_install_commands_with_exceptions("python", method)
                except UnsupportedPlatformError:
                    pass  # This is OK for platform-specific methods
                except WorkspaceAIError as e:
                    if "Invalid method" in str(e):
                        pytest.fail(f"Method {method} should be valid")
    
    @patch('platform.system')
    def test_platform_detection_edge_cases(self, mock_system):
        """Test platform detection edge cases"""
        # Test empty platform string
        mock_system.return_value = ""
        with pytest.raises(UnsupportedPlatformError):
            generate_install_commands_with_exceptions("python", "auto")
        
        # Test None platform
        mock_system.return_value = None
        with pytest.raises(UnsupportedPlatformError):
            generate_install_commands_with_exceptions("python", "auto")


class TestSoftwareDatabase:
    """Test software database coverage"""
    
    def test_all_major_software_covered(self):
        """Test that major software packages are covered"""
        major_software = [
            "python", "nodejs", "git", "docker", "vscode", 
            "ollama", "chrome", "firefox", "vim", "curl"
        ]
        
        with patch('platform.system', return_value='Windows'):
            for software in major_software:
                result = generate_install_commands_with_exceptions(software, "auto")
                assert software.lower() in result.lower()
                assert "not found in database" not in result
    
    def test_all_platforms_coverage(self):
        """Test that major platforms are covered for Python"""
        platforms = ["Windows", "Darwin", "Linux"]
        
        for platform_name in platforms:
            with patch('platform.system', return_value=platform_name):
                if platform_name == "Linux":
                    with patch('src.software_installer.detect_linux_package_manager', return_value="apt"):
                        result = generate_install_commands_with_exceptions("python", "auto")
                else:
                    result = generate_install_commands_with_exceptions("python", "auto")
                
                assert isinstance(result, str)
                assert len(result) > 0
                assert "python" in result.lower()
