"""
Conversation Context Manager for WorkspaceAI

This module manages conversation context, session state, and provides
context-aware intelligence for improved user interaction.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from .exceptions import (
    WorkspaceAIError,
    MemoryError,
    ConversationError,
    handle_exception
)

logger = logging.getLogger(__name__)


@dataclass
class OperationInfo:
    """Information about a completed operation"""
    timestamp: float
    operation_type: str
    tool_name: str
    parameters: Dict[str, Any]
    result: str
    success: bool
    context_tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.context_tags is None:
            self.context_tags = []


@dataclass
class FileInfo:
    """Information about files in the workspace"""
    name: str
    path: str
    created_timestamp: float
    last_modified: float
    size_bytes: int
    file_type: str
    created_by_operation: Optional[str] = None
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ConversationSession:
    """Complete conversation session state"""
    session_id: str
    start_time: float
    last_activity: float
    operation_history: List[OperationInfo]
    file_state: Dict[str, FileInfo]
    user_patterns: Dict[str, Any]
    context_memory: Dict[str, Any]
    active_project: Optional[str] = None
    
    def __post_init__(self):
        if not self.operation_history:
            self.operation_history = []
        if not self.file_state:
            self.file_state = {}
        if not self.user_patterns:
            self.user_patterns = {}
        if not self.context_memory:
            self.context_memory = {}


class ConversationContext:
    """
    Manages conversation context and session state for enhanced AI interaction.
    
    Provides context-aware intelligence by tracking:
    - Operation history and patterns
    - File state and relationships
    - User preferences and patterns
    - Active projects and workflows
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize conversation context.
        
        Args:
            session_id: Optional session identifier
        """
        self.session_id = session_id or self._generate_session_id()
        self.session = ConversationSession(
            session_id=self.session_id,
            start_time=time.time(),
            last_activity=time.time(),
            operation_history=[],
            file_state={},
            user_patterns={},
            context_memory={}
        )
        
        logger.info(f"Initialized conversation context for session: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier"""
        import uuid
        return f"session_{int(time.time())}_{str(uuid.uuid4())[:8]}"
    
    def add_operation(
        self,
        operation_type: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: str,
        success: bool,
        context_tags: Optional[List[str]] = None
    ) -> None:
        """
        Record a completed operation in the context.
        
        Args:
            operation_type: Type of operation (e.g., 'file_creation', 'file_read')
            tool_name: Name of the tool used
            parameters: Parameters passed to the operation
            result: Result message or output
            success: Whether the operation succeeded
            context_tags: Optional tags for context categorization
        """
        try:
            operation = OperationInfo(
                timestamp=time.time(),
                operation_type=operation_type,
                tool_name=tool_name,
                parameters=parameters.copy() if parameters else {},
                result=result,
                success=success,
                context_tags=context_tags or []
            )
            
            self.session.operation_history.append(operation)
            self.session.last_activity = time.time()
            
            # Update user patterns based on successful operations
            if success:
                self._update_user_patterns(operation)
            
            # Update file state if this was a file operation
            self._update_file_state(operation)
            
            logger.debug(f"Added operation to context: {operation_type} with {tool_name}")
            
        except Exception as e:
            error = handle_exception("add_operation", e)
            error.context.update({
                "operation_type": operation_type,
                "tool_name": tool_name,
                "session_id": self.session_id
            })
            logger.error(f"Failed to add operation to context: {error}")
            raise error
    
    def _update_user_patterns(self, operation: OperationInfo) -> None:
        """Update user patterns based on successful operations"""
        try:
            patterns = self.session.user_patterns
            
            # Track tool usage frequency
            tool_usage = patterns.setdefault("tool_usage", {})
            tool_usage[operation.tool_name] = tool_usage.get(operation.tool_name, 0) + 1
            
            # Track operation type frequency
            op_types = patterns.setdefault("operation_types", {})
            op_types[operation.operation_type] = op_types.get(operation.operation_type, 0) + 1
            
            # Track parameter patterns
            param_patterns = patterns.setdefault("parameter_patterns", {})
            for param_name, param_value in operation.parameters.items():
                param_stats = param_patterns.setdefault(param_name, {"values": {}, "count": 0})
                param_stats["count"] += 1
                if isinstance(param_value, str) and len(param_value) < 100:
                    param_stats["values"][param_value] = param_stats["values"].get(param_value, 0) + 1
            
            # Track context tags
            if operation.context_tags:
                tag_usage = patterns.setdefault("context_tags", {})
                for tag in operation.context_tags:
                    tag_usage[tag] = tag_usage.get(tag, 0) + 1
                    
        except Exception as e:
            # Don't fail the main operation if pattern tracking fails
            logger.warning(f"Failed to update user patterns: {e}")
    
    def _update_file_state(self, operation: OperationInfo) -> None:
        """Update file state tracking based on operations"""
        try:
            # Track file operations
            if operation.tool_name in ['create_file', 'write_to_file', 'write_json_file']:
                file_name = operation.parameters.get('file_name') or operation.parameters.get('filename')
                if file_name:
                    # Create or update file info
                    file_info = FileInfo(
                        name=file_name,
                        path=file_name,  # Simplified - could be enhanced with full paths
                        created_timestamp=operation.timestamp,
                        last_modified=operation.timestamp,
                        size_bytes=len(str(operation.parameters.get('content', ''))),
                        file_type=self._detect_file_type(file_name),
                        created_by_operation=operation.operation_type,
                        tags=operation.context_tags.copy() if operation.context_tags else []
                    )
                    self.session.file_state[file_name] = file_info
                    
        except Exception as e:
            # Don't fail the main operation if file state tracking fails
            logger.warning(f"Failed to update file state: {e}")
    
    def _detect_file_type(self, filename: str) -> str:
        """Detect file type from filename"""
        if '.' not in filename:
            return 'unknown'
        
        extension = filename.split('.')[-1].lower()
        type_mapping = {
            'txt': 'text',
            'md': 'markdown',
            'py': 'python',
            'js': 'javascript',
            'json': 'json',
            'csv': 'csv',
            'xml': 'xml',
            'html': 'html',
            'css': 'css',
            'yaml': 'yaml',
            'yml': 'yaml'
        }
        return type_mapping.get(extension, 'text')
    
    def get_recent_operations(self, count: int = 5, operation_type: Optional[str] = None) -> List[OperationInfo]:
        """
        Get recent operations from the session history.
        
        Args:
            count: Number of recent operations to return
            operation_type: Optional filter by operation type
            
        Returns:
            List of recent operations
        """
        try:
            operations = self.session.operation_history
            
            if operation_type:
                operations = [op for op in operations if op.operation_type == operation_type]
            
            # Return most recent operations
            return operations[-count:] if len(operations) >= count else operations
            
        except Exception as e:
            error = handle_exception("get_recent_operations", e)
            error.context.update({
                "count": count,
                "operation_type": operation_type,
                "session_id": self.session_id
            })
            logger.error(f"Failed to get recent operations: {error}")
            raise error
    
    def get_files_by_pattern(self, pattern: str) -> List[FileInfo]:
        """
        Get files matching a pattern or context.
        
        Args:
            pattern: Pattern to match against file names or tags
            
        Returns:
            List of matching files
        """
        try:
            pattern_lower = pattern.lower()
            matching_files = []
            
            for file_info in self.session.file_state.values():
                # Check filename match
                if pattern_lower in file_info.name.lower():
                    matching_files.append(file_info)
                    continue
                
                # Check tags match
                if any(pattern_lower in tag.lower() for tag in (file_info.tags or [])):
                    matching_files.append(file_info)
                    continue
                    
                # Check file type match
                if pattern_lower == file_info.file_type.lower():
                    matching_files.append(file_info)
            
            return matching_files
            
        except Exception as e:
            error = handle_exception("get_files_by_pattern", e)
            error.context.update({
                "pattern": pattern,
                "session_id": self.session_id
            })
            logger.error(f"Failed to get files by pattern: {error}")
            raise error
    
    def get_context_for_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Get relevant context for intent classification.
        
        Args:
            user_input: The user's input
            
        Returns:
            Dictionary with relevant context information
        """
        try:
            context = {
                "session_id": self.session_id,
                "recent_operations": [],
                "recent_files": [],
                "user_patterns": {},
                "active_project": self.session.active_project,
                "input_analysis": {}
            }
            
            # Get recent operations for context
            recent_ops = self.get_recent_operations(3)
            context["recent_operations"] = [
                {
                    "type": op.operation_type,
                    "tool": op.tool_name,
                    "success": op.success,
                    "timestamp": op.timestamp
                }
                for op in recent_ops
            ]
            
            # Get recent files
            recent_files = sorted(
                self.session.file_state.values(),
                key=lambda f: f.last_modified,
                reverse=True
            )[:5]
            
            context["recent_files"] = [
                {
                    "name": f.name,
                    "type": f.file_type,
                    "created": f.created_timestamp,
                    "tags": f.tags
                }
                for f in recent_files
            ]
            
            # Include relevant user patterns
            patterns = self.session.user_patterns
            context["user_patterns"] = {
                "preferred_tools": self._get_preferred_tools(patterns),
                "common_operations": self._get_common_operations(patterns),
                "recent_context_tags": self._get_recent_context_tags()
            }
            
            # Analyze input for context clues
            context["input_analysis"] = self._analyze_input_for_context(user_input)
            
            return context
            
        except Exception as e:
            error = handle_exception("get_context_for_intent", e)
            error.context.update({
                "user_input": user_input[:100] if user_input else None,
                "session_id": self.session_id
            })
            logger.error(f"Failed to get context for intent: {error}")
            # Return minimal context to avoid breaking the flow
            return {
                "session_id": self.session_id,
                "recent_operations": [],
                "recent_files": [],
                "user_patterns": {},
                "active_project": None,
                "input_analysis": {},
                "error": str(error)
            }
    
    def _get_preferred_tools(self, patterns: Dict[str, Any]) -> List[str]:
        """Get user's preferred tools based on usage patterns"""
        tool_usage = patterns.get("tool_usage", {})
        if not tool_usage:
            return []
        
        # Sort by usage frequency
        sorted_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
        return [tool for tool, count in sorted_tools[:3]]  # Top 3 preferred tools
    
    def _get_common_operations(self, patterns: Dict[str, Any]) -> List[str]:
        """Get user's common operation types"""
        op_types = patterns.get("operation_types", {})
        if not op_types:
            return []
        
        sorted_ops = sorted(op_types.items(), key=lambda x: x[1], reverse=True)
        return [op for op, count in sorted_ops[:3]]  # Top 3 operation types
    
    def _get_recent_context_tags(self) -> List[str]:
        """Get recent context tags from operations"""
        recent_ops = self.get_recent_operations(10)
        tag_counts = {}
        
        for op in recent_ops:
            for tag in (op.context_tags or []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Return most frequent recent tags
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags[:5]]
    
    def _analyze_input_for_context(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input for context clues"""
        if not user_input:
            return {}
        
        input_lower = user_input.lower()
        analysis = {
            "references_previous": False,
            "mentions_files": [],
            "suggests_continuation": False,
            "indicates_new_project": False
        }
        
        # Check for references to previous work
        previous_indicators = [
            "the file", "that file", "previous", "earlier", "before",
            "we created", "we made", "we built", "last time"
        ]
        analysis["references_previous"] = any(indicator in input_lower for indicator in previous_indicators)
        
        # Look for file mentions
        import re
        file_patterns = [
            r'\b\w+\.\w+\b',  # filename.extension
            r'\b(file|document|script|guide)\b'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, input_lower)
            if matches:
                analysis["mentions_files"].extend(matches)
        
        # Check for continuation indicators
        continuation_indicators = [
            "continue", "next", "also", "then", "after that",
            "add to", "update", "modify", "extend"
        ]
        analysis["suggests_continuation"] = any(indicator in input_lower for indicator in continuation_indicators)
        
        # Check for new project indicators
        new_project_indicators = [
            "new project", "start fresh", "create project",
            "build something new", "new workspace"
        ]
        analysis["indicates_new_project"] = any(indicator in input_lower for indicator in new_project_indicators)
        
        return analysis
    
    def set_active_project(self, project_name: str) -> None:
        """Set the active project context"""
        try:
            self.session.active_project = project_name
            self.session.last_activity = time.time()
            logger.info(f"Set active project to: {project_name}")
            
        except Exception as e:
            error = handle_exception("set_active_project", e)
            error.context.update({
                "project_name": project_name,
                "session_id": self.session_id
            })
            logger.error(f"Failed to set active project: {error}")
            raise error
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session"""
        try:
            return {
                "session_id": self.session_id,
                "duration_minutes": (time.time() - self.session.start_time) / 60,
                "total_operations": len(self.session.operation_history),
                "successful_operations": sum(1 for op in self.session.operation_history if op.success),
                "files_created": len(self.session.file_state),
                "active_project": self.session.active_project,
                "preferred_tools": self._get_preferred_tools(self.session.user_patterns),
                "last_activity": self.session.last_activity
            }
            
        except Exception as e:
            error = handle_exception("get_session_summary", e)
            error.context["session_id"] = self.session_id
            logger.error(f"Failed to get session summary: {error}")
            raise error


# Global context instance for the application
conversation_context = ConversationContext()


def get_conversation_context() -> ConversationContext:
    """Get the global conversation context instance"""
    return conversation_context


def reset_conversation_context() -> ConversationContext:
    """Reset the conversation context to a new session"""
    global conversation_context
    conversation_context = ConversationContext()
    logger.info("Reset conversation context to new session")
    return conversation_context
