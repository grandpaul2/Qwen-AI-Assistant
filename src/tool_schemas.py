"""
Tool schemas for WorkspaceAI file management functions

This module contains all the JSON schemas for tool calling functionality,
enabling the LLM to understand and properly use available file operations.
"""

def get_all_tool_schemas():
    """Build tool schemas for all file management functions"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a new file with the specified content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to create (e.g., 'example.txt', 'script.py')"
                        },
                        "content": {
                            "type": "string", 
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["filename", "content"]
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
                "name": "append_file",
                "description": "Append content to an existing file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to append to"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to append to the file"
                        }
                    },
                    "required": ["filename", "content"]
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
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to delete"
                        }
                    },
                    "required": ["filename"]
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
                "description": "List files and folders in current directory or specified folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder": {
                            "type": "string",
                            "description": "Folder to list (optional, defaults to current directory)"
                        },
                        "show_hidden": {
                            "type": "boolean",
                            "description": "Show hidden files (optional, defaults to false)"
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
                "description": "Search for files by name pattern or content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern (filename or content to search for)"
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["name", "content"],
                            "description": "Type of search: 'name' for filename search, 'content' for text within files"
                        },
                        "folder": {
                            "type": "string",
                            "description": "Folder to search in (optional, defaults to current directory)"
                        }
                    },
                    "required": ["pattern", "search_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "copy_file",
                "description": "Copy a file to a new location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source file to copy"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination path for the copy"
                        }
                    },
                    "required": ["source", "destination"]
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
                "description": "Generate installation commands for popular software (cross-platform)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "software": {
                            "type": "string",
                            "description": "Name of the software to install (e.g., 'python', 'nodejs', 'git', 'docker', 'vscode')"
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
