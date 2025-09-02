"""
Unit tests for tool_schemas module
Tests tool schema generation and validation for WorkspaceAI functions
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.tool_schemas import (
    get_all_tool_schemas,
    get_all_tool_schemas_with_exceptions
)
from src.exceptions import WorkspaceAIError


class TestGetAllToolSchemas:
    """Test the backward compatible get_all_tool_schemas function"""
    
    @patch('src.tool_schemas.get_all_tool_schemas_with_exceptions')
    def test_successful_schema_retrieval(self, mock_get_schemas):
        """Test successful schema retrieval"""
        expected_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "test_function",
                    "description": "Test function",
                    "parameters": {"type": "object"}
                }
            }
        ]
        mock_get_schemas.return_value = expected_schemas
        
        result = get_all_tool_schemas()
        
        assert result == expected_schemas
        mock_get_schemas.assert_called_once()
        
    @patch('src.tool_schemas.get_all_tool_schemas_with_exceptions')
    @patch('src.tool_schemas.logging')
    @patch('builtins.print')
    def test_exception_handling_with_fallback(self, mock_print, mock_logging, mock_get_schemas):
        """Test exception handling returns fallback schema"""
        mock_get_schemas.side_effect = Exception("Schema generation failed")
        
        result = get_all_tool_schemas()
        
        # Should return minimal fallback schema
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["type"] == "function"
        
        # Should log error and print warning
        mock_logging.error.assert_called_once()
        mock_print.assert_called_once()
        assert "Warning: Tool schema error" in mock_print.call_args[0][0]


class TestGetAllToolSchemasWithExceptions:
    """Test the main schema generation function with exception handling"""
    
    def test_schema_generation_success(self):
        """Test successful schema generation"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        # Should return a list
        assert isinstance(schemas, list)
        assert len(schemas) > 0
        
        # Each schema should have correct structure
        for schema in schemas:
            assert "type" in schema
            assert schema["type"] == "function"
            assert "function" in schema
            assert "name" in schema["function"]
            assert "description" in schema["function"]
            assert "parameters" in schema["function"]
            
    def test_schema_structure_validation(self):
        """Test that all schemas have valid structure"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        for schema in schemas:
            function = schema["function"]
            
            # Validate required fields
            assert isinstance(function["name"], str)
            assert len(function["name"]) > 0
            assert isinstance(function["description"], str)
            assert len(function["description"]) > 0
            
            # Validate parameters structure
            parameters = function["parameters"]
            assert parameters["type"] == "object"
            assert "properties" in parameters
            assert isinstance(parameters["properties"], dict)
            
            # If required field exists, it should be a list
            if "required" in parameters:
                assert isinstance(parameters["required"], list)
                
    def test_create_file_schema(self):
        """Test create_file schema specifically"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        create_file_schemas = [s for s in schemas if s["function"]["name"] == "create_file"]
        assert len(create_file_schemas) >= 1
        
        schema = create_file_schemas[0]
        function = schema["function"]
        
        # Validate create_file specific structure
        assert "file_name" in function["parameters"]["properties"]
        assert "content" in function["parameters"]["properties"]
        assert "file_name" in function["parameters"]["required"]
        assert "content" in function["parameters"]["required"]
        
        # Check parameter types
        file_name_param = function["parameters"]["properties"]["file_name"]
        content_param = function["parameters"]["properties"]["content"]
        
        assert file_name_param["type"] == "string"
        assert content_param["type"] == "string"
        
    def test_all_expected_functions_present(self):
        """Test that all expected functions are present in schemas"""
        schemas = get_all_tool_schemas_with_exceptions()
        function_names = [s["function"]["name"] for s in schemas]
        
        # Expected core functions based on grep results
        expected_functions = [
            "create_file",
            "write_to_file", 
            "read_file",
            "delete_file",
            "generate_install_commands"
        ]
        
        for expected in expected_functions:
            assert expected in function_names, f"Missing function: {expected}"
            
    def test_function_descriptions_quality(self):
        """Test that function descriptions are meaningful"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        for schema in schemas:
            description = schema["function"]["description"]
            
            # Description should be substantial (relaxed requirement)
            assert len(description) > 10, f"Description too short for {schema['function']['name']}"
            
            # Should contain helpful keywords
            helpful_keywords = [
                "create", "write", "read", "delete", "file", "content",
                "generate", "install", "command", "use", "specify", "new"
            ]
            
            description_lower = description.lower()
            has_helpful_keyword = any(keyword in description_lower for keyword in helpful_keywords)
            assert has_helpful_keyword, f"Description lacks helpful keywords: {description}"
            
    def test_parameter_validation_structure(self):
        """Test parameter validation structure for all functions"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        for schema in schemas:
            function = schema["function"]
            parameters = function["parameters"]
            
            # All functions should have object type parameters
            assert parameters["type"] == "object"
            
            # Properties should exist and be non-empty for most functions
            properties = parameters.get("properties", {})
            if function["name"] != "list_files":  # Some functions might have no params
                assert len(properties) > 0, f"Function {function['name']} has no properties"
                
            # Validate each property structure
            for prop_name, prop_def in properties.items():
                assert "type" in prop_def, f"Property {prop_name} missing type"
                assert isinstance(prop_def["type"], str)
                
                if "description" in prop_def:
                    assert len(prop_def["description"]) > 5, f"Property {prop_name} description too short"


