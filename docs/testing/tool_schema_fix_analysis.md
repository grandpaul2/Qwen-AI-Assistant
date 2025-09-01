"""
Tool Schema Fix Analysis and Solution

PROBLEM IDENTIFIED:
The `generate_install_commands` function has this description:
"Generate installation commands for popular software (cross-platform)"
with examples including "git", "python", "nodejs", etc.

When users say "write me a guide for git" the AI sees the word "git" and chooses 
`generate_install_commands` instead of `create_file` because:

1. The function description mentions "git" as an example
2. The system prompt emphasizes using tools immediately
3. The AI matches "git" to the installation function before considering context

SOLUTION:
1. Remove specific software examples from generate_install_commands description
2. Make create_file description more prominent for writing/guide creation
3. Add negative guidance to generate_install_commands to avoid confusion
4. Enhance the system prompt with better tool selection logic

CRITICAL INSIGHT:
This isn't an accuracy optimization problem - it's a fundamental tool selection 
logic error caused by keyword matching in function descriptions overriding 
contextual understanding.

IMPLEMENTATION PLAN:
1. Fix tool schema descriptions to be less ambiguous
2. Add context-aware tool selection logic
3. Test with real-world examples that failed
"""
