"""
Response Intelligence Module for WorkspaceAI

This module provides intelligent, context-aware response generation that makes
interactions more helpful, conversational, and informative.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .exceptions import (
    WorkspaceAIError,
    handle_exception
)

logger = logging.getLogger(__name__)


@dataclass
class OperationStep:
    """Represents a single step in a multi-step operation"""
    step_number: int
    tool_name: str
    description: str
    parameters: Dict[str, Any]
    estimated_time: float = 1.0
    dependencies: Optional[List[int]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ResponseContext:
    """Context information for response generation"""
    operation_type: str
    success: bool
    result: Any
    execution_time: float
    user_input: str
    conversation_context: Optional[Dict[str, Any]] = None
    operation_steps: Optional[List[OperationStep]] = None
    error_details: Optional[str] = None
    
    def __post_init__(self):
        if self.operation_steps is None:
            self.operation_steps = []


class ResponseIntelligence:
    """
    Generates intelligent, context-aware responses for WorkspaceAI operations.
    
    This class enhances user experience by providing:
    - Contextual response generation
    - Step-by-step operation explanations
    - Progress updates for multi-step operations
    - Proactive suggestions and guidance
    """
    
    def __init__(self):
        """Initialize the response intelligence system"""
        self.response_templates = self._load_response_templates()
        self.suggestion_engine = SuggestionEngine()
        
    def generate_contextual_response(
        self, 
        response_context: ResponseContext
    ) -> str:
        """
        Generate an intelligent, contextual response for an operation.
        
        Args:
            response_context: Context information about the operation
            
        Returns:
            Contextual response string
        """
        try:
            return self._generate_contextual_response_with_exceptions(response_context)
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            # Fallback to basic response
            if response_context.success:
                return f"✅ Operation completed successfully."
            else:
                return f"❌ Operation failed: {response_context.error_details or 'Unknown error'}"
    
    def _generate_contextual_response_with_exceptions(
        self, 
        response_context: ResponseContext
    ) -> str:
        """
        Generate contextual response with proper error handling.
        
        Args:
            response_context: Context information about the operation
            
        Returns:
            Contextual response string
            
        Raises:
            WorkspaceAIError: If response generation fails
        """
        if not isinstance(response_context, ResponseContext):
            error = WorkspaceAIError("Invalid response context")
            error.context["context_type"] = type(response_context).__name__
            raise error
        
        # Determine response strategy
        if response_context.success:
            return self._generate_success_response(response_context)
        else:
            return self._generate_error_response(response_context)
    
    def _generate_success_response(self, context: ResponseContext) -> str:
        """Generate response for successful operations"""
        response_parts = []
        
        # Add success indicator with context
        success_message = self._get_success_message(context.operation_type)
        response_parts.append(success_message)
        
        # Add operation details
        if context.result:
            details = self._format_operation_details(context)
            if details:
                response_parts.append(details)
        
        # Add multi-step explanation if applicable
        if context.operation_steps and len(context.operation_steps) > 1:
            steps_explanation = self._explain_operation_steps(context.operation_steps)
            response_parts.append(f"\n📋 Operation completed in {len(context.operation_steps)} steps:\n{steps_explanation}")
        
        # Add performance info if significant
        if context.execution_time > 1.0:
            response_parts.append(f"⏱️ Completed in {context.execution_time:.1f}s")
        
        # Add contextual suggestions
        suggestions = self._get_contextual_suggestions(context)
        if suggestions:
            response_parts.append(f"\n💡 {suggestions}")
        
        return "\n".join(response_parts)
    
    def _generate_error_response(self, context: ResponseContext) -> str:
        """Generate response for failed operations"""
        response_parts = []
        
        # Add error indicator
        response_parts.append("❌ Operation failed")
        
        # Add error details with context
        if context.error_details:
            error_explanation = self._explain_error_with_context(
                context.error_details, context.operation_type, context.user_input
            )
            response_parts.append(f"🔍 {error_explanation}")
        
        # Add recovery suggestions
        recovery_suggestions = self._get_recovery_suggestions(context)
        if recovery_suggestions:
            response_parts.append(f"\n🔧 Suggestions:\n{recovery_suggestions}")
        
        # Add alternative actions
        alternatives = self._suggest_alternative_actions(context)
        if alternatives:
            response_parts.append(f"\n🔄 You could try:\n{alternatives}")
        
        return "\n".join(response_parts)
    
    def _get_success_message(self, operation_type: str) -> str:
        """Get contextual success message based on operation type"""
        success_messages = {
            "file_creation": "✅ File created successfully",
            "file_modification": "✅ File updated successfully", 
            "file_deletion": "✅ File deleted successfully",
            "folder_creation": "✅ Folder created successfully",
            "multi_step": "✅ Multi-step operation completed successfully",
            "project_setup": "✅ Project structure created successfully",
            "content_generation": "✅ Content generated successfully",
            "search_operation": "✅ Search completed successfully",
            "llm_request": "✅ Request processed successfully"
        }
        
        return success_messages.get(operation_type, "✅ Operation completed successfully")
    
    def _format_operation_details(self, context: ResponseContext) -> Optional[str]:
        """Format operation-specific details"""
        operation_type = context.operation_type
        result = context.result
        
        if operation_type == "file_creation" and isinstance(result, dict):
            file_name = result.get("file_name", "Unknown")
            file_size = result.get("file_size", 0)
            return f"📄 Created: {file_name} ({file_size} bytes)"
        
        elif operation_type == "folder_creation" and isinstance(result, dict):
            folder_name = result.get("folder_name", "Unknown")
            return f"📁 Created: {folder_name}"
        
        elif operation_type == "search_operation" and isinstance(result, dict):
            matches = result.get("matches", 0)
            return f"🔍 Found {matches} matches"
        
        elif operation_type == "content_generation" and isinstance(result, str):
            word_count = len(result.split())
            return f"📝 Generated {word_count} words"
        
        return None
    
    def _explain_operation_steps(self, steps: List[OperationStep]) -> str:
        """Generate explanation of operation steps"""
        step_lines = []
        for step in steps:
            step_lines.append(f"   {step.step_number}. {step.description}")
        return "\n".join(step_lines)
    
    def _explain_error_with_context(
        self, 
        error_details: str, 
        operation_type: str, 
        user_input: str
    ) -> str:
        """Provide contextual error explanation"""
        # Common error patterns and explanations
        error_explanations = {
            "file not found": "The file you're trying to access doesn't exist or has been moved",
            "permission denied": "You don't have permission to perform this operation on the file/folder",
            "file already exists": "A file with this name already exists in the location",
            "invalid path": "The file path contains invalid characters or doesn't exist",
            "disk full": "There's not enough disk space to complete this operation",
            "timeout": "The operation took too long and was cancelled"
        }
        
        # Check for known error patterns
        error_lower = error_details.lower()
        for pattern, explanation in error_explanations.items():
            if pattern in error_lower:
                return f"{explanation}. {error_details}"
        
        # Provide operation-specific context
        if operation_type == "file_creation":
            return f"Failed to create file. {error_details}"
        elif operation_type == "file_modification":
            return f"Failed to update file. {error_details}"
        else:
            return error_details
    
    def _get_recovery_suggestions(self, context: ResponseContext) -> Optional[str]:
        """Generate recovery suggestions based on error context"""
        if not context.error_details:
            return None
        
        error_lower = context.error_details.lower()
        suggestions = []
        
        if "file not found" in error_lower:
            suggestions.append("• Check if the file path is correct")
            suggestions.append("• Verify the file hasn't been moved or deleted")
            suggestions.append("• Try listing files in the directory first")
        
        elif "permission denied" in error_lower:
            suggestions.append("• Check if the file is open in another program")
            suggestions.append("• Verify you have write permissions for this location")
            suggestions.append("• Try running as administrator if needed")
        
        elif "file already exists" in error_lower:
            suggestions.append("• Choose a different filename")
            suggestions.append("• Delete the existing file first (if intended)")
            suggestions.append("• Use append mode to add to existing file")
        
        elif "invalid path" in error_lower:
            suggestions.append("• Remove special characters from the path")
            suggestions.append("• Ensure all directory names are valid")
            suggestions.append("• Check path length (Windows has 260 character limit)")
        
        return "\n".join(suggestions) if suggestions else None
    
    def _suggest_alternative_actions(self, context: ResponseContext) -> Optional[str]:
        """Suggest alternative actions based on failed operation"""
        operation_type = context.operation_type
        alternatives = []
        
        if operation_type == "file_creation":
            alternatives.append("• Create the file in a different location")
            alternatives.append("• Try a different filename")
            alternatives.append("• Create the directory first if it doesn't exist")
        
        elif operation_type == "file_modification":
            alternatives.append("• Create a new file with the content")
            alternatives.append("• Check if the file is read-only")
            alternatives.append("• Try opening the file first to verify it exists")
        
        elif operation_type == "search_operation":
            alternatives.append("• Try different search terms")
            alternatives.append("• Search in a different directory")
            alternatives.append("• Use case-insensitive search")
        
        return "\n".join(alternatives) if alternatives else None
    
    def _get_contextual_suggestions(self, context: ResponseContext) -> Optional[str]:
        """Get proactive suggestions based on successful operation"""
        return self.suggestion_engine.get_next_action_suggestions(context)
    
    def explain_multi_step_operation(self, operation_plan: List[OperationStep]) -> str:
        """
        Generate explanation for a planned multi-step operation.
        
        Args:
            operation_plan: List of operation steps
            
        Returns:
            Formatted explanation of the operation plan
        """
        if not operation_plan:
            return "No operation steps planned."
        
        explanation_parts = [
            f"📋 Planning {len(operation_plan)}-step operation:"
        ]
        
        total_time = sum(step.estimated_time for step in operation_plan)
        if total_time > 5.0:
            explanation_parts.append(f"⏱️ Estimated time: {total_time:.1f} seconds")
        
        explanation_parts.append("")
        
        for step in operation_plan:
            step_line = f"   {step.step_number}. {step.description}"
            if step.dependencies:
                deps = ", ".join(f"step {d}" for d in step.dependencies)
                step_line += f" (after {deps})"
            explanation_parts.append(step_line)
        
        return "\n".join(explanation_parts)
    
    def generate_progress_update(
        self, 
        current_step: int, 
        total_steps: int, 
        current_operation: str
    ) -> str:
        """
        Generate progress update for multi-step operations.
        
        Args:
            current_step: Current step number (1-based)
            total_steps: Total number of steps
            current_operation: Description of current operation
            
        Returns:
            Progress update message
        """
        progress_percent = (current_step / total_steps) * 100
        progress_bar = self._generate_progress_bar(progress_percent)
        
        return f"🔄 Step {current_step}/{total_steps}: {current_operation}\n{progress_bar}"
    
    def _generate_progress_bar(self, percent: float, width: int = 20) -> str:
        """Generate a text-based progress bar"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percent:.1f}%"
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Load response templates for different scenarios"""
        return {
            "file_created": "✅ Successfully created {filename}",
            "file_updated": "✅ Successfully updated {filename}",
            "folder_created": "✅ Successfully created folder {foldername}",
            "search_completed": "🔍 Found {count} matches for '{query}'",
            "operation_failed": "❌ {operation} failed: {error}",
            "multi_step_started": "🚀 Starting {step_count}-step operation",
            "multi_step_completed": "✅ Completed all {step_count} steps successfully"
        }


class SuggestionEngine:
    """
    Generates intelligent suggestions for next actions based on context.
    """
    
    def __init__(self):
        """Initialize the suggestion engine"""
        self.suggestion_rules = self._load_suggestion_rules()
    
    def get_next_action_suggestions(self, context: ResponseContext) -> Optional[str]:
        """
        Generate suggestions for next actions based on operation context.
        
        Args:
            context: Response context from completed operation
            
        Returns:
            Suggestion string or None if no suggestions
        """
        operation_type = context.operation_type
        suggestions = []
        
        # File creation suggestions
        if operation_type == "file_creation":
            suggestions.extend([
                "Add content to your new file",
                "Create additional files for your project",
                "Set up a folder structure if needed"
            ])
        
        # File modification suggestions
        elif operation_type == "file_modification":
            suggestions.extend([
                "Review the changes you made",
                "Create a backup of the modified file",
                "Test the updated file if it's code"
            ])
        
        # Folder creation suggestions
        elif operation_type == "folder_creation":
            suggestions.extend([
                "Create files in your new folder",
                "Organize existing files into the folder",
                "Set up additional subfolders if needed"
            ])
        
        # Search operation suggestions
        elif operation_type == "search_operation":
            suggestions.extend([
                "Open one of the found files",
                "Refine your search with different terms",
                "Create a new file if you didn't find what you need"
            ])
        
        # Project setup suggestions
        elif operation_type == "project_setup":
            suggestions.extend([
                "Initialize version control (git)",
                "Create a README file",
                "Set up your development environment"
            ])
        
        if not suggestions:
            return None
        
        # Limit to top 2-3 suggestions
        top_suggestions = suggestions[:3]
        suggestion_lines = [f"• {suggestion}" for suggestion in top_suggestions]
        return "\n".join(suggestion_lines)
    
    def _load_suggestion_rules(self) -> Dict[str, List[str]]:
        """Load rules for generating contextual suggestions"""
        return {
            "after_file_creation": [
                "Add content to the file",
                "Create related files",
                "Organize into folders"
            ],
            "after_folder_creation": [
                "Create files in the folder", 
                "Set up subfolders",
                "Move existing files"
            ],
            "after_search": [
                "Open found files",
                "Refine search terms",
                "Create new file if needed"
            ]
        }


# Utility functions for response formatting
def format_file_list(files: List[str], max_display: int = 5) -> str:
    """Format a list of files for display"""
    if not files:
        return "No files found"
    
    if len(files) <= max_display:
        return "\n".join(f"📄 {file}" for file in files)
    else:
        displayed = files[:max_display]
        remaining = len(files) - max_display
        result = "\n".join(f"📄 {file}" for file in displayed)
        result += f"\n... and {remaining} more files"
        return result


def format_operation_summary(
    operations: List[Dict[str, Any]], 
    max_display: int = 3
) -> str:
    """Format a summary of recent operations"""
    if not operations:
        return "No recent operations"
    
    summary_lines = []
    for i, op in enumerate(operations[:max_display]):
        timestamp = op.get("timestamp", time.time())
        operation = op.get("operation_type", "unknown")
        success = op.get("success", False)
        
        status = "✅" if success else "❌"
        summary_lines.append(f"{status} {operation}")
    
    if len(operations) > max_display:
        remaining = len(operations) - max_display
        summary_lines.append(f"... and {remaining} more operations")
    
    return "\n".join(summary_lines)


def format_execution_time(seconds: float) -> str:
    """Format execution time in a human-readable way"""
    if seconds < 0.001:
        return "< 1ms"
    elif seconds < 1.0:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
