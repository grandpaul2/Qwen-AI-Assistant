"""
Parameter extraction utilities for WorkspaceAI tools

Extracts parameters like filenames, content, and keywords from user prompts.
"""

import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ParameterExtractor:
    """Extracts parameters from user prompts for tool execution"""
    
    @staticmethod
    def extract_filename_from_prompt(prompt: str) -> Optional[str]:
        """
        Extract filename from user prompt using various patterns
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Extracted filename or None if not found
        """
        prompt_lower = prompt.lower()
        
        # Pattern 1: "file called/named X"
        match = re.search(r'\b(?:file|document)\s+(?:called|named)\s+([^\s,\.]+(?:\.[a-zA-Z0-9]+)?)', prompt_lower)
        if match:
            return match.group(1)
        
        # Pattern 2: "create X.ext"
        match = re.search(r'\b(?:create|make|write|generate)\s+([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)', prompt_lower)
        if match:
            return match.group(1)
        
        # Pattern 3: "save as X" or "save to X"
        match = re.search(r'\bsave\s+(?:as|to)\s+([a-zA-Z0-9_.-]+(?:\.[a-zA-Z0-9]+)?)', prompt_lower)
        if match:
            return match.group(1)
        
        # Pattern 4: Quoted filename
        match = re.search(r'["\']([^"\']+\.[a-zA-Z0-9]+)["\']', prompt)
        if match:
            return match.group(1)
        
        # Pattern 5: Extension at end of sentence/phrase
        match = re.search(r'\b([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)(?:\s|$|[,.])', prompt_lower)
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    def extract_content_from_prompt(prompt: str, tool_name: str) -> str:
        """
        Extract content to be written from the prompt
        
        Args:
            prompt: User's input prompt
            tool_name: Name of the tool being used
            
        Returns:
            Extracted content or generated content based on prompt
        """
        # Remove the action words to get content
        action_patterns = [
            r'\b(?:create|make|write|generate|build)\s+(?:a\s+)?(?:file|document)\s+(?:called|named)\s+[^\s]+\s+(?:with|containing)\s+',
            r'\b(?:save|store|put)\s+.*?\s+(?:in|to|as)\s+[^\s]+\s*:?\s*',
            r'\b(?:write|create)\s+.*?\s+(?:to|in)\s+[^\s]+\s*:?\s*'
        ]
        
        content = prompt
        for pattern in action_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        content = content.strip()
        
        # If no meaningful content extracted, generate based on prompt
        if not content or len(content) < 10:
            content = ParameterExtractor._generate_content_from_topic(prompt, tool_name)
        
        return content
    
    @staticmethod
    def _generate_content_from_topic(prompt: str, tool_name: str) -> str:
        """Generate content based on the topic in the prompt"""
        topic = ParameterExtractor.extract_topic_from_prompt(prompt)
        
        if tool_name == "write_json_file":
            return f'{{\n  "topic": "{topic}",\n  "created": "Generated from prompt",\n  "data": {{}}\n}}'
        elif any(ext in tool_name for ext in ["md", "markdown"]):
            return f"# {topic}\n\nContent for {topic}\n\n## Overview\n\nThis document covers {topic}."
        else:
            return f"Content for {topic}\n\nThis file contains information about {topic}."
    
    @staticmethod
    def extract_topic_from_prompt(prompt: str) -> str:
        """
        Extract the main topic/subject from a prompt
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Extracted topic or default
        """
        # Remove common action words
        topic = re.sub(r'\b(?:create|make|write|generate|build|save|store|put|file|document|guide|tutorial|about|for|on|the|a|an)\b', '', prompt, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        topic = re.sub(r'\s+', ' ', topic).strip()
        topic = re.sub(r'^[^\w]+|[^\w]+$', '', topic)
        
        # If nothing meaningful left, extract first meaningful words
        if not topic or len(topic) < 3:
            words = prompt.split()
            meaningful_words = [w for w in words if len(w) > 2 and w.lower() not in ['the', 'and', 'for', 'with', 'file', 'create', 'make']]
            topic = ' '.join(meaningful_words[:3]) if meaningful_words else 'Document'
        
        return topic.title()
    
    @staticmethod
    def extract_software_name_from_prompt(prompt: str) -> Optional[str]:
        """
        Extract software name from installation prompts
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Extracted software name or None
        """
        # Pattern 1: "install X" or "setup X"
        match = re.search(r'\b(?:install|setup|configure)\s+([a-zA-Z0-9._-]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 2: "how to install X"
        match = re.search(r'\bhow\s+to\s+install\s+([a-zA-Z0-9._-]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 3: "X installation"
        match = re.search(r'\b([a-zA-Z0-9._-]+)\s+installation', prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    def extract_search_keyword_from_prompt(prompt: str) -> Optional[str]:
        """
        Extract search keywords from file search prompts
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Extracted search keyword or None
        """
        # Pattern 1: "search for X"
        match = re.search(r'\bsearch\s+for\s+([^\s]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 2: "find files containing X"
        match = re.search(r'\bfind.*?containing\s+([^\s]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 3: "files with X"
        match = re.search(r'\bfiles\s+with\s+([^\s]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 4: Quoted search term
        match = re.search(r'["\']([^"\']+)["\']', prompt)
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    def extract_source_and_target_from_prompt(prompt: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract source and target filenames from copy/move operations
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Tuple of (source_filename, target_filename)
        """
        # Pattern 1: "copy X to Y"
        match = re.search(r'\b(?:copy|move)\s+([^\s]+)\s+to\s+([^\s]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2)
        
        # Pattern 2: "copy X as Y"
        match = re.search(r'\b(?:copy|move)\s+([^\s]+)\s+as\s+([^\s]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2)
        
        return None, None
    
    @staticmethod
    def generate_tool_parameters(tool_name: str, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate parameters for a specific tool based on the prompt
        
        Args:
            tool_name: Name of the tool
            prompt: User's input prompt
            
        Returns:
            Dictionary of parameters or None if extraction fails
        """
        try:
            if tool_name in ["create_file", "write_to_file", "write_txt_file", "write_md_file"]:
                filename = ParameterExtractor.extract_filename_from_prompt(prompt)
                if not filename:
                    topic = ParameterExtractor.extract_topic_from_prompt(prompt)
                    filename = f"{topic.lower().replace(' ', '_')}.txt"
                
                content = ParameterExtractor.extract_content_from_prompt(prompt, tool_name)
                return {"file_name": filename, "content": content}
            
            elif tool_name == "write_json_file":
                filename = ParameterExtractor.extract_filename_from_prompt(prompt)
                if not filename:
                    topic = ParameterExtractor.extract_topic_from_prompt(prompt)
                    filename = f"{topic.lower().replace(' ', '_')}.json"
                
                content = ParameterExtractor.extract_content_from_prompt(prompt, tool_name)
                return {"file_name": filename, "content": content}
            
            elif tool_name in ["read_file", "delete_file"]:
                filename = ParameterExtractor.extract_filename_from_prompt(prompt)
                if filename:
                    return {"file_name": filename}
            
            elif tool_name in ["copy_file", "move_file"]:
                source, target = ParameterExtractor.extract_source_and_target_from_prompt(prompt)
                if source and target:
                    return {"source_file": source, "target_file": target}
            
            elif tool_name == "search_files":
                keyword = ParameterExtractor.extract_search_keyword_from_prompt(prompt)
                if keyword:
                    return {"search_term": keyword}
            
            elif tool_name == "generate_install_commands":
                software = ParameterExtractor.extract_software_name_from_prompt(prompt)
                if software:
                    return {"software": software}
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating parameters for {tool_name}: {e}")
            return None
