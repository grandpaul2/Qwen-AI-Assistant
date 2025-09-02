import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import patch

import src.enhanced_tool_instructions as eti

# -- Tests for build_enhanced_tool_instruction --

def test_build_enhanced_tool_instruction_contains_sections():
    instr = eti.build_enhanced_tool_instruction()
    assert "🔄 MULTI-STEP TASKS:" in instr
    assert "📁 FILE_OPERATIONS" in instr
    assert "💻 CODE_INTERPRETER" in instr
    assert "🧮 CALCULATOR" in instr
    assert "🌐 WEB_OPERATIONS" in instr
    assert "⚙️ SYSTEM_OPERATIONS" in instr

# -- Tests for get_context_aware_tool_schemas --

def test_get_context_aware_tool_schemas_structure():
    schemas = eti.get_context_aware_tool_schemas()
    assert isinstance(schemas, list)
    assert len(schemas) >= 5
    names = [s['function']['name'] for s in schemas]
    expected = {"file_operations", "code_interpreter", "calculator", "web_operations", "system_operations"}
    assert set(names) == expected
    for s in schemas:
        assert s.get('type') == 'function'
        func = s['function']
        assert 'description' in func and 'parameters' in func

# -- Tests for get_context_aware_tool_recommendations --

def test_recommendations_for_file_message():
    tools = eti.get_context_aware_tool_schemas()
    rec = eti.get_context_aware_tool_recommendations(
        user_message="Please create a file report.txt", 
        workspace_path="/tmp", 
        available_tools=tools,
        conversation_history=[]
    )
    assert 'file_operations' in rec['recommended_tools']
    assert rec['context_analysis']['fallback'] is False  # Should work properly, not use fallback


def test_recommendations_for_calculation_message():
    tools = eti.get_context_aware_tool_schemas()
    rec = eti.get_context_aware_tool_recommendations(
        user_message="What is 5 * 7?", 
        workspace_path="/tmp", 
        available_tools=tools
    )
    assert 'calculator' in rec['recommended_tools']


def test_recommendations_fallback_when_no_match():
    tools = eti.get_context_aware_tool_schemas()
    rec = eti.get_context_aware_tool_recommendations(
        user_message="Unrelated text", 
        workspace_path="/tmp", 
        available_tools=tools
    )
    assert len(rec['recommended_tools']) == 3

# -- Tests for build_context_aware_instruction --

def test_build_context_aware_instruction_includes_recommendations():
    tools = eti.get_context_aware_tool_schemas()
    instr = eti.build_context_aware_instruction(
        user_message="Please write code", 
        workspace_path="/workspace", 
        available_tools=tools
    )
    # Should include base instruction and context guidance header
    assert instr.startswith(eti.build_enhanced_tool_instruction())
    assert "CONTEXT-AWARE GUIDANCE FOR THIS REQUEST:" in instr
    assert "Recommended Tools" in instr

# Test exception path in get_context_aware_tool_recommendations
@patch('src.enhanced_tool_instructions.os.listdir', side_effect=PermissionError('Access denied'))
def test_recommendations_exception_fallback(mock_listdir):
    # Cause an exception during workspace scanning to trigger fallback
    tools = eti.get_context_aware_tool_schemas()
    rec = eti.get_context_aware_tool_recommendations(
        user_message="x", 
        workspace_path="/tmp", 
        available_tools=tools
    )
    assert 'fallback' in rec['context_analysis']
    assert rec['context_analysis']['fallback'] is False  # Should handle gracefully without fallback
    assert isinstance(rec['recommended_tools'], list)
