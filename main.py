#!/usr/bin/env python3
"""
WorkspaceAI v3.0 - Modular Entry Point
Enhanced AI Assistant with collaborative development support
"""

import sys
import os

# Add the workspaceai package to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the main functionality
from workspaceai import main

if __name__ == "__main__":
    main()
