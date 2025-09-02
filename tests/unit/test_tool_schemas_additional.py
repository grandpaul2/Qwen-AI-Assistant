import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import patch

import src.tool_schemas as ts
from src.exceptions import WorkspaceAIError

# -- Tests for get_all_tool_schemas_with_exceptions --

def test_get_all_tool_schemas_with_exceptions_success():
    schemas = ts.get_all_tool_schemas_with_exceptions()
    assert isinstance(schemas, list)
    assert len(schemas) > 0
    # Check first schema structure
    first = schemas[0]
    assert 'type' in first and first['type'] == 'function'
    func = first.get('function')
    assert isinstance(func, dict)
    assert 'name' in func and isinstance(func['name'], str)

# -- Tests for get_all_tool_schemas wrapper fallback --

@patch('src.tool_schemas.get_all_tool_schemas_with_exceptions', side_effect=Exception('fail'))
def test_get_all_tool_schemas_wrapper_on_error(mock_exc, capsys):
    schemas = ts.get_all_tool_schemas()
    out = capsys.readouterr().out
    assert isinstance(schemas, list)
    assert len(schemas) == 1
    schema = schemas[0]
    assert schema['function']['name'] == 'create_file'
    assert 'Warning: Tool schema error: fail' in out

# -- Tests for validation errors in with_exceptions --

def test_get_all_tool_schemas_with_exceptions_empty_schemas(monkeypatch, capsys):
    # Patch a scenario where schemas list is empty
    def fake_empty():
        return []
    monkeypatch.setattr(ts, 'get_all_tool_schemas_with_exceptions', fake_empty)
    # When internal returns empty, wrapper should catch and return minimal schema
    schemas = ts.get_all_tool_schemas()
    out = capsys.readouterr().out
    assert isinstance(schemas, list)
    assert len(schemas) == 1
    # Fallback schema should be create_file
    schema = schemas[0]
    assert schema['function']['name'] == 'create_file'
    # Warning message should indicate the error
    assert 'Tool schemas cannot be empty' in out
