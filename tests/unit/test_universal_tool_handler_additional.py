import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import MagicMock, patch

from src.universal_tool_handler import UniversalToolHandler
from src.file_manager import FileManager

# Fixture for a UniversalToolHandler with a mocked FileManager
@pytest.fixture
def handler_with_mocked_file_manager():
    handler = UniversalToolHandler()
    mock_fm = MagicMock(spec=FileManager)
    # Provide return values for all file operations methods
    mock_fm.read_file.return_value = 'content'
    mock_fm.write_to_file.return_value = 'written'
    mock_fm.create_file.return_value = 'created'
    mock_fm.delete_file.return_value = 'deleted'
    mock_fm.list_files.return_value = ['a.txt', 'b.txt']
    mock_fm.copy_file.return_value = 'copied'
    mock_fm.move_file.return_value = 'moved'
    mock_fm.search_files.return_value = ['found1', 'found2']
    handler.file_manager = mock_fm
    return handler

@pytest.mark.parametrize(
    'func_name,args,expected',
    [
        ('read_file', {'file_name': 'x.txt'}, 'content'),
        ('write_file', {'file_name': 'x.txt', 'content': 'd'}, 'written'),
        ('create_file', {'file_name': 'n.txt', 'content': 'd'}, 'created'),
        ('delete_file', {'file_name': 'o.txt'}, 'deleted'),
        ('list_files', {'path': '.'}, ['a.txt', 'b.txt']),
        ('copy_file', {'src_name': 's.txt', 'dst_name': 'd.txt'}, 'copied'),
        ('move_file', {'old_name': 'o.txt', 'new_name': 'n.txt'}, 'moved'),
        ('search_files', {'pattern': '*.txt'}, ['found1', 'found2']),
    ]
)
def test_try_file_operations_standard(handler_with_mocked_file_manager, func_name, args, expected):
    handler = handler_with_mocked_file_manager
    result = handler._try_file_operations(func_name, args)
    assert result == expected

# Test alternative command names mapping to same methods
@pytest.mark.parametrize(
    'alias,expected_method',
    [
        ('read_text_file', 'read_file'),
        ('write_text_file', 'write_to_file'),
        ('save_file', 'create_file'),
        ('remove_file', 'delete_file'),
        ('delete', 'delete_file'),
        ('ls', 'list_files'),
        ('dir', 'list_files'),
        ('cp', 'copy_file'),
        ('mv', 'move_file'),
        ('find', 'search_files'),
        ('grep', 'search_files'),
    ]
)
def test_try_file_operations_aliases(handler_with_mocked_file_manager, alias, expected_method):
    handler = handler_with_mocked_file_manager
    # call with minimal args for method signature
    default_args = {}
    result = handler._try_file_operations(alias, default_args)
    # ensure correct FileManager method called
    getattr(handler.file_manager, expected_method).assert_called()

# Test missing file_manager yields None
def test_try_file_operations_no_file_manager():
    handler = UniversalToolHandler()
    handler.file_manager = None
    assert handler._try_file_operations('read_file', {}) is None

# Test unmapped function returns None
def test_try_file_operations_unmapped(handler_with_mocked_file_manager):
    handler = handler_with_mocked_file_manager
    assert handler._try_file_operations('unknown_op', {}) is None
