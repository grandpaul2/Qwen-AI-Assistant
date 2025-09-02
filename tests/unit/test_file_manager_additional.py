import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from pathlib import Path

import src.config as cfg
from src.file_manager import FileManager
from src.exceptions import WorkspaceAIError, ToolParameterError

# Fixture to provide a FileManager with workspace path overridden to tmp_path
def file_manager(tmp_path, monkeypatch):
    # Create FileManager and override base_path to tmp_path
    config = cfg.APP_CONFIG.copy()
    config['safe_mode'] = True
    fm = FileManager(config=config)
    # Override workspace base path
    fm.base_path = str(tmp_path)
    return fm

# Tests for create_file and read_file
def test_create_and_read_file(tmp_path, monkeypatch):
    fm = file_manager(tmp_path, monkeypatch)
    # Create a file
    result = fm.create_file('test.txt', 'hello')
    assert "created successfully" in result
    # File exists
    file_path = tmp_path / 'test.txt'
    assert file_path.exists()
    content = file_path.read_text(encoding='utf-8')
    assert content == 'hello'
    # Read file using FileManager
    output = fm.read_file('test.txt')
    assert output == 'hello'
    # Read non-existent file
    err = fm.read_file('nope.txt')
    assert err.startswith('Error:')

# Test unique filename generation when file exists
def test_create_file_uniqueness(tmp_path, monkeypatch):
    fm = file_manager(tmp_path, monkeypatch)
    # First create
    res1 = fm.create_file('dup.txt', 'one')
    assert "created successfully" in res1
    # Second create should rename
    res2 = fm.create_file('dup.txt', 'two')
    assert "original name already existed" in res2
    # Confirm both files exist with unique names
    files = sorted(p.name for p in Path(str(tmp_path)).iterdir())
    assert 'dup.txt' in files
    # Find renamed file
    renamed = [f for f in files if f.startswith('dup_')][0]
    assert renamed.endswith('.txt')

# Tests for write_to_file
def test_write_to_file(tmp_path, monkeypatch):
    fm = file_manager(tmp_path, monkeypatch)
    # Write to new file
    out = fm.write_to_file('w.txt', 'data')
    assert "Content written to" in out
    # Overwrite existing triggers uniqueness
    out2 = fm.write_to_file('w.txt', 'more')
    assert "original name already existed" in out2

# Tests for delete_file behavior
def test_delete_file_safe_mode(tmp_path, monkeypatch):
    fm = file_manager(tmp_path, monkeypatch)
    # Safe mode on, delete should be disabled
    msg = fm.delete_file('any.txt')
    assert 'Safe mode is ON' in msg

def test_delete_file_force(tmp_path, monkeypatch):
    # Setup FileManager with base_path = tmp_path and safe_mode disabled
    config = cfg.APP_CONFIG.copy()
    config['safe_mode'] = False
    fm = FileManager(config=config)
    fm.base_path = str(tmp_path)
    # Create a file
    file = Path(str(tmp_path)) / 'del.txt'
    file.write_text('x')
    # Delete existing
    msg = fm.delete_file('del.txt')
    assert "deleted successfully" in msg
    # Delete missing
    err = fm.delete_file('no.txt')
    assert err.startswith('Error:')

# Tests for list_files
def test_list_files(tmp_path, monkeypatch):
    fm = file_manager(tmp_path, monkeypatch)
    # Create files and subdir
    (tmp_path / 'a.txt').write_text('')
    sub = tmp_path / 'sub'
    sub.mkdir()
    (sub / 'b.txt').write_text('')
    # List root
    root_list = fm.list_files()
    assert 'a.txt' in root_list
    # List subdirectory
    sub_list = fm.list_files('sub')
    assert 'b.txt' in sub_list
    # List non-existent
    err = fm.list_files('noui')
    assert err.startswith('Error:')
