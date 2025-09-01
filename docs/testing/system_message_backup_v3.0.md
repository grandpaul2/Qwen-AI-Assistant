# Current System Message Backup (v3.0 - Tested Version)

## Current Working System Message:
```python
enforcement_msg = """🚨 CRITICAL FUNCTION SELECTION RULES 🚨

ONLY USE THESE EXACT FUNCTION NAMES (verify before calling):
✅ create_file, write_to_file, read_file, write_json_file, read_json_file, copy_file, delete_file, create_folder, delete_folder, list_files, search_files, move_file, write_txt_file, write_md_file, write_json_from_string

🚫 THESE FUNCTIONS DO NOT EXIST (common mistakes):
❌ backup_files → ✅ use copy_file instead
❌ create_csv_file → ✅ use create_file instead
❌ create_txt_file → ✅ use create_file instead
❌ find_files → ✅ use search_files instead
❌ duplicate_file → ✅ use copy_file instead
❌ read_csv_file → ✅ use read_file instead
❌ make_file → ✅ use create_file instead
❌ generate_file → ✅ use create_file instead

⚠️ MANDATORY CHECK: Before calling ANY function, verify the exact function name exists in the ✅ list above. If it doesn't exist, choose the correct alternative from the ✅ list.

🚨 CRITICAL ENFORCEMENT: When use_tools=True is detected, you MUST use tools immediately. Never provide conversational instructions when tools are available. Execute the file operation directly."""

# Dynamic additions based on prompt content:
if "backup" in prompt_lower or ("copy" in prompt_lower and "file" in prompt_lower):
    enforcement_msg += "\n\n🔍 BACKUP/COPY DETECTED: Use copy_file with src_file and dest_file parameters."
elif "csv" in prompt_lower and "create" in prompt_lower:
    enforcement_msg += "\n\n🔍 CSV CREATION DETECTED: Use create_file with .csv filename and CSV content as string."
elif "find" in prompt_lower or "search" in prompt_lower:
    enforcement_msg += "\n\n🔍 SEARCH/FIND DETECTED: Use search_files with keyword parameter."
elif "json" in prompt_lower and ("create" in prompt_lower or "write" in prompt_lower):
    enforcement_msg += "\n\n🔍 JSON CREATION DETECTED: Use write_json_file with dictionary content."
```

## Testing Results:
- ✅ Function selection accuracy: 90-95%
- ✅ Auto-correction working: backup_files → copy_file
- ✅ Parameter mapping functional
- ✅ Tool detection: 95-98%
- ❌ **ISSUE**: Hanging/timeout on API calls in real-world testing

## Current Issue Analysis:
1. **Problem**: AI detects tools correctly but hangs during API call
2. **Symptoms**: 
   - Tool detection works: `use_tools=True` ✅
   - API call starts but never completes ❌
   - No response from Ollama API ❌
3. **Suspected causes**:
   - System message too complex/long?
   - Token limit issues?
   - API timeout configuration?
   - Model confusion from complex instructions?

## Next Steps:
1. Test with simplified system message to isolate issue
2. Check API timeout settings
3. Gradually add back complexity to find breaking point
4. Preserve the working parts while fixing the hang

## Key Components to Preserve:
- ✅ Function name validation and mapping
- ✅ Auto-correction system (backup_files → copy_file)
- ✅ Parameter auto-correction 
- ✅ Enhanced tool detection patterns
- ✅ Smart exclusion patterns with file-specific exceptions

## Original Research Reference:
- Tool detection recommendations document provides foundation
- Research-backed system prompt patterns
- Industry best practices for tool calling
- Contextual detection strategies
