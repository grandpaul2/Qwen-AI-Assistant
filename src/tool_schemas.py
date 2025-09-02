"""
Tool schemas for WorkspaceAI file management functions

This module contains all the JSON schemas for tool calling functionality,
enabling the LLM to understand         # Validate schema structure
        for i, schema in enumerate(schemas):
            if not isinstance(schema, dict):
                raise WorkspaceAIError(f"Schema {i} must be a dictionary")
            if "type" not in schema or "function" not in schema:
                raise WorkspaceAIError(f"Schema {i} missing required 'type' or 'function' field")
        
        # Validate schemas can be JSON serialized (this will test json.dumps)
        try:
            # Create a test serialization to ensure schemas are JSON compatible
            serialized = json.dumps(schemas)
            if len(serialized) < 100:  # Should be much larger for real schemas
                raise Exception("Schema serialization seems invalid")
        except Exception as e:
            raise WorkspaceAIError(f"Schemas are not JSON serializable: {e}")
        
        logging.debug(f"Successfully generated {len(schemas)} tool schemas")
        return schemasrly use available file operations.

IMPORTANT FOR AI: Only use functions defined in this schema. Do not invent new function names.
Common function mapping:
- For copying files: use copy_file (not backup_files, duplicate_file, etc.)
- For creating any text file: use create_file (not create_csv_file, create_txt_file, etc.)
- For JSON data: use write_json_file (not create_json_file, save_json, etc.)
- For searching: use search_files (not find_files, locate_files, etc.)
"""

import logging
import json
from typing import List, Dict, Any
from .exceptions import WorkspaceAIError


def get_all_tool_schemas() -> List[Dict[str, Any]]:
    """Get tool schemas for all file management functions - backward compatible wrapper"""
    try:
        schemas = get_all_tool_schemas_with_exceptions()
        # If no schemas returned, use fallback instead of raising exception (wrapper behavior)
        if not schemas:
            logging.warning("Tool schemas empty, using fallback")
            return _get_fallback_schemas()
        return schemas
    except Exception as e:
        logging.error(f"Tool schema retrieval failed: {e}")
        print(f"Warning: Tool schema error: {str(e)}")
        # Return minimal schema to maintain functionality
        return _get_fallback_schemas()

def _get_fallback_schemas() -> List[Dict[str, Any]]:
    """Return fallback schemas when main function fails"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a new file with specified content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {"type": "string", "description": "Name of the file"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["file_name", "content"]
                }
            }
        }
    ]


def get_all_tool_schemas_with_exceptions() -> List[Dict[str, Any]]:
    """
    Build tool schemas for all file management functions.
    This is the exception-raising version.
    
    Returns:
        List of tool schema dictionaries
        
    Raises:
        WorkspaceAIError: If schema generation fails
    """
    try:
        # Define the complete tool schemas
        schemas = [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Create a new file with specified content. Use this for ANY file type including .csv, .txt, .py, .md, .json, etc. ALWAYS use this when user wants to create, write, make, save, or generate any kind of file, document, guide, or text content. Do NOT use create_csv_file, create_txt_file or similar - they don't exist.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_name": {
                                "type": "string",
                                "description": "Name of the file to create (e.g., 'guide.md', 'script.py', 'data.csv')"
                            },
                            "content": {
                                "type": "string", 
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["file_name", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_to_file",
                    "description": "Write content to a file (create new or overwrite existing)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_name": {
                                "type": "string",
                                "description": "Name of the file to write to"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["file_name", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_name": {
                                "type": "string",
                                "description": "Name of the file to read"
                            }
                        },
                        "required": ["file_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_name": {
                                "type": "string",
                                "description": "Name of the file to delete"
                            }
                        },
                        "required": ["file_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_install_commands",
                    "description": "Generate software installation commands. ONLY use when user explicitly asks for installation instructions, setup commands, or how to install software. DO NOT use for creating guides, documentation, or files about software.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "software": {
                                "type": "string",
                                "description": "Name of the software to generate installation commands for"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["auto", "package_manager", "official", "manual"],
                                "description": "Installation method preference (defaults to 'auto')"
                            }
                        },
                        "required": ["software"]
                    }
                }
            }
        ]
        
        # Validate that schemas is not empty
        if not schemas:
            raise WorkspaceAIError("Tool schemas cannot be empty")
            
        # Validate each schema has required structure
        for i, schema in enumerate(schemas):
            if not isinstance(schema, dict):
                raise WorkspaceAIError(f"Schema {i} must be a dictionary")
            if "type" not in schema or "function" not in schema:
                raise WorkspaceAIError(f"Schema {i} missing required 'type' or 'function' field")
        
        logging.debug(f"Successfully generated {len(schemas)} tool schemas")
        return schemas
        
    except Exception as e:
        error_msg = f"Failed to generate tool schemas: {str(e)}"
        logging.error(error_msg)
        raise WorkspaceAIError(error_msg) from e
