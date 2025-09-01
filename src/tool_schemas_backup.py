"""
Tool schemas for WorkspaceAI file management functions

This module contains all the JSON schemas for tool calling functionality,
enabling the LLM to understand and properly use available file operations.

IMPORTANT FOR AI: Only use functions defined in this schema. Do not invent new function names.
Common function mapping:
- For copying files: use copy_file (not backup_files, duplicate_file, etc.)
- For creating any text file: use create_file (not create_csv_file, create_txt_file, etc.)
- For JSON data: use write_json_file (not create_json_file, save_json, etc.)
- For searching: use search_files (not find_files, locate_files, etc.)
"""

import logging
from typing import List, Dict, Any
from .exceptions import WorkspaceAIError


def get_all_tool_schemas() -> List[Dict[str, Any]]:
    """Get tool schemas for all file management functions - backward compatible wrapper"""
    try:
        return get_all_tool_schemas_with_exceptions()
    except Exception as e:
        logging.error(f"Tool schema retrieval failed: {e}")
        print(f"Warning: Tool schema error: {str(e)}")
        # Return minimal schema to maintain functionality
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
                "name": "create_folder",
                "description": "Create a new folder/directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder_name": {
                            "type": "string",
                            "description": "Name of the folder to create"
                        }
                    },
                    "required": ["folder_name"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "list_files",
                "description": "List files and folders in current directory or specified subdirectory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subdirectory": {
                            "type": "string",
                            "description": "Subdirectory to list (optional, defaults to workspace root)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search for files by keyword in workspace. Use this for finding files, locating files, listing files by pattern, etc. Do NOT use find_files, locate_files or similar - they don't exist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Keyword to search for in filenames"
                        },
                        "subdirectory": {
                            "type": "string",
                            "description": "Subdirectory to search in (optional, defaults to workspace root)"
                        }
                    },
                    "required": ["keyword"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "copy_file",
                "description": "Copy a file to a new location. Use this for backups, duplicates, etc. Do NOT use backup_files, duplicate_file or similar - they don't exist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "src_file": {
                            "type": "string",
                            "description": "Source file to copy"
                        },
                        "dest_file": {
                            "type": "string",
                            "description": "Destination path for the copy"
                        }
                    },
                    "required": ["src_file", "dest_file"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "move_file",
                "description": "Move or rename a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source file to move"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination path"
                        }
                    },
                    "required": ["source", "destination"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compress_file",
                "description": "Compress files or folders into a zip archive",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "File or folder to compress"
                        },
                        "archive_name": {
                            "type": "string",
                            "description": "Name of the zip archive to create (optional)"
                        }
                    },
                    "required": ["source"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "extract_archive",
                "description": "Extract a zip archive",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "archive_name": {
                            "type": "string",
                            "description": "Name of the archive to extract"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination folder (optional, defaults to current directory)"
                        }
                    },
                    "required": ["archive_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "backup_files",
                "description": "Create a backup of specified files or folders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "File or folder to backup"
                        },
                        "backup_name": {
                            "type": "string",
                            "description": "Name for the backup (optional)"
                        }
                    },
                    "required": ["source"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_file_info",
                "description": "Get detailed information about a file or folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File or folder path to get info about"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_json_file",
                "description": "Create a JSON file from dictionary data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "Name of the JSON file to create"
                        },
                        "content": {
                            "type": "object",
                            "description": "Dictionary data to save as JSON"
                        }
                    },
                    "required": ["file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_json_file",
                "description": "Read and parse a JSON file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the JSON file to read"
                        }
                    },
                    "required": ["filename"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_csv_file",
                "description": "Create a CSV file from list data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the CSV file to create"
                        },
                        "data": {
                            "type": "array",
                            "description": "List of rows (each row is a list of values)"
                        },
                        "headers": {
                            "type": "array",
                            "description": "List of column headers (optional)",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["filename", "data"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_csv_file",
                "description": "Read a CSV file and return as list of dictionaries",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the CSV file to read"
                        }
                    },
                    "required": ["filename"]
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
            },
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