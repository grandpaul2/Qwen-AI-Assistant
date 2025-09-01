#!/usr/bin/env python3
"""
Sample Python script for testing purposes

This script demonstrates various Python features and
is used in WorkspaceAI file management tests.
"""

import os
import sys
from typing import List, Dict, Any


def hello_world() -> str:
    """Return a greeting message"""
    return "Hello, World!"


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


def process_data(data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Process a list of data dictionaries"""
    result = {}
    for item in data:
        if 'name' in item and 'value' in item:
            result[item['name']] = item['value']
    return result


class TestClass:
    """A simple test class"""
    
    def __init__(self, name: str):
        self.name = name
        self.data = []
    
    def add_data(self, item: Any) -> None:
        """Add data to the internal list"""
        self.data.append(item)
    
    def get_data(self) -> List[Any]:
        """Get all stored data"""
        return self.data.copy()


if __name__ == "__main__":
    print(hello_world())
    print(f"2 + 3 = {add_numbers(2, 3)}")
    
    test_obj = TestClass("test")
    test_obj.add_data("sample")
    print(f"Test object data: {test_obj.get_data()}")
