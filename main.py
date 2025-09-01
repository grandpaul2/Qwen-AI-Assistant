#!/usr/bin/env python3
"""
WorkspaceAI v3.0 - Modular Entry Point
Enhanced AI Assistant with collaborative development support
"""

import sys
import os

# Add the workspaceai package to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the main functionality from modular package
    from workspaceai import main
    print("🤖 WorkspaceAI v3.0 - Modular Architecture")
    print("Enhanced AI Assistant with collaborative development support")
    print("=" * 60)
except ImportError as e:
    print(f"Error importing WorkspaceAI modules: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check the logs in WorkspaceAI/qwen_assistant.log for details")
        sys.exit(1)
