import os
import sys
import json
import time
import pytest
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import src.config as cfg
from src.memory import MemoryManager
from src.config import CONSTANTS
from src.exceptions import ConversationError, WorkspaceAIError

class DummyResponse:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

@ pytest.fixture(autouse=True)
def no_logging(monkeypatch):
    # suppress logging
    monkeypatch.setattr(logging, 'error', lambda *args, **kwargs: None)
    monkeypatch.setattr(logging, 'warning', lambda *args, **kwargs: None)
    monkeypatch.setattr(logging, 'info', lambda *args, **kwargs: None)
    monk = monkeypatch
    yield

@pytest.fixture
def mm(tmp_path, monkeypatch):
    # Override module-level get_memory_path in src.memory to tmp_path
    import importlib
    memory_mod = importlib.import_module('src.memory')
    monkeypatch.setattr(memory_mod, 'get_memory_path', lambda: str(tmp_path))
    # Create manager after patch so memory_file under tmp_path
    mp = MemoryManager()
    return mp

def test_load_memory_no_file_creates_empty_lists(mm, tmp_path):
    # On init, memory_file should be created via save_memory in reset
    mem_file = tmp_path / 'memory.json'
    assert mem_file.exists()
    assert mm.current_conversation == []
    assert mm.recent_conversations == []
    assert mm.summarized_conversations == []

def test_save_memory_writes_contents(mm, tmp_path):
    # Add a message and save
    mm.current_conversation = [{'role': 'user', 'content': 'hi', 'timestamp': 't'}]
    mm.save_memory()
    data = json.loads((tmp_path / 'memory.json').read_text())
    assert 'current_conversation' in data
    assert data['current_conversation'][0]['content'] == 'hi'

def test_save_memory_async(mm, tmp_path):
    mm.current_conversation = [{'role': 'assistant', 'content': 'bot', 'timestamp': 't'}]
    mm.save_memory_async()
    # wait for async write
    time.sleep(0.1)
    assert (tmp_path / 'memory.json').exists()

def test_add_message_valid_and_invalid(mm):
    # Valid
    result = mm.add_message('user', 'hello')
    assert mm.current_conversation[-1]['content'] == 'hello'
    # Invalid role
    prev = len(mm.current_conversation)
    assert mm.add_message('invalid', 'oops') is None
    assert len(mm.current_conversation) == prev
    # Invalid content
    assert mm.add_message('user', None) is None

def test_start_new_conversation_branches(mm, monkeypatch, capsys):
    # Add two messages
    mm.current_conversation = [
        {'role': 'user', 'content': 'm1', 'timestamp': 't1'},
        {'role': 'assistant', 'content': 'm2', 'timestamp': 't2'}
    ]
    # Mock summarize to track calls
    called = {}
    def fake_summarize(msgs):
        called['sum'] = True
        return 'sum'
    monkeypatch.setattr(mm, 'summarize_conversation', fake_summarize)
    # First new conversation
    mm.start_new_conversation()
    out1 = capsys.readouterr().out
    assert 'Started new conversation' in out1
    assert len(mm.recent_conversations) == 1
    # Fill recent to exceed max
    mm.current_conversation = [{'role': 'user','content':'x','timestamp':'t'}]
    # Insert pre-existing to simulate full recent
    mm.recent_conversations = [{'date':'d','messages':[]}] * CONSTANTS['MAX_RECENT_CONVERSATIONS']
    mm.start_new_conversation()
    # Should summarize oldest to summarized_conversations
    assert called.get('sum')
    assert len(mm.summarized_conversations) >= 1

def test_summarize_conversation_http(monkeypatch, mm):
    messages = [
        {'role':'user','content':'foo','timestamp':'2025-09-02T00:00:00'}
    ]
    # Success case
    monkeypatch.setattr('requests.post', lambda *args, **kwargs: DummyResponse(200, {'message':{'content':'ok'}}))
    assert mm.summarize_conversation(messages) == 'ok'
    # Server error case
    monkeypatch.setattr('requests.post', lambda *args, **kwargs: DummyResponse(500))
    res = mm.summarize_conversation(messages)
    assert res.startswith('Conversation from 2025-09-02')
    # Timeout case
    import requests
    def fake_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout('timeout')
    monkeypatch.setattr('requests.post', fake_timeout)
    res2 = mm.summarize_conversation(messages)
    assert res2.startswith('Conversation from 2025-09-02')

def test_get_context_messages(mm):
    # Populate memory
    mm.current_conversation = [{'role':'user','content':'u','timestamp':'t'}]
    mm.recent_conversations = [{'date':'d','messages':[{'role':'assistant','content':'a','timestamp':'t'}]}]
    mm.summarized_conversations = [{'date':'d','summary':'s'}]
    ctx = mm.get_context_messages()
    # First entry is system prompt
    assert ctx[0]['role'] == 'system'
    # Contains summary and messages
    assert any('s' in msg.get('content','') for msg in ctx)
    assert any(msg['role']=='assistant' for msg in ctx)