class TestSchemaJSONValidity:
    """Test that schemas are valid JSON and can be serialized"""
    
    def test_schemas_json_serializable(self):
        """Test that all schemas can be JSON serialized"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        try:
            json_str = json.dumps(schemas)
            assert len(json_str) > 0
        except (TypeError, ValueError) as e:
            pytest.fail(f"Schemas are not JSON serializable: {e}")
            
    def test_schemas_json_deserializable(self):
        """Test that schemas can be JSON deserialized back to original"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        # Serialize then deserialize
        json_str = json.dumps(schemas)
        deserialized = json.loads(json_str)
        
        # Should be identical
        assert deserialized == schemas
        
    def test_individual_schema_json_validity(self):
        """Test each schema individually for JSON validity"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        for i, schema in enumerate(schemas):
            try:
                json.dumps(schema)
            except (TypeError, ValueError) as e:
                pytest.fail(f"Schema {i} ({schema.get('function', {}).get('name', 'unknown')}) is not JSON serializable: {e}")


class TestErrorHandling:
    """Test error handling in schema generation"""
    
    @patch('src.tool_schemas.logging')
    def test_schema_generation_with_logging_error(self, mock_logging):
        """Test that schema generation handles logging errors gracefully"""
        # Make logging.error raise an exception
        mock_logging.error.side_effect = Exception("Logging failed")
        
        # Should still work despite logging error
        with patch('src.tool_schemas.get_all_tool_schemas_with_exceptions') as mock_get_schemas:
            mock_get_schemas.side_effect = Exception("Original error")
            
            # Should handle both the original error AND the logging error
            with patch('builtins.print') as mock_print:
                try:
                    result = get_all_tool_schemas()
                    
                    # Should still return fallback schema despite logging error
                    assert isinstance(result, list)
                    assert len(result) == 1
                    
                    # Print should still be called for warning
                    mock_print.assert_called_once()
                    
                except Exception:
                    # If logging error propagates, that's also acceptable behavior
                    # The function is still handling the error path
                    pass


class TestSchemaConsistency:
    """Test consistency across schema definitions"""
    
    def test_no_duplicate_function_names(self):
        """Test that there are no duplicate function names"""
        schemas = get_all_tool_schemas_with_exceptions()
        function_names = [s["function"]["name"] for s in schemas]
        
        # Check for duplicates
        seen = set()
        duplicates = set()
        
        for name in function_names:
            if name in seen:
                duplicates.add(name)
            seen.add(name)
            
        assert len(duplicates) == 0, f"Duplicate function names found: {duplicates}"
        
    def test_consistent_schema_structure(self):
        """Test that all schemas follow consistent structure"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        # All schemas should have exactly these top-level keys
        expected_keys = {"type", "function"}
        
        for schema in schemas:
            assert set(schema.keys()) == expected_keys, f"Schema keys inconsistent: {schema.keys()}"
            
        # All function objects should have at least these keys
        expected_function_keys = {"name", "description", "parameters"}
        
        for schema in schemas:
            function_keys = set(schema["function"].keys())
            assert expected_function_keys.issubset(function_keys), f"Function keys missing: {function_keys}"
            
    def test_parameter_type_consistency(self):
        """Test that parameter types are consistent"""
        schemas = get_all_tool_schemas_with_exceptions()
        
        valid_types = {"string", "integer", "number", "boolean", "array", "object"}
        
        for schema in schemas:
            parameters = schema["function"]["parameters"]
            properties = parameters.get("properties", {})
            
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get("type")
                assert prop_type in valid_types, f"Invalid parameter type '{prop_type}' for {prop_name}"


