"""
Custom Exception Classes for WorkspaceAI

This module defines a hierarchy of custom exceptions for better error handling,
categorization, and user experience across the WorkspaceAI application.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WorkspaceAIError(Exception):
    """
    Base exception class for all WorkspaceAI-related errors.
    
    Provides common functionality for error logging, context, and user-friendly messages.
    """
    
    def __init__(
        self, 
        message: str, 
        user_message: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize WorkspaceAI error.
        
        Args:
            message: Technical error message for developers/logs
            user_message: User-friendly message for display
            error_code: Unique error code for tracking
            context: Additional context information
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message
        self.error_code = error_code
        self.context = context or {}
        self.original_error = original_error
        
        # Log the error when created
        self._log_error()
    
    def _log_error(self):
        """Log the error with appropriate level and context."""
        log_message = f"{self.__class__.__name__}: {self.message}"
        if self.context:
            log_message += f" | Context: {self.context}"
        if self.original_error:
            log_message += f" | Caused by: {self.original_error}"
            
        logger.error(log_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "user_message": self.user_message,
            "error_code": self.error_code,
            "context": self.context
        }


# === Configuration Errors ===

class ConfigurationError(WorkspaceAIError):
    """Errors related to application configuration."""
    pass


class ConfigFileError(ConfigurationError):
    """Errors related to config file operations."""
    pass


class ConfigValidationError(ConfigurationError):
    """Errors related to config validation."""
    pass


# === Connection & Network Errors ===

class ConnectionError(WorkspaceAIError):
    """Base class for connection-related errors."""
    pass


class OllamaConnectionError(ConnectionError):
    """Errors connecting to Ollama service."""
    
    def __init__(self, message: str, host: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.host = host
        if host:
            self.context["host"] = host


class NetworkTimeoutError(ConnectionError):
    """Network timeout errors."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            self.context["timeout_seconds"] = timeout_seconds


class ServiceUnavailableError(ConnectionError):
    """Service unavailable errors."""
    pass


# === File System Errors ===

class FileSystemError(WorkspaceAIError):
    """Base class for file system related errors."""
    pass


class WorkspaceSecurityError(FileSystemError):
    """Errors related to workspace security violations."""
    
    def __init__(self, message: str, attempted_path: Optional[str] = None, **kwargs):
        user_message = "Access denied: Operation outside workspace boundaries"
        super().__init__(message, user_message=user_message, **kwargs)
        self.attempted_path = attempted_path
        if attempted_path:
            self.context["attempted_path"] = attempted_path


class FileNotFoundError(FileSystemError):
    """File or directory not found errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        if file_path:
            self.context["file_path"] = file_path


class FilePermissionError(FileSystemError):
    """File permission errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None, **kwargs):
        user_message = f"Permission denied for {operation or 'operation'}"
        super().__init__(message, user_message=user_message, **kwargs)
        self.file_path = file_path
        self.operation = operation
        if file_path:
            self.context["file_path"] = file_path
        if operation:
            self.context["operation"] = operation


class FileAlreadyExistsError(FileSystemError):
    """File already exists errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        user_message = "File already exists"
        super().__init__(message, user_message=user_message, **kwargs)
        self.file_path = file_path
        if file_path:
            self.context["file_path"] = file_path


# === Tool Execution Errors ===

class ToolExecutionError(WorkspaceAIError):
    """Base class for tool execution errors."""
    pass


class ToolNotFoundError(ToolExecutionError):
    """Tool or function not found errors."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, **kwargs):
        user_message = f"Unknown tool: {tool_name}" if tool_name else "Tool not found"
        super().__init__(message, user_message=user_message, **kwargs)
        self.tool_name = tool_name
        if tool_name:
            self.context["tool_name"] = tool_name


