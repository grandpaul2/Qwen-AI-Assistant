# Complete Tool Inventory for WorkspaceAI

## Currently Available Tools (5 tools)

### Exposed via Tool Schemas:
1. **create_file** - Create any type of file with content
   - Parameters: `file_name`, `content`
   - Example: "Create a Python script called hello.py"

2. **write_to_file** - Write/overwrite file content  
   - Parameters: `file_name`, `content`
   - Example: "Update the config file with new settings"

3. **read_file** - Read file contents
   - Parameters: `file_name`
   - Example: "Show me what's in the README file"

4. **delete_file** - Delete a file
   - Parameters: `file_name`
   - Example: "Remove the old backup file"

5. **generate_install_commands** - Generate software installation instructions
   - Parameters: `software`, `method`
   - Example: "How do I install Docker?"

## Available but Not Exposed (10+ additional operations)

### File Operations (in FileManager but not in tool schemas):
6. **list_files** - List files in directory
7. **create_folder** - Create directories
8. **delete_folder** - Remove directories  
9. **copy_file** - Copy files
10. **move_file** - Move/rename files
11. **search_files** - Search for files by keyword
12. **write_txt_file** - Specialized text file creation
13. **write_md_file** - Specialized markdown file creation
14. **read_json_file** - Read and parse JSON files
15. **write_json_file** - Write structured JSON data
16. **write_json_from_string** - Convert string to JSON file

## Potential Standard Tools We Could Add

### Core Standard Tools:
17. **file_operations** (Standard consolidated tool)
    - Actions: create, read, write, delete, list, copy, move, search
    - Would replace tools 1-4, 6-11 with one standard interface

18. **code_interpreter** (Industry standard)
    - Execute Python, JavaScript, shell commands
    - Would replace/enhance `generate_install_commands`

19. **web_search** (Industry standard)
    - Search internet for information
    - Useful for finding documentation, solutions

20. **calculator** (Industry standard)
    - Mathematical calculations
    - File size calculations, etc.

### Advanced Tools:
21. **text_processor**
    - Text analysis, formatting, regex operations
    - Extract data from files, format content

22. **git_operations**
    - Git commands: commit, push, pull, status
    - Repository management

23. **package_manager**
    - Install packages via pip, npm, etc.
    - Better than current install command generation

24. **system_info**
    - Get system information, disk space, processes
    - Environment inspection

## Recommended Implementation Priority

### Phase 1: Standardize Existing (Quick Win)
- Replace tools 1-4 with `file_operations` standard tool
- Expose tools 6-11 through the standard interface
- Keep same functionality, improve naming

### Phase 2: Add Core Standards
- Add `code_interpreter` for command execution
- Add `calculator` for math operations
- These are universally expected tools

### Phase 3: Advanced Features  
- Add `web_search` if internet access desired
- Add `git_operations` for developers
- Add domain-specific tools as needed

## Current vs Standard Comparison

| Current (Domain-Specific) | Standard (Industry) | Benefit |
|---------------------------|---------------------|---------|
| create_file, write_to_file, read_file, delete_file | file_operations | Familiar, consolidated |
| generate_install_commands | code_interpreter | More powerful, standard |
| (missing) | calculator | Expected by users |
| (missing) | web_search | Common AI capability |

## Summary
- **Currently accessible: 5 tools** (via schemas)
- **Available but hidden: 10+ tools** (in FileManager)
- **Could implement: 15+ standard tools** (industry conventions)
- **Quick win: Consolidate to `file_operations`** for immediate improvement