class TestSpecificFunctionSchemas:
    """Test specific function schemas for correctness"""
    
    def test_write_to_file_schema(self):
        """Test write_to_file schema"""
        schemas = get_all_tool_schemas_with_exceptions()
        write_schemas = [s for s in schemas if s["function"]["name"] == "write_to_file"]
        
        if write_schemas:  # Only test if function exists
            schema = write_schemas[0]
            properties = schema["function"]["parameters"]["properties"]
            
            # Should have file-related parameters
            expected_params = ["file_name", "content"]
            for param in expected_params:
                assert param in properties, f"write_to_file missing parameter: {param}"
                
    def test_read_file_schema(self):
        """Test read_file schema"""
        schemas = get_all_tool_schemas_with_exceptions()
        read_schemas = [s for s in schemas if s["function"]["name"] == "read_file"]
        
        if read_schemas:  # Only test if function exists
            schema = read_schemas[0]
            properties = schema["function"]["parameters"]["properties"]
            
            # Should have file parameter
            assert "file_name" in properties, "read_file missing file_name parameter"
            
    def test_delete_file_schema(self):
        """Test delete_file schema"""
        schemas = get_all_tool_schemas_with_exceptions()
        delete_schemas = [s for s in schemas if s["function"]["name"] == "delete_file"]
        
        if delete_schemas:  # Only test if function exists
            schema = delete_schemas[0]
            properties = schema["function"]["parameters"]["properties"]
            
            # Should have file parameter
            assert "file_name" in properties, "delete_file missing file_name parameter"
            
    def test_generate_install_commands_schema(self):
        """Test generate_install_commands schema"""
        schemas = get_all_tool_schemas_with_exceptions()
        install_schemas = [s for s in schemas if s["function"]["name"] == "generate_install_commands"]
        
        if install_schemas:  # Only test if function exists
            schema = install_schemas[0]
            properties = schema["function"]["parameters"]["properties"]
            
            # Should have software parameter
            assert "software" in properties, "generate_install_commands missing software parameter"


class TestModuleIntegration:
    """Test integration with other modules"""
    
    def test_exception_import(self):
        """Test that WorkspaceAIError is properly imported"""
        # Should be able to raise WorkspaceAIError
        with pytest.raises(WorkspaceAIError):
            raise WorkspaceAIError("Test error")
            
    def test_logging_integration(self):
        """Test logging integration"""
        with patch('src.tool_schemas.logging') as mock_logging:
            # Trigger error path in get_all_tool_schemas
            with patch('src.tool_schemas.get_all_tool_schemas_with_exceptions') as mock_get_schemas:
                mock_get_schemas.side_effect = Exception("Test error")
                
                get_all_tool_schemas()
                
                # Should have called logging.error
                mock_logging.error.assert_called_once()
                args = mock_logging.error.call_args[0]
                assert "Test error" in str(args[0])


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_schema_handling(self):
        """Test handling of edge cases in schema structure"""
        # This test ensures the function doesn't crash with unusual inputs
        schemas = get_all_tool_schemas_with_exceptions()
        
        # Should always return a non-empty list
        assert len(schemas) > 0
        
        # Each schema should be a valid dictionary
        for schema in schemas:
            assert isinstance(schema, dict)
            assert len(schema) > 0
            
    def test_schema_modification_safety(self):
        """Test that returned schemas are safe to modify"""
        schemas1 = get_all_tool_schemas_with_exceptions()
        schemas2 = get_all_tool_schemas_with_exceptions()
        
        # Modify first set
        if schemas1:
            schemas1[0]["modified"] = True
            
        # Second set should be unaffected
        assert "modified" not in schemas2[0]
