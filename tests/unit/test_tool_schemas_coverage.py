"""
Additional tests for tool_schemas.py to achieve 80%+ coverage
Simple approach to hit missing lines without complex mocking
"""
import pytest
from src.tool_schemas import get_all_tool_schemas_with_exceptions, get_all_tool_schemas
from src.exceptions import WorkspaceAIError


class TestBasicToolSchemasCoverage:
    """Basic tests to improve tool_schemas coverage"""
    
    def test_get_all_tool_schemas_wrapper(self):
        """Test the wrapper function get_all_tool_schemas"""
        # This should call get_all_tool_schemas_with_exceptions internally
        schemas = get_all_tool_schemas()
        assert len(schemas) > 0
        assert isinstance(schemas, list)
        
        # Validate basic structure
        for schema in schemas:
            assert isinstance(schema, dict)
            assert "type" in schema
            assert "function" in schema
    
    def test_get_all_tool_schemas_with_exceptions_direct(self):
        """Test the main function directly"""
        schemas = get_all_tool_schemas_with_exceptions()
        assert len(schemas) > 0
        assert isinstance(schemas, list)
        
        # This should hit the validation success paths
        for i, schema in enumerate(schemas):
            assert isinstance(schema, dict), f"Schema {i} must be a dictionary"
            assert "type" in schema and "function" in schema, f"Schema {i} missing required fields"
    
    def test_schema_content_validation(self):
        """Test that schemas have proper content structure"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        # Look for expected function names
        function_names = [schema["function"]["name"] for schema in schemas]
        
        # Should include basic file operations
        expected_functions = ["create_file", "write_to_file", "read_file"]
        for func_name in expected_functions:
            assert func_name in function_names, f"Expected function {func_name} not found"
    
    def test_schema_logging_and_debug(self):
        """Test that schema generation includes logging"""
        # Just run the function normally to exercise logging paths
        schemas = get_all_tool_schemas_with_exceptions()
        assert len(schemas) > 0
        
        # Also test the wrapper function 
        wrapper_schemas = get_all_tool_schemas()
        assert len(wrapper_schemas) > 0
    
    def test_error_path_coverage(self):
        """Test error handling paths"""
        from unittest.mock import patch
        
        # Test wrapper function error handling (line 26)
        with patch('src.tool_schemas.get_all_tool_schemas_with_exceptions') as mock_func:
            mock_func.side_effect = Exception("Test error for coverage")
            
            # This should hit the exception handler and return fallback schema
            schemas = get_all_tool_schemas()
            assert len(schemas) > 0  # Should return fallback schema


class TestErrorPaths:
    """Test error handling paths without complex mocking"""
    
    def test_import_validation(self):
        """Test that imports work correctly"""
        # Test importing the functions
        from src.tool_schemas import get_all_tool_schemas, get_all_tool_schemas_with_exceptions
        from src.exceptions import WorkspaceAIError
        
        # These should not raise import errors
        assert callable(get_all_tool_schemas)
        assert callable(get_all_tool_schemas_with_exceptions)
        assert issubclass(WorkspaceAIError, Exception)
    
    def test_wrapper_fallback_behavior(self):
        """Test wrapper function fallback when main function fails"""
        from unittest.mock import patch, MagicMock
        
        # Mock to cause the main function to fail
        with patch('src.tool_schemas.get_all_tool_schemas_with_exceptions') as mock_main:
            mock_main.side_effect = Exception("Simulated failure")
            
            # This should trigger the exception handler in get_all_tool_schemas
            # and return the fallback schema (lines 26, 28-32)
            result = get_all_tool_schemas()
            
            # Should return fallback schema, not empty
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Should be basic fallback schema structure
            schema = result[0]
            assert "type" in schema
            assert "function" in schema
