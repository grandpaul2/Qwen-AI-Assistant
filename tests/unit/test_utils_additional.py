import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import patch
import tempfile
import time

import src.utils as utils
from src.exceptions import WorkspaceAIError

# -- Tests for detect_linux_package_manager --

def test_detect_linux_package_manager_error(monkeypatch, capsys):
    # Simulate exception in with_exceptions
    monkeypatch.setattr(utils, 'detect_linux_package_manager_with_exceptions', lambda: (_ for _ in ()).throw(RuntimeError('pm fail')))
    result = utils.detect_linux_package_manager()
    out = capsys.readouterr().out
    assert result is None
    assert 'Warning: Package manager detection error: pm fail' in out

@patch('src.utils.platform')
@patch('src.utils.shutil')
def test_detect_linux_package_manager_with_exceptions_non_linux(mock_shutil, mock_platform):
    mock_platform.system.return_value = 'Windows'
    with pytest.raises(WorkspaceAIError) as exc:
        utils.detect_linux_package_manager_with_exceptions()
    assert 'current OS' in str(exc.value)

@patch('src.utils.platform')
@patch('src.utils.shutil')
def test_detect_linux_package_manager_with_exceptions_linux_found(mock_shutil, mock_platform):
    mock_platform.system.return_value = 'Linux'
    mock_shutil.which.side_effect = lambda cmd: '/usr/bin/' + cmd if cmd == 'dnf' else None
    result = utils.detect_linux_package_manager_with_exceptions()
    assert result == 'dnf'

# -- Tests for is_safe_filename and exceptions wrapper --

def test_is_safe_filename_with_exceptions_valid():
    assert utils.is_safe_filename_with_exceptions('file.txt') is True

@patch('src.utils.platform')
def test_is_safe_filename_with_exceptions_windows_reserved(mock_platform):
    mock_platform.system.return_value = 'Windows'
    assert utils.is_safe_filename_with_exceptions('CON.txt') is False

def test_is_safe_filename_with_exceptions_non_str():
    with pytest.raises(WorkspaceAIError):
        utils.is_safe_filename_with_exceptions(123)

# Wrapper returns False on exception
@patch('src.utils.is_safe_filename_with_exceptions', side_effect=RuntimeError('boom'))
def test_is_safe_filename_wrapper(mock_exc, capsys):
    result = utils.is_safe_filename('any')
    out = capsys.readouterr().out
    assert result is False
    assert 'Warning: Filename safety check error: boom' in out

# -- Tests for sanitize_filename and exceptions wrapper --

def test_sanitize_filename_with_exceptions_empty():
    assert utils.sanitize_filename_with_exceptions('') == 'file'

def test_sanitize_filename_with_exceptions_non_str():
    with pytest.raises(WorkspaceAIError):
        utils.sanitize_filename_with_exceptions(123)

@patch('src.utils.sanitize_filename_with_exceptions', side_effect=ValueError('err'))
def test_sanitize_filename_wrapper(mock_exc, capsys):
    result = utils.sanitize_filename('x')
    out = capsys.readouterr().out
    assert result == 'safe_file.txt'
    assert 'Warning: Filename sanitization error: err' in out

# -- Tests for get_unique_filename_with_exceptions and wrapper --

def test_get_unique_filename_with_exceptions_errors(tmp_path):
    # None directory
    with pytest.raises(WorkspaceAIError):
        utils.get_unique_filename_with_exceptions(None, 'a.txt')
    # None filename
    with pytest.raises(WorkspaceAIError):
        utils.get_unique_filename_with_exceptions(str(tmp_path), None)
    # non-existent dir
    fake = tmp_path / 'no_dir'
    with pytest.raises(WorkspaceAIError):
        utils.get_unique_filename_with_exceptions(str(fake), 'a.txt')


def test_get_unique_filename_with_exceptions_success(tmp_path):
    d = tmp_path
    # create existing file
    (d / 'f.txt').write_text('x')
    # first unique should be 'f_1.txt'
    result = utils.get_unique_filename_with_exceptions(str(d), 'f.txt')
    assert result == 'f_1.txt'

@patch('src.utils.get_unique_filename_with_exceptions', side_effect=RuntimeError('fail'))
def test_get_unique_filename_wrapper(mock_exc, capsys):
    result = utils.get_unique_filename('dir', 'b.txt')
    out = capsys.readouterr().out
    assert 'file_' in result and result.endswith('.txt')
    assert 'Warning: Unique filename generation error: fail' in out

# -- Tests for bytes_to_human_readable_with_exceptions and wrapper --

def test_bytes_to_human_readable_with_exceptions_errors():
    with pytest.raises(WorkspaceAIError):
        utils.bytes_to_human_readable_with_exceptions(None)
    with pytest.raises(WorkspaceAIError):
        utils.bytes_to_human_readable_with_exceptions('x')
    with pytest.raises(WorkspaceAIError):
        utils.bytes_to_human_readable_with_exceptions(-1)


def test_bytes_to_human_readable_with_exceptions_values():
    assert utils.bytes_to_human_readable_with_exceptions(0) == '0 B'
    assert utils.bytes_to_human_readable_with_exceptions(1024) == '1.0 KB'
    large = 1024**6 * 2
    assert 'e' in utils.bytes_to_human_readable_with_exceptions(large)

@patch('src.utils.bytes_to_human_readable_with_exceptions', side_effect=RuntimeError('fail'))
def test_bytes_to_human_readable_wrapper(mock_exc, capsys):
    result = utils.bytes_to_human_readable(123)
    out = capsys.readouterr().out
    assert result == 'Unknown size'
    assert 'Warning: Bytes conversion error: fail' in out

# -- Tests for validate_json_string_with_exceptions and wrapper --

def test_validate_json_string_with_exceptions():
    assert utils.validate_json_string_with_exceptions('{}') is True
    assert utils.validate_json_string_with_exceptions('[]') is True
    assert utils.validate_json_string_with_exceptions('invalid') is False

@patch('src.utils.validate_json_string_with_exceptions', side_effect=RuntimeError('fail'))
def test_validate_json_string_wrapper(mock_exc, capsys):
    result = utils.validate_json_string('x')
    out = capsys.readouterr().out
    assert result is False
    assert 'Warning: JSON validation error: fail' in out