class ToolParameterError(ToolExecutionError):
    """Tool parameter validation errors."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, invalid_params: Optional[list] = None, **kwargs):
        # Use custom user message if provided, otherwise default
        if 'user_message' not in kwargs:
            kwargs['user_message'] = "Invalid parameters provided"
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        self.invalid_params = invalid_params or []
        if tool_name:
            self.context["tool_name"] = tool_name
        if invalid_params:
            self.context["invalid_params"] = invalid_params


class ToolTimeoutError(ToolExecutionError):
    """Tool execution timeout errors."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, timeout_seconds: Optional[float] = None, **kwargs):
        user_message = "Operation timed out"
        super().__init__(message, user_message=user_message, **kwargs)
        self.tool_name = tool_name
        self.timeout_seconds = timeout_seconds
        if tool_name:
            self.context["tool_name"] = tool_name
        if timeout_seconds:
            self.context["timeout_seconds"] = timeout_seconds


# === AI/LLM Errors ===

class AIError(WorkspaceAIError):
    """Base class for AI/LLM related errors."""
    pass


class ModelError(AIError):
    """Model-related errors."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        if model_name:
            self.context["model_name"] = model_name


class ResponseParsingError(AIError):
    """Errors parsing AI responses."""
    
    def __init__(self, message: str, response_content: Optional[str] = None, **kwargs):
        user_message = "Failed to understand AI response"
        super().__init__(message, user_message=user_message, **kwargs)
        self.response_content = response_content
        if response_content:
            self.context["response_content"] = response_content[:200] + "..." if len(response_content) > 200 else response_content


class TokenLimitError(AIError):
    """Token limit exceeded errors."""
    
    def __init__(self, message: str, token_count: Optional[int] = None, limit: Optional[int] = None, **kwargs):
        user_message = "Content too long for processing"
        super().__init__(message, user_message=user_message, **kwargs)
        self.token_count = token_count
        self.limit = limit
        if token_count:
            self.context["token_count"] = token_count
        if limit:
            self.context["limit"] = limit


# === Memory & Storage Errors ===

class MemoryError(WorkspaceAIError):
    """Base class for memory/storage related errors."""
    pass


class ConversationError(MemoryError):
    """Conversation management errors."""
    pass


class MemoryCorruptionError(MemoryError):
    """Memory corruption or invalid data errors."""
    
    def __init__(self, message: str, **kwargs):
        user_message = "Memory data corrupted, starting fresh"
        super().__init__(message, user_message=user_message, **kwargs)


# === Software Installation Errors ===

class InstallationError(WorkspaceAIError):
    """Base class for software installation errors."""
    pass


class UnsupportedPlatformError(InstallationError):
    """Unsupported platform errors."""
    
    def __init__(self, message: str, platform: Optional[str] = None, software: Optional[str] = None, **kwargs):
        user_message = f"Unsupported platform for {software}" if software else "Unsupported platform"
        super().__init__(message, user_message=user_message, **kwargs)
        self.platform = platform
        self.software = software
        if platform:
            self.context["platform"] = platform
        if software:
            self.context["software"] = software


class PackageManagerError(InstallationError):
    """Package manager related errors."""
    
    def __init__(self, message: str, package_manager: Optional[str] = None, **kwargs):
        user_message = "Package manager operation failed"
        super().__init__(message, user_message=user_message, **kwargs)
        self.package_manager = package_manager
        if package_manager:
            self.context["package_manager"] = package_manager


# === Intent Classification Errors ===

class IntentError(WorkspaceAIError):
    """Base class for intent classification errors."""
    pass


class AmbiguousIntentError(IntentError):
    """Multiple possible intents detected."""
    
    def __init__(self, message: str, possible_intents: Optional[list] = None, **kwargs):
        user_message = "Could you be more specific about what you want to do?"
        super().__init__(message, user_message=user_message, **kwargs)
        self.possible_intents = possible_intents or []
        if possible_intents:
            self.context["possible_intents"] = possible_intents


class UnknownIntentError(IntentError):
    """Unknown or unclear intent."""
    
    def __init__(self, message: str, user_input: Optional[str] = None, **kwargs):
        user_message = "I'm not sure what you want to do. Could you rephrase your request?"
        super().__init__(message, user_message=user_message, **kwargs)
        self.user_input = user_input
        if user_input:
            self.context["user_input"] = user_input[:100] + "..." if len(user_input) > 100 else user_input


# === Utility Functions ===

def handle_exception(
    func_name: str,
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_friendly: bool = True
) -> WorkspaceAIError:
    """
    Convert generic exceptions to appropriate WorkspaceAI exceptions.
    
    Args:
        func_name: Name of the function where error occurred
        exception: Original exception
        context: Additional context
        user_friendly: Whether to provide user-friendly messages
        
    Returns:
        Appropriate WorkspaceAI exception
    """
    context = context or {}
    context["function"] = func_name
    
    # Map common exception types to custom exceptions
    # Order matters! Check more specific types first
    if isinstance(exception, TimeoutError):
        return NetworkTimeoutError(
            f"Timeout in {func_name}: {exception}",
            context=context,
            original_error=exception
        )
    
    elif isinstance(exception, ConnectionError):
        return OllamaConnectionError(
            f"Connection error in {func_name}: {exception}",
            context=context,
            original_error=exception
        )
    
    elif isinstance(exception, (OSError, IOError)):
        if "permission" in str(exception).lower():
            return FilePermissionError(
                f"Permission error in {func_name}: {exception}",
                operation=func_name,
                context=context,
                original_error=exception
            )
        elif "not found" in str(exception).lower() or "no such file" in str(exception).lower():
            return FileNotFoundError(
                f"File not found in {func_name}: {exception}",
                context=context,
                original_error=exception
            )
        else:
            return FileSystemError(
                f"File system error in {func_name}: {exception}",
                context=context,
                original_error=exception
            )
    
    elif isinstance(exception, ValueError):
        return ToolParameterError(
            f"Parameter error in {func_name}: {exception}",
            context=context,
            original_error=exception
        )
    
    elif isinstance(exception, KeyError):
        return ConfigurationError(
            f"Configuration error in {func_name}: {exception}",
            context=context,
            original_error=exception
        )
    
    # Default to generic WorkspaceAI error
    return WorkspaceAIError(
        f"Unexpected error in {func_name}: {exception}",
        user_message="An unexpected error occurred" if user_friendly else None,
        context=context,
        original_error=exception
    )


def log_and_raise(exception: WorkspaceAIError):
    """
    Log and raise a WorkspaceAI exception.
    
    Args:
        exception: The exception to log and raise
    """
    # Exception is already logged in its constructor
    raise exception


# === Error Recovery Helpers ===

class ErrorRecovery:
    """Helper class for error recovery strategies."""
    
    @staticmethod
    def with_retry(
        func,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        exceptions: tuple = (WorkspaceAIError,)
    ):
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            max_attempts: Maximum retry attempts
            delay_seconds: Delay between attempts
            exceptions: Exception types to retry on
            
        Returns:
            Function result
            
        Raises:
            Last exception if all attempts fail
        """
        import time
        
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay_seconds}s: {e}")
                    time.sleep(delay_seconds)
                else:
                    logger.error(f"All {max_attempts} attempts failed")
                    
        if last_exception:
            raise last_exception
        else:
            raise WorkspaceAIError("All retry attempts failed with no exception captured")
    
    @staticmethod
    def with_fallback(primary_func, fallback_func, exceptions: tuple = (WorkspaceAIError,)):
        """
        Execute primary function with fallback on error.
        
        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            exceptions: Exception types to catch
            
        Returns:
            Result from primary or fallback function
        """
        try:
            return primary_func()
        except exceptions as e:
            logger.warning(f"Primary function failed, using fallback: {e}")
            return fallback_func()
