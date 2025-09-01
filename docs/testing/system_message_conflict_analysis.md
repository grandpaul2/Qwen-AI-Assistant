# System Message Conflict Analysis & Solution

## 🔍 **Problem Identified:**

**TWO SYSTEM PROMPTS** are being applied simultaneously:

### 1. **Config System Prompt** (memory.py line 166):
```python
CONSTANTS['SYSTEM_PROMPT'] = """You are WorkspaceAI, an intelligent file management assistant...
**CRITICAL RULE:** When tools are available and users request file operations, you MUST use the tools immediately...
```

### 2. **Enforcement Message** (ollama_client.py line 304):
```python
enforcement_msg = """🚨 CRITICAL FUNCTION SELECTION RULES 🚨
ONLY USE THESE EXACT FUNCTION NAMES...
```

## 🚨 **Result**: 
- Extremely long system message (both prompts combined)
- Conflicting instructions 
- Model confusion leading to API timeouts
- Potential token limit issues

## ✅ **Solution Strategy:**

### **Option 1: Merge the Best of Both (Recommended)**
- Use the original config system prompt as the foundation (research-backed)
- Add our function selection improvements as enhancements
- Create one unified, optimized system prompt

### **Option 2: Conditional System Prompts**
- Use config system prompt for basic operations
- Add enforcement message only for complex cases
- Avoid duplication

### **Option 3: Replace Config Prompt**
- Update the config system prompt with our improvements
- Remove the separate enforcement message
- Single source of truth

## 🎯 **Recommended Implementation:**

Update the config system prompt to include our proven improvements while maintaining the research-backed foundation:

```python
UNIFIED_SYSTEM_PROMPT = """You are WorkspaceAI, an intelligent file management assistant with access to file operation tools in a secure workspace environment.

**CRITICAL RULE:** When tools are available and users request file operations, you MUST use the tools immediately. Do not provide explanations or instructions - execute the action directly.

**AVAILABLE FUNCTIONS:** create_file, write_to_file, read_file, write_json_file, read_json_file, copy_file, delete_file, create_folder, delete_folder, list_files, search_files, move_file, write_txt_file, write_md_file, write_json_from_string

**FUNCTION CORRECTIONS (use these exact names):**
- backup_files → copy_file
- create_csv_file → create_file  
- find_files → search_files
- duplicate_file → copy_file

**ABSOLUTE REQUIREMENTS:**
- If user mentions creating, writing, saving, making files → USE TOOLS IMMEDIATELY
- If user mentions reading, opening, viewing files → USE TOOLS IMMEDIATELY  
- If user mentions listing, searching, finding files → USE TOOLS IMMEDIATELY
- If user mentions copying, moving, deleting files → USE TOOLS IMMEDIATELY

For non-file requests (general questions, conversations), respond normally without tools."""
```

## 🔧 **Implementation Steps:**

1. **Test current timeout**: Temporarily disable one system prompt to confirm this fixes the hang
2. **Merge prompts**: Combine the best elements into one unified prompt
3. **Remove duplication**: Eliminate the redundant system message
4. **Test thoroughly**: Validate that accuracy improvements are maintained

## 🎯 **Expected Results:**
- ✅ Eliminates API timeouts/hangs
- ✅ Maintains 90-95% accuracy improvements  
- ✅ Preserves all function selection enhancements
- ✅ Single, clean system prompt
- ✅ Faster API responses
