# Tool Selection Problem - Research Request for Claude

## Problem Summary

We have a WorkspaceAI application that uses function calling with Ollama/Qwen models. The core issue is **fundamental tool selection failure** where the AI consistently chooses incorrect tools despite clear user intent.

### Specific Failure Example
- **User Input:** "write me a guide for git"
- **Expected:** `create_file` with guide content
- **Actual:** `generate_install_commands` for git installation
- **Root Cause:** AI sees "git" keyword and matches it to installation function instead of understanding "write me a guide" context

## Current System Architecture

### Tool Schema Structure
```json
{
  "type": "function",
  "function": {
    "name": "create_file",
    "description": "Create a new file with specified content. Use this for ANY file type including .csv, .txt, .py, .md, .json, etc. ALWAYS use this when user wants to create, write, make, save, or generate any kind of file, document, guide, or text content.",
    "parameters": {
      "type": "object",
      "properties": {
        "file_name": {"type": "string", "description": "Name of the file to create"},
        "content": {"type": "string", "description": "Content to write to the file"}
      },
      "required": ["file_name", "content"]
    }
  }
}
```

```json
{
  "type": "function", 
  "function": {
    "name": "generate_install_commands",
    "description": "Generate software installation commands. ONLY use when user explicitly asks for installation instructions, setup commands, or how to install software. DO NOT use for creating guides, documentation, or files about software.",
    "parameters": {
      "type": "object",
      "properties": {
        "software": {"type": "string", "description": "Name of the software to generate installation commands for"}
      },
      "required": ["software"]
    }
  }
}
```

### Current System Prompt
```
You are WorkspaceAI, an intelligent file management assistant with access to file operation tools in a secure workspace environment.

**CRITICAL RULE:** When tools are available and users request file operations, you MUST use the tools immediately. Do not provide explanations or instructions - execute the action directly.

**ABSOLUTE REQUIREMENTS:**
- If user mentions creating, writing, saving, making files → USE TOOLS IMMEDIATELY
- If user mentions reading, opening, viewing files → USE TOOLS IMMEDIATELY  
- If user mentions listing, searching, finding files → USE TOOLS IMMEDIATELY
- If user mentions copying, moving, deleting files → USE TOOLS IMMEDIATELY
- If user asks to "save that as [filename]" → USE create_file or write_to_file IMMEDIATELY

**CONTEXTUAL PATTERNS:** These phrases indicate file operations:
- "make that a file" / "save that" / "create file" → USE TOOLS
- "put that in a file" / "write to file" → USE TOOLS
- "show me files" / "list files" / "what files" → USE TOOLS
- "find files" / "search for" / "look for files" → USE TOOLS

You have access to comprehensive file management tools. When users request file operations, execute them immediately using the appropriate tools. Do not ask for permission or provide instructions instead of acting.

For non-file requests (general questions, conversations), respond normally without tools.
```

### Current Enforcement Message (Added to Each Request)
```
CRITICAL: Use exact function names from schema. 
Common corrections: backup_files→copy_file, create_csv_file→create_file, find_files→search_files.

TOOL SELECTION RULES:
- "write/create/save/make a guide/file/document" = create_file
- "install commands/how to install" = generate_install_commands
- When in doubt about file creation vs installation, choose create_file for writing content

When use_tools=True, execute tools immediately.
```

## Fundamental Issues Identified

1. **Keyword Override:** AI prioritizes individual keywords ("git") over contextual intent ("write me a guide")
2. **Description Ambiguity:** Despite explicit negative instructions, the AI still confuses similar domains
3. **Prompt Competition:** Multiple system messages may be competing/conflicting
4. **Insufficient Hierarchical Guidance:** No clear priority system for tool selection

## Real-World Test Results

- **Simple Commands:** ~80% success ("create file.txt", "list files")
- **Natural Language:** ~20% success ("write me a guide for git", "make a backup of this")
- **Compound Requests:** ~5% success ("create a csv file with this data")

## Technical Constraints

- Using Ollama with Qwen 2.5:3b model (local, not cloud)
- Function calling via OpenAI-compatible API format
- No fine-tuning capability - must solve with prompting
- Real-time execution (can't do multi-pass reasoning)

## Research Questions for Claude

1. **Advanced Prompting Patterns:** What are the most effective prompting techniques used in production systems for disambiguating tool selection in function calling scenarios?

2. **Hierarchical Intent Recognition:** How do systems like Claude, GPT-4, or other production AI handle conflicting keywords vs contextual intent? Are there specific prompt structures that create clear decision trees?

3. **Negative Instruction Effectiveness:** What are proven methods for making "DO NOT use X when Y" instructions actually work in practice? Are there linguistic patterns that models follow better?

4. **Context Weighting Techniques:** How can we structure prompts so that contextual phrases ("write me a guide") carry more weight than individual keywords ("git")?

5. **Production System Analysis:** Can you research how companies like Anthropic, OpenAI, or others structure their system prompts for function calling? What patterns emerge?

6. **Model Architecture Considerations:** Are there specific prompting techniques that work better with smaller models (3B parameters) vs larger ones?

7. **Alternative Architectures:** Should we consider a two-stage approach (intent classification → tool selection) or other architectural patterns?

## Specific Research Request

Please research and provide:

1. **Concrete examples** of production-grade system prompts for function calling
2. **Specific linguistic patterns** that improve tool disambiguation
3. **Proven techniques** for handling keyword conflicts in natural language
4. **Alternative prompt structures** that might solve this fundamental issue
5. **Any academic papers or resources** on this specific problem domain

## Success Criteria

We need the system to correctly choose `create_file` for "write me a guide for git" instead of `generate_install_commands`. This represents the core pattern we must solve to make the system viable for real-world use.

The goal is to find prompting techniques that fundamentally improve contextual understanding rather than continuing to add more specific rules and edge cases.
