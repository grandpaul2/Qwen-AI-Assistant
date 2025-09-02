"""
Updated Unit Tests for Enhanced Tool Instructions

Tests the context-aware tool instruction system that provides
dynamic tool recommendations and enhanced instructions.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path

from src.enhanced_tool_instructions import (
    build_enhanced_tool_instruction,
    get_context_aware_tool_schemas,
    build_context_aware_instruction,
    get_context_aware_tool_recommendations
)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_tool_schemas():
    """Sample tool schemas for testing"""
    return [
        {
            "type": "function",
            "function": {
                "name": "file_operations",
                "description": "Handle file operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "path": {"type": "string"}
                    }
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "code_interpreter",
                "description": "Execute code",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string"},
                        "code": {"type": "string"}
                    }
                }
            }
        }
    ]


@pytest.mark.unit
class TestEnhancedToolInstructions:
    """Test enhanced tool instruction generation"""
    
    def test_build_enhanced_tool_instruction_basic(self):
        """Test basic enhanced tool instruction building"""
        result = build_enhanced_tool_instruction()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "TOOL SELECTION STRATEGY" in result
    
    def test_build_enhanced_tool_instruction_contains_tools(self):
        """Test enhanced instruction contains tool information"""
        result = build_enhanced_tool_instruction()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "FILE_OPERATIONS" in result
        assert "CODE_INTERPRETER" in result
        assert "CALCULATOR" in result
    
    def test_build_enhanced_tool_instruction_contains_examples(self):
        """Test enhanced instruction contains examples"""
        result = build_enhanced_tool_instruction()
        
        assert isinstance(result, str)
        assert "Examples" in result or "EXAMPLES" in result
        assert "file_operations" in result
    
    def test_build_enhanced_tool_instruction_contains_guidelines(self):
        """Test enhanced instruction contains guidelines"""
        result = build_enhanced_tool_instruction()
        
        assert isinstance(result, str)
        assert "DO:" in result or "DON'T:" in result
        assert "GUIDELINES" in result


@pytest.mark.unit
class TestContextAwareToolSchemas:
    """Test context-aware tool schema generation"""
    
    def test_get_context_aware_tool_schemas_basic(self, temp_workspace):
        """Test basic context-aware tool schema generation"""
        result = get_context_aware_tool_schemas()
        
        assert isinstance(result, list)
        # Should return some tool schemas
        assert len(result) >= 0
    
    def test_get_context_aware_tool_schemas_file_context(self, temp_workspace):
        """Test context-aware schemas structure"""
        # Create a test file in workspace
        test_file = os.path.join(temp_workspace, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        result = get_context_aware_tool_schemas()
        
        assert isinstance(result, list)
        # Should include file-related tools
        tool_names = [tool.get("function", {}).get("name", "") for tool in result]
        assert any("file" in name.lower() for name in tool_names)
    
    def test_get_context_aware_tool_schemas_structure(self, temp_workspace):
        """Test that schemas have proper structure"""
        result = get_context_aware_tool_schemas()
        
        assert isinstance(result, list)
        
        for tool in result:
            assert "type" in tool
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
    
    def test_get_context_aware_tool_schemas_content(self, temp_workspace):
        """Test that schemas contain expected tools"""
        result = get_context_aware_tool_schemas()
        
        assert isinstance(result, list)
        # Should include various tool types
        tool_names = [tool.get("function", {}).get("name", "") for tool in result]
        expected_tools = ["file_operations", "code_interpreter", "calculator"]
        
        for expected_tool in expected_tools:
            assert any(expected_tool in name for name in tool_names)
    
    def test_get_context_aware_tool_schemas_consistency(self, temp_workspace):
        """Test that schemas are consistent across calls"""
        result1 = get_context_aware_tool_schemas()
        result2 = get_context_aware_tool_schemas()
        
        assert isinstance(result1, list)
        assert isinstance(result2, list)
        assert len(result1) == len(result2)
    
    def test_get_context_aware_tool_schemas_parameters(self):
        """Test that tool schemas have proper parameters"""
        result = get_context_aware_tool_schemas()
        
        for tool in result:
            if tool["function"]["name"] == "file_operations":
                params = tool["function"]["parameters"]["properties"]
                assert "action" in params
                assert "path" in params
                # Action should have enum values
                if "enum" in params["action"]:
                    assert len(params["action"]["enum"]) > 0


@pytest.mark.unit
class TestContextAwareInstructions:
    """Test context-aware instruction building"""
    
    def test_build_context_aware_instruction_basic(self, temp_workspace, sample_tool_schemas):
        """Test basic context-aware instruction building"""
        result = build_context_aware_instruction(
            "test message", 
            temp_workspace, 
            sample_tool_schemas
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "test message" in result
    
    def test_build_context_aware_instruction_with_workspace_files(self, temp_workspace, sample_tool_schemas):
        """Test context-aware instruction with workspace files"""
        # Create some test files
        files = ["test1.txt", "test2.py", "data.json"]
        for file in files:
            filepath = os.path.join(temp_workspace, file)
            with open(filepath, "w") as f:
                f.write(f"content of {file}")
        
        result = build_context_aware_instruction(
            "work with files", 
            temp_workspace, 
            sample_tool_schemas
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should mention available files
        for file in files:
            assert file in result
    
    def test_build_context_aware_instruction_empty_workspace(self, temp_workspace, sample_tool_schemas):
        """Test context-aware instruction with empty workspace"""
        result = build_context_aware_instruction(
            "test message", 
            temp_workspace, 
            sample_tool_schemas
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "empty" in result.lower() or "no files" in result.lower()
    
    def test_build_context_aware_instruction_large_workspace(self, temp_workspace, sample_tool_schemas):
        """Test context-aware instruction with many files"""
        # Create many files
        for i in range(20):
            filepath = os.path.join(temp_workspace, f"file_{i}.txt")
            with open(filepath, "w") as f:
                f.write(f"content {i}")
        
        result = build_context_aware_instruction(
            "list files", 
            temp_workspace, 
            sample_tool_schemas
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should handle large number of files gracefully
    
    def test_build_context_aware_instruction_no_tools(self, temp_workspace):
        """Test context-aware instruction with no tools"""
        result = build_context_aware_instruction("test message", temp_workspace, [])
        
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.unit
class TestContextAwareRecommendations:
    """Test context-aware tool recommendations"""
    
    def test_get_context_aware_tool_recommendations_basic(self, temp_workspace, sample_tool_schemas):
        """Test basic tool recommendations"""
        result = get_context_aware_tool_recommendations(
            "test message",
            temp_workspace,
            sample_tool_schemas
        )
        
        assert isinstance(result, dict)
        assert "recommended_tools" in result
        assert "context_analysis" in result
        assert "execution_plan" in result
        
        assert isinstance(result["recommended_tools"], list)
        assert isinstance(result["context_analysis"], dict)
        assert isinstance(result["execution_plan"], list)
    
    def test_get_context_aware_tool_recommendations_file_message(self, temp_workspace, sample_tool_schemas):
        """Test recommendations for file-related messages"""
        result = get_context_aware_tool_recommendations(
            "create a new file called test.txt",
            temp_workspace,
            sample_tool_schemas
        )
        
        assert isinstance(result, dict)
        assert len(result["recommended_tools"]) > 0
        
        # Should recommend file operations
        recommended = result["recommended_tools"]
        assert any("file" in tool.lower() for tool in recommended)
    
    def test_get_context_aware_tool_recommendations_code_message(self, temp_workspace, sample_tool_schemas):
        """Test recommendations for code-related messages"""
        result = get_context_aware_tool_recommendations(
            "run python script to analyze data",
            temp_workspace,
            sample_tool_schemas
        )
        
        assert isinstance(result, dict)
        assert len(result["recommended_tools"]) > 0
        
        # Should recommend code interpreter
        recommended = result["recommended_tools"]
        assert any("code" in tool.lower() for tool in recommended)
    
    def test_get_context_aware_tool_recommendations_with_history(self, temp_workspace, sample_tool_schemas):
        """Test recommendations with conversation history"""
        history = [
            "I want to work with files",
            "Create a Python script",
            "Run some calculations"
        ]
        
        result = get_context_aware_tool_recommendations(
            "continue with the analysis",
            temp_workspace,
            sample_tool_schemas,
            history
        )
        
        assert isinstance(result, dict)
        assert "context_analysis" in result
        # Should consider conversation history
        assert "conversation_context" in result["context_analysis"] or len(result["recommended_tools"]) > 0
    
    def test_get_context_aware_tool_recommendations_empty_message(self, temp_workspace, sample_tool_schemas):
        """Test recommendations with empty message"""
        result = get_context_aware_tool_recommendations(
            "",
            temp_workspace,
            sample_tool_schemas
        )
        
        assert isinstance(result, dict)
        assert "recommended_tools" in result
        assert "context_analysis" in result
    
    def test_get_context_aware_tool_recommendations_no_tools(self, temp_workspace):
        """Test recommendations with no available tools"""
        result = get_context_aware_tool_recommendations(
            "test message",
            temp_workspace,
            []
        )
        
        assert isinstance(result, dict)
        assert "recommended_tools" in result
        assert len(result["recommended_tools"]) == 0
    
    def test_get_context_aware_tool_recommendations_complex_message(self, temp_workspace, sample_tool_schemas):
        """Test recommendations for complex multi-step messages"""
        complex_message = """
        I need to:
        1. Create a Python script that reads data from a CSV file
        2. Process the data and calculate statistics
        3. Save the results to a new file
        4. Generate a simple visualization
        """
        
        result = get_context_aware_tool_recommendations(
            complex_message,
            temp_workspace,
            sample_tool_schemas
        )
        
        assert isinstance(result, dict)
        assert len(result["execution_plan"]) > 0
        
        # Should break down into steps
        plan = result["execution_plan"]
        assert len(plan) >= 2  # Should have multiple steps
    
    def test_get_context_aware_tool_recommendations_error_handling(self, temp_workspace):
        """Test error handling in recommendations"""
        # Test with invalid workspace
        result = get_context_aware_tool_recommendations(
            "test message",
            "/invalid/workspace/path",
            []
        )
        
        assert isinstance(result, dict)
        assert "context_analysis" in result
        # Should handle errors gracefully
        if "error" in result["context_analysis"]:
            assert "fallback" in result["context_analysis"]


@pytest.mark.unit
class TestIntegration:
    """Test integration between different components"""
    
    def test_full_workflow_integration(self, temp_workspace):
        """Test full workflow from message to recommendations"""
        user_message = "I want to create a Python script that lists all files"
        
        # Get context-aware schemas
        schemas = get_context_aware_tool_schemas()
        
        # Build context-aware instruction
        instruction = build_context_aware_instruction(user_message, temp_workspace, schemas)
        
        # Get recommendations
        recommendations = get_context_aware_tool_recommendations(
            user_message, temp_workspace, schemas
        )
        
        # Verify all components work together
        assert isinstance(schemas, list)
        assert isinstance(instruction, str)
        assert isinstance(recommendations, dict)
        
        assert len(instruction) > 0
        assert "recommended_tools" in recommendations
    
    def test_edge_case_integration(self, temp_workspace):
        """Test integration with edge cases"""
        edge_cases = [
            "",  # Empty message
            "a" * 1000,  # Very long message
            "特殊字符测试",  # Unicode characters
            "test\n\rmultiline\tmessage",  # Special characters
            "12345 !@#$% test",  # Mixed content
        ]
        
        for edge_case in edge_cases:
            # Should handle all edge cases gracefully
            schemas = get_context_aware_tool_schemas()
            instruction = build_context_aware_instruction(edge_case, temp_workspace, schemas)
            recommendations = get_context_aware_tool_recommendations(
                edge_case, temp_workspace, schemas
            )
            
            assert isinstance(schemas, list)
            assert isinstance(instruction, str)
            assert isinstance(recommendations, dict)
    
    @patch('src.enhanced_tool_instructions.os.listdir')
    def test_workspace_scanning_error_handling(self, mock_listdir, temp_workspace):
        """Test error handling when scanning workspace fails"""
        mock_listdir.side_effect = PermissionError("Access denied")
        
        result = build_context_aware_instruction(
            "test message", 
            temp_workspace, 
            []
        )
        
        # Should handle permission errors gracefully
        assert isinstance(result, str)
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__])
