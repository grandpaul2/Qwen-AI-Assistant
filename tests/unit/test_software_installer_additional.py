import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import subprocess
from unittest.mock import patch

from src.software_installer import (
    generate_install_commands_with_exceptions,
    generate_install_commands,
    check_software_installed,
    check_software_installed_with_exceptions
)
from src.exceptions import WorkspaceAIError, UnsupportedPlatformError

# -- Tests for generate_install_commands_with_exceptions input validation --

def test_generate_install_commands_none_software():
    with pytest.raises(WorkspaceAIError) as exc:
        generate_install_commands_with_exceptions(None)  # type: ignore
    assert "Software name cannot be None" in str(exc.value)

@patch('src.software_installer.platform.system')
def test_generate_install_commands_non_string_platform_error(mock_system):
    mock_system.side_effect = Exception("fail sys")
    with pytest.raises(WorkspaceAIError) as exc:
        generate_install_commands_with_exceptions("python")
    assert "fail sys" in str(exc.value)

# -- Additional tests for generate_install_commands_with_exceptions --

def test_generate_install_commands_non_str_software():
    with pytest.raises(WorkspaceAIError):
        generate_install_commands_with_exceptions(123)  # type: ignore


def test_generate_install_commands_empty_string():
    with pytest.raises(WorkspaceAIError):
        generate_install_commands_with_exceptions("   ")


def test_generate_install_commands_too_long_name():
    long_name = "a" * 101
    with pytest.raises(WorkspaceAIError):
        generate_install_commands_with_exceptions(long_name)


def test_generate_install_commands_invalid_method():
    with pytest.raises(WorkspaceAIError):
        generate_install_commands_with_exceptions("python", method="invalid_method")


def test_generate_install_commands_success_linux(monkeypatch):
    import src.software_installer as si
    monkeypatch.setattr(si.platform, 'system', lambda: "Linux")
    monkeypatch.setattr(si, 'detect_linux_package_manager', lambda: "apt")
    result = generate_install_commands_with_exceptions("python", method="auto")
    assert "📦 Python programming language" in result
    assert "apt install python3" in result or "apt install python" in result

# -- Additional tests for generate_install_commands_with_exceptions unsupported platform --

@patch('src.software_installer.platform.system')
def test_generate_install_commands_unsupported_platform(mock_system):
    # Unknown OS yields UnsupportedPlatformError when platform not in software_db
    import src.software_installer as si
    mock_system.return_value = 'UnknownOS'
    with pytest.raises(si.UnsupportedPlatformError):
        generate_install_commands_with_exceptions('python')

# -- Test method-specific install command path --

@patch('src.software_installer.platform.system')
@patch('src.software_installer.detect_linux_package_manager')
def test_generate_install_commands_direct_method_on_windows(mock_pm, mock_system):
    import src.software_installer as si
    mock_system.return_value = 'Windows'
    # direct method exists in windows commands for python
    result = generate_install_commands_with_exceptions('python', method='direct')
    assert '📋 DIRECT Install:' in result or 'Direct Download' in result

# -- Tests for check_software_installed and its wrapper --

def test_check_software_installed_with_exceptions_none():
    with pytest.raises(WorkspaceAIError):
        check_software_installed_with_exceptions(None)  # type: ignore


def test_check_software_installed_with_exceptions_non_str():
    with pytest.raises(WorkspaceAIError):
        check_software_installed_with_exceptions(456)  # type: ignore


def test_check_software_installed_with_exceptions_empty():
    with pytest.raises(WorkspaceAIError):
        check_software_installed_with_exceptions("   ")


def test_check_software_installed_with_exceptions_unknown():
    result = check_software_installed_with_exceptions("foobar")
    assert result["installed"] is False
    assert "Don't know how to check" in result["error"]


@patch('src.software_installer.subprocess.run')
def test_check_software_installed_with_exceptions_success(mock_run, monkeypatch):
    import src.software_installer as si
    # simulate version check and path check
    class Proc:
        def __init__(self):
            self.returncode = 0
            self.stdout = "cmd v1.0"
            self.stderr = ""
    mock_run.side_effect = [Proc(), Proc()]
    monkeypatch.setattr(si.platform, 'system', lambda: "Linux")
    result = check_software_installed_with_exceptions("git")
    assert result["installed"] is True
    assert "cmd v1.0" in result["version"]
    assert result["path"] == "cmd v1.0"


@patch('src.software_installer.check_software_installed_with_exceptions', side_effect=RuntimeError("fail check"))
def test_check_software_installed_wrapper(mock_exc, capsys):
    result = check_software_installed("node")
    out = capsys.readouterr().out
    assert result["installed"] is False
    assert "Warning: Software check error: fail check" in out

# -- Tests for check_software_installed non-zero exit code and errors --

@patch('src.software_installer.subprocess.run')
def test_check_software_installed_with_exceptions_failure(mock_run, monkeypatch):
    import subprocess
    import src.software_installer as si
    # simulate non-zero return code
    proc = type('P', (), {'returncode': 1, 'stdout': '', 'stderr': 'error happened'})()
    mock_run.return_value = proc
    monkeypatch.setattr(si.platform, 'system', lambda: 'Linux')
    result = check_software_installed_with_exceptions('curl')
    assert result['installed'] is False
    assert result['error'] == 'error happened'

@patch('src.software_installer.subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=['git'], timeout=1))
def test_check_software_installed_with_exceptions_timeout(mock_run, monkeypatch):
    import src.software_installer as si
    monkeypatch.setattr(si.platform, 'system', lambda: 'Linux')
    result = check_software_installed_with_exceptions('git')
    assert 'timed out' in result['error']

@patch('src.software_installer.subprocess.run', side_effect=FileNotFoundError())
def test_check_software_installed_with_exceptions_not_found(mock_run, monkeypatch):
    import src.software_installer as si
    monkeypatch.setattr(si.platform, 'system', lambda: 'Linux')
    result = check_software_installed_with_exceptions('git')
    assert 'Command not found' in result['error']
