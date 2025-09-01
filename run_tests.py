#!/usr/bin/env python3
"""
Test runner script for WorkspaceAI

This script provides convenient commands for running different types of tests.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(command: list[str]) -> int:
    """Run a command and return the exit code"""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        return 1


def main():
    """Main test runner"""
    if len(sys.argv) < 2:
        print("WorkspaceAI Test Runner")
        print()
        print("Usage: python run_tests.py [command]")
        print()
        print("Commands:")
        print("  all          - Run all tests")
        print("  unit         - Run unit tests only")
        print("  integration  - Run integration tests only")
        print("  security     - Run security tests only")
        print("  coverage     - Run tests with coverage report")
        print("  fast         - Run tests excluding slow ones")
        print("  install      - Install test dependencies")
        print("  clean        - Clean test artifacts")
        return 1
    
    command = sys.argv[1].lower()
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    if command == "install":
        return run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    elif command == "clean":
        # Remove test artifacts
        artifacts = [".coverage", "htmlcov", ".pytest_cache", "coverage.xml"]
        for artifact in artifacts:
            if os.path.exists(artifact):
                if os.path.isdir(artifact):
                    import shutil
                    shutil.rmtree(artifact)
                else:
                    os.remove(artifact)
                print(f"Removed {artifact}")
        return 0
    
    elif command == "all":
        return run_command([sys.executable, "-m", "pytest", "tests/"])
    
    elif command == "unit":
        return run_command([sys.executable, "-m", "pytest", "tests/unit/", "-m", "unit"])
    
    elif command == "integration":
        return run_command([sys.executable, "-m", "pytest", "tests/integration/", "-m", "integration"])
    
    elif command == "security": 
        return run_command([sys.executable, "-m", "pytest", "tests/security/", "-m", "security"])
    
    elif command == "coverage":
        return run_command([sys.executable, "-m", "pytest", "tests/", "--cov=src", "--cov-report=html", "--cov-report=term"])
    
    elif command == "fast":
        return run_command([sys.executable, "-m", "pytest", "tests/", "-m", "not slow"])
    
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
