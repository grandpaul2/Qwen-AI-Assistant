import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

import src.ollama_universal_interface as ui

# -- Tests for _build_open_tool_instruction --

def test_build_open_tool_instruction_contains_keywords():
    instruction = ui._build_open_tool_instruction()
    assert "file_operations" in instruction
    assert "calculator" in instruction
    assert "web_operations" in instruction

# -- Tests for _simple_chat_without_tools --

def test_simple_chat_without_tools_success(monkeypatch):
    dummy_response = {"message": {"content": "hello world"}}
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = dummy_response

    monkeypatch.setattr(ui, 'OllamaClient', lambda: mock_client)

    result = ui._simple_chat_without_tools("hi", None, False)
    assert result == "hello world"


def test_simple_chat_without_tools_no_message(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = {}
    monkeypatch.setattr(ui, 'OllamaClient', lambda: mock_client)

    result = ui._simple_chat_without_tools("hi", None, False)
    assert result is None


def test_simple_chat_without_tools_exception(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("fail")

    mock_client = MagicMock()
    mock_client.chat_completion.side_effect = raise_error
    monkeypatch.setattr(ui, 'OllamaClient', lambda: mock_client)

    result = ui._simple_chat_without_tools("hi", None, False)
    assert result is None

# -- Tests for _call_ollama_with_open_tools --

@patch('src.ollama_universal_interface.memory')
@patch('src.ollama_universal_interface.get_context_aware_tool_schemas')
@patch('src.ollama_universal_interface.build_context_aware_instruction')
@patch('src.ollama_universal_interface.build_enhanced_tool_instruction')
@patch('src.ollama_universal_interface.OllamaClient')
def test_call_open_tools_with_context_fallback(
    mock_client_cls,
    mock_build_basic,
    mock_build_context,
    mock_get_schemas,
    mock_memory
):
    # Setup fallbacks and schemas
    mock_memory.get_context_messages.return_value = []
    mock_get_schemas.return_value = []
    # Context instruction raises
    mock_build_context.side_effect = ValueError("ctx fail")
    mock_build_basic.return_value = "basic sys inst"

    # Dummy client and response
    client_instance = MagicMock()
    client_instance.chat_completion.return_value = {"message": {}, "tool_calls": []}
    mock_client_cls.return_value = client_instance

    response = ui._call_ollama_with_open_tools("prompt", None, False)
    assert response == {"message": {}, "tool_calls": []}
    # Ensure fallback instruction used
    args, kwargs = client_instance.chat_completion.call_args
    messages_arg = args[0]
    assert any(msg.get('content') == "basic sys inst" for msg in messages_arg)

@patch('src.ollama_universal_interface.memory')
@patch('src.ollama_universal_interface.get_context_aware_tool_schemas')
@patch('src.ollama_universal_interface.build_context_aware_instruction')
@patch('src.ollama_universal_interface.OllamaClient')
def test_call_open_tools_verbose_output(
    mock_client_cls,
    mock_build_context,
    mock_get_schemas,
    mock_memory
):
    # Setup with one context message and schemas
    mock_memory.get_context_messages.return_value = [{"role": "user", "content": "x"}]
    # Provide some tool schemas
    mock_get_schemas.return_value = [
        {"function": {"name": "test_tool"}},
        {"function": {"name": "another_tool"}}
    ]
    mock_build_context.return_value = "sys inst"

    # Dummy client
    client_instance = MagicMock()
    client_instance.chat_completion.return_value = {"dummy": True}
    mock_client_cls.return_value = client_instance

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        resp = ui._call_ollama_with_open_tools("prompt", "mymodel", True)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert resp == {"dummy": True}
    assert "🔧 Available tool categories" in output
    assert "test_tool" in output and "another_tool" in output

# -- Tests for call_ollama_with_universal_tools --

def test_call_without_tools(monkeypatch, capsys):
    # Patch config, simple chat, and memory
    monkeypatch.setattr(ui, 'load_config', lambda: {'verbose_output': False})
    monkeypatch.setattr(ui, '_simple_chat_without_tools', lambda p, m, v: "reply text")

    fake_mem = MagicMock()
    monkeypatch.setattr(ui, 'memory', fake_mem)

    ui.call_ollama_with_universal_tools("hello", None, use_tools=False)
    captured = capsys.readouterr()
    assert "reply text" in captured.out
    fake_mem.add_message.assert_called_with("assistant", "reply text")
    fake_mem.save_memory_async.assert_called_once()


def test_call_with_no_response(monkeypatch, capsys):
    # Patch config, memory, and open tools call to return no response
    monkeypatch.setattr(ui, 'load_config', lambda: {'verbose_output': False})
    monkeypatch.setattr(ui, '_simple_chat_without_tools', lambda p, m, v: None)

    fake_mem = MagicMock()
    monkeypatch.setattr(ui, 'memory', fake_mem)
    monkeypatch.setattr(ui, '_call_ollama_with_open_tools', lambda p, m, v: None)

    ui.call_ollama_with_universal_tools("hello", None, use_tools=True)
    captured = capsys.readouterr()
    assert "❌ No response from Ollama" in captured.out

# -- Tests for _get_open_tool_schemas (backward compatibility) --

def test_get_open_tool_schemas_contains_all_categories():
    from src.ollama_universal_interface import _get_open_tool_schemas
    schemas = _get_open_tool_schemas()
    names = [s['function']['name'] for s in schemas]
    assert set(names) == {"file_operations", "code_interpreter", "calculator", "web_operations", "system_operations"}
    # Each schema should have type and parameters
    for s in schemas:
        assert s.get('type') == 'function'
        assert 'parameters' in s['function']

# -- Tests for call_ollama_with_universal_tools with tool calls --

def test_call_with_tools_and_tool_calls(monkeypatch, capsys):
    from src.ollama_universal_interface import call_ollama_with_universal_tools, _call_ollama_with_open_tools
    # config patch
    monkeypatch.setattr('src.ollama_universal_interface.load_config', lambda: {})
    # memory stub
    fake_mem = MagicMock()
    monkeypatch.setattr('src.ollama_universal_interface.memory', fake_mem)
    # simulate open tools response with tool_calls and content
    response = {"message": {"content": "final reply", "tool_calls": [
        {"function": {"name": "func1"}},
        {"function": {"name": "func2"}}
    ]}}
    monkeypatch.setattr('src.ollama_universal_interface', '_call_ollama_with_open_tools', lambda p, m, v: response)
    # patch handle_any_tool_call
    calls = []
    def fake_handle(call):
        calls.append(call)
        if call['function']['name'] == 'func1':
            return {"success": True, "result": "res1"}
        return {"error": "err2", "suggestion": "sugg2"}
    monkeypatch.setattr('src.ollama_universal_interface', 'handle_any_tool_call', fake_handle)

    # run
    call_ollama_with_universal_tools("prompt text", model=None, use_tools=True)
    out = capsys.readouterr().out
    # verify tool output prints
    assert "🛠️ Tool: func1" in out
    assert "📊 Result: res1" in out
    assert "res1" in out
    assert "❌ Tool Error: err2" in out
    assert "💡 Suggestion: sugg2" in out
    # verify final content printed
    assert "final reply" in out
    # ensure memory messages added
    fake_mem.add_message.assert_any_call("assistant", "final reply", response['message']['tool_calls'])
    fake_mem.save_memory_async.assert_called()

# -- Tests for exception in call_ollama_with_universal_tools --

def test_call_ollama_with_universal_tools_exception(monkeypatch, capsys):
    from src.ollama_universal_interface import call_ollama_with_universal_tools
    # force exception
    monkeypatch.setattr('src.ollama_universal_interface', 'load_config', lambda: {})
    monkeypatch.setattr('src.ollama_universal_interface', '_simple_chat_without_tools', lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    # run with use_tools=False to hit simple path
    call_ollama_with_universal_tools("x", None, use_tools=False)
    out = capsys.readouterr().out
    assert "❌ An error occurred: boom" in out

# -- Tests for backward compatibility alias call_ollama_with_tools --

def test_call_ollama_with_tools_alias_routes_correctly(monkeypatch, capsys):
    import src.ollama_universal_interface as ui_mod
    # patch universal call
    called = {}
    def fake_universal(prompt, model, use_tools, verbose):
        called['args'] = (prompt, model, use_tools, verbose)
    monkeypatch.setattr(ui_mod, 'call_ollama_with_universal_tools', fake_universal)
    # patch config verbose
    monkeypatch.setattr(ui_mod, 'load_config', lambda: {'verbose_output': True})

    ui_mod.call_ollama_with_tools('p', 'm', False)
    assert called['args'] == ('p', 'm', False, True)

# -- Test _simple_chat_without_tools prints nothing on None and use_tools=False path error with verbose --

def test_call_without_tools_exception_and_verbose(monkeypatch, capsys):
    import src.ollama_universal_interface as ui_mod
    # patch components to throw
    monkeypatch.setattr(ui_mod, 'load_config', lambda: {'verbose_output': True})
    monkeypatch.setattr(ui_mod, '_simple_chat_without_tools', lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail chat")))
    fake_mem = MagicMock()
    monkeypatch.setattr(ui_mod, 'memory', fake_mem)

    ui_mod.call_ollama_with_universal_tools('hi', None, use_tools=False)
    out = capsys.readouterr().out
    # on exception, should print error message
    assert "❌ An error occurred: fail chat" in out
