"""
Response formatter for Ollama API results

Handles formatting and cleaning of tool execution results for user display.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formats tool execution results for clean user display"""
    
    @staticmethod
    def format_tool_result(tool_name: str, result: str) -> str:
        """
        Format tool results for clean output
        
        Args:
            tool_name: Name of the executed tool
            result: Raw result from tool execution
            
        Returns:
            Formatted result string
        """
        if tool_name == "create_file":
            # Extract filename from result
            if "created successfully" in result:
                filename = result.split("'")[1] if "'" in result else "file"
                return f"{filename} created successfully!"
            return result
            
        elif tool_name == "list_files":
            # Count files listed
            if "Found" in result:
                return result
            # Count lines to estimate number of files
            lines = result.count('\n')
            return f"{lines} files found"
            
        elif tool_name == "read_file":
            return "file content retrieved"
            
        elif tool_name == "delete_file":
            return result
            
        elif tool_name == "copy_file":
            return result
            
        elif tool_name == "search_files":
            return result
            
        elif tool_name == "write_to_file":
            if "written successfully" in result:
                return "Content written to file successfully!"
            return result
            
        elif tool_name == "write_json_file":
            if "JSON file" in result and "created successfully" in result:
                return "JSON file created successfully!"
            return result
            
        elif tool_name == "compress_file":
            if "compressed successfully" in result:
                return "Files compressed successfully!"
            return result
            
        elif tool_name == "extract_archive":
            if "extracted successfully" in result:
                return "Archive extracted successfully!"
            return result
            
        else:
            return result
    
    @staticmethod
    def format_error_message(error: Exception, context: str = "") -> str:
        """
        Format error messages for user display
        
        Args:
            error: Exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            Formatted error message
        """
        error_msg = str(error)
        
        # Common error patterns and user-friendly messages
        if "No such file or directory" in error_msg:
            return "❌ File not found. Please check the filename and try again."
        elif "Permission denied" in error_msg:
            return "❌ Permission denied. Check file permissions."
        elif "File exists" in error_msg:
            return "❌ File already exists. Use a different name or enable overwrite mode."
        elif "Invalid filename" in error_msg:
            return f"❌ Invalid filename: {error_msg}"
        elif "Path" in error_msg and "outside" in error_msg:
            return "❌ Path outside workspace directory not allowed for security."
        else:
            prefix = f"❌ Error in {context}: " if context else "❌ Error: "
            return f"{prefix}{error_msg}"
    
    @staticmethod
    def format_success_message(tool_name: str, details: Optional[Dict[str, Any]] = None) -> str:
        """
        Format success messages for tool operations
        
        Args:
            tool_name: Name of the tool that succeeded
            details: Optional details about the operation
            
        Returns:
            Formatted success message
        """
        messages = {
            "create_file": "✅ File created successfully!",
            "write_to_file": "✅ Content written to file!",
            "read_file": "✅ File content retrieved!",
            "delete_file": "✅ File deleted successfully!",
            "copy_file": "✅ File copied successfully!",
            "move_file": "✅ File moved successfully!",
            "create_folder": "✅ Folder created successfully!",
            "list_files": "✅ Files listed successfully!",
            "search_files": "✅ File search completed!",
            "compress_file": "✅ Files compressed successfully!",
            "extract_archive": "✅ Archive extracted successfully!",
            "write_json_file": "✅ JSON file created successfully!",
            "write_txt_file": "✅ Text file created successfully!",
            "write_md_file": "✅ Markdown file created successfully!"
        }
        
        base_message = messages.get(tool_name, f"✅ {tool_name} completed successfully!")
        
        if details:
            if "filename" in details:
                base_message += f" ({details['filename']})"
            elif "count" in details:
                base_message += f" ({details['count']} items)"
        
        return base_message
    
    @staticmethod
    def format_progress_message(operation: str, current: int, total: int) -> str:
        """
        Format progress messages for long-running operations
        
        Args:
            operation: Description of the operation
            current: Current progress count
            total: Total count
            
        Returns:
            Formatted progress message
        """
        percentage = int((current / total) * 100) if total > 0 else 0
        return f"🔄 {operation}: {current}/{total} ({percentage}%)"
    
    @staticmethod
    def format_debug_info(debug_data: Dict[str, Any]) -> str:
        """
        Format debug information for verbose output
        
        Args:
            debug_data: Dictionary containing debug information
            
        Returns:
            Formatted debug string
        """
        lines = ["🔍 Debug Information:"]
        
        if "intent" in debug_data:
            lines.append(f"  Intent: {debug_data['intent']}")
            
        if "intent_confidence" in debug_data:
            lines.append(f"  Intent Confidence: {debug_data['intent_confidence']:.2f}")
            
        if "selected_tool" in debug_data:
            lines.append(f"  Selected Tool: {debug_data['selected_tool']}")
            
        if "total_weight" in debug_data:
            lines.append(f"  Context Weight: {debug_data['total_weight']}")
            
        if "word_breakdown" in debug_data and debug_data['word_breakdown']:
            breakdown = ", ".join([f"{word}({weight})" for word, weight in debug_data['word_breakdown'].items()])
            lines.append(f"  Word Weights: {breakdown}")
        
        return "\n".join(lines)
