# WorkspaceAI Tool Detection Issue Analysis & Proposed Solutions

## **Problem Summary**

WorkspaceAI has a critical UX issue where users request file operations but the AI responds conversationally instead of using available file management tools. 

### **Root Cause Analysis:**
1. **Missing System Prompt**: The model receives tool schemas but no instructions on when/how to use them
2. **Keyword Detection**: Works correctly but may be too liberal, causing false positives
3. **No Tool Usage Guidance**: Model doesn't understand it should prefer tools over conversation

### **Evidence from User Testing:**
- User: "make that guide an .md file for me" → AI gave conversational response instead of creating file
- User: "save it directly to the system" → AI provided manual instructions instead of using tools
- User: "create it yourself and put it in the workspace folder" → AI continued conversational mode

## **Current Implementation**
```python
# Keyword detection (works)
file_keywords = ['file', 'folder', 'create', 'delete', 'read', 'write', ...]
looks_like_file_task = any(keyword in prompt.lower() for keyword in file_keywords)
call_ollama_with_tools(prompt, use_tools=looks_like_file_task)

# Missing: System prompt telling model to USE the tools
```

## **Proposed Solutions**

### **1. Add System Prompt (Critical Fix)**
```python
SYSTEM_PROMPT = """You are an AI assistant with file management tools in a secure workspace folder. 

Always use tools directly for file operations (create, read, write, save, copy, move, list, search, etc.) instead of providing instructions. Respond with your action results.

USER OVERRIDES:
- "chat:" = conversational response only, no tools
- "tools:" = force file tools usage  
- "install:" = provide software installation commands
- Otherwise auto-detect and prefer tools for file tasks

Work within the workspace folder and perform actions immediately when requested."""
```

### **2. Keyword Detection Strategy Options**

**Option A: Liberal Detection (Current + Expanded)**
- Pro: Catches more legitimate requests
- Con: False positives ("I read a book" triggers file tools)
- Use Case: File-heavy workflows

**Option B: Contextual Detection (Recommended)**
- Look for file-related phrases: "create file", "save to", "in workspace"
- Avoid conversational triggers: "how to", "what is", "explain"
- Pro: Better precision, fewer false positives
- Con: Might miss some edge cases

**Option C: Liberal + Smart System Prompt**
- Keep liberal detection but train model to distinguish context
- Rely on model intelligence to avoid inappropriate tool usage
- Pro: Simple implementation
- Con: Model-dependent behavior

### **3. Enhanced Keywords for Liberal Approach**
```python
file_keywords = [
    'file', 'folder', 'directory', 'create', 'make', 'generate', 'build',
    'save', 'write', 'edit', 'copy', 'move', 'list', 'search', 'find',
    'compress', 'backup', 'json', 'txt', 'md', 'workspace', 'put', 'store'
]
```

## **Research Questions for Claude**

1. **Industry Best Practices**: How do other AI assistants with tools (ChatGPT Code Interpreter, etc.) handle tool vs conversation decisions?

2. **Model Behavior Studies**: Are there research papers on tool-calling behavior across different LLM architectures (Qwen, Llama, Mistral)?

3. **System Prompt Effectiveness**: What system prompt patterns have been proven most effective for tool-calling consistency?

4. **False Positive Mitigation**: What techniques exist for reducing tool activation false positives without complex NLU?

5. **User Experience Research**: How do users typically phrase file operation requests vs general questions about files?

6. **Contextual Detection Algorithms**: Are there lightweight methods for intent classification that don't require additional model calls?

## **Implementation Priority**

1. **High Priority**: Add system prompt (fixes 80% of the issue)
2. **Medium Priority**: Improve keyword detection strategy
3. **Low Priority**: Add debug logging and user feedback mechanisms

## **Success Metrics**

- User requests like "create a file" should result in actual file creation
- General questions like "how do files work" should remain conversational
- Users should rarely need to use "tools:" or "chat:" prefixes

**Request for Claude: Please research these questions and recommend the optimal approach for reliable tool vs conversation detection in AI assistants.**
