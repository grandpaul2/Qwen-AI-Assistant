"""
Ollama API client for WorkspaceAI

This module handles all interactions with the Ollama API, including:
- API connection testing and health checks
- Tool-enabled chat completions with conversation memory
- File intent detection for automatic tool usage
- Request/response handling with retry logic and error handling
"""

import json
import logging
import re
import requests
import time
import threading
from typing import Optional

from .config import APP_CONFIG, CONSTANTS, CYAN, RESET, load_config
from .memory import memory


def format_tool_result(tool_name: str, result: str) -> str:
    """Format tool results for clean output"""
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
    else:
        return result


from .memory import memory
from .file_manager import file_manager
from .utils import show_progress
from .tool_schemas import get_all_tool_schemas
from .intent_classifier import IntentClassifier
from .tool_selector import ContextWeightedToolSelector

# Initialize enhanced tool selection components
intent_classifier = IntentClassifier()
tool_selector = ContextWeightedToolSelector()

# Additional color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'

# Configure logging
logger = logging.getLogger(__name__)


def enhanced_tool_selection_pipeline(prompt: str, verbose_output: bool = False) -> tuple[str, str, dict]:
    """
    Enhanced three-stage tool selection pipeline
    
    Args:
        prompt: User input string
        verbose_output: Whether to show debug information
        
    Returns:
        Tuple of (selected_tool, confidence_level, debug_info)
    """
    # Stage 1: Intent Classification
    intent, confidence = intent_classifier.classify_with_confidence(prompt)
    
    # Stage 2: Tool Selection with Context Weighting
    total_weight, word_breakdown = tool_selector.calculate_context_weight(prompt)
    selected_tool = tool_selector.select_tool(intent, prompt, confidence)
    
    # Stage 3: Determine confidence level
    if confidence > 0.8 and total_weight > 10:
        confidence_level = "HIGH_CONFIDENCE"
    elif confidence > 0.5 and total_weight > 5:
        confidence_level = "MEDIUM_CONFIDENCE"
    else:
        confidence_level = "LLM_FALLBACK"
    
    # Debug information
    debug_info = {
        'intent': intent,
        'intent_confidence': confidence,
        'total_weight': total_weight,
        'word_breakdown': word_breakdown,
        'selected_tool': selected_tool,
        'confidence_level': confidence_level
    }
    
    # Print debug information only if verbose
    if verbose_output:
        print(f"🎯 Intent: {intent} (confidence: {confidence:.2f})")
        print(f"⚖️  Context Weight: {total_weight} {word_breakdown}")
        print(f"🔧 Selected Tool: {selected_tool} ({confidence_level})")
    
    return selected_tool, confidence_level, debug_info


def should_use_enhanced_selection(prompt: str) -> bool:
    """
    Determine if we should use enhanced selection vs fallback to LLM
    
    Args:
        prompt: User input string
        
    Returns:
        True if enhanced selection should be used
    """
    # Always try enhanced selection first
    # If it fails or has low confidence, we'll fallback to LLM
    return detect_file_intent(prompt)


def detect_file_intent(prompt: str) -> bool:
    """Enhanced contextual detection for file operations"""
    prompt_lower = prompt.lower()
    
    # File action patterns (contextual)
    file_action_patterns = [
        # Direct commands
        r'\b(create|make|generate|build)\s+.*\b(file|folder|directory)\b',
        r'\b(save|write|store|put)\s+.*\b(to|in|into)\s+.*\b(workspace|folder|directory)\b',
        r'\b(read|open|view|show|display)\s+.*\b(file|document)\b',
        
        # Installation commands (NEW PATTERN)
        r'\b(install|setup|configure)\s+\w+',
        r'\bhow\s+to\s+install\s+\w+',
        r'\binstallation\s+(commands|instructions|steps)\s+for\s+\w+',
        r'\bget\s+.*\binstallation\b',
        
        # Enhanced file reading patterns (ACCURACY BOOST)
        r'\b(what\'s in|what is in|contents? of|inside)\s+.*\.(py|txt|json|md|csv)\b',
        r'\b(review|analyze|check|examine|inspect|look at)\s+.*\b(my|the)\s+.*\.(py|txt|json|md|csv)\b',
        r'\b(what\'s in|what is in)\s+.*\b(my|the)\s+.*\b(file|document)\b',
        
        # Search and find operations
        r'\b(find|search|list|show)\s+.*\b(files?|folders?|directories?)\b',
        r'\b(find|search)\s+.*\b(in|within)\s+.*\b(workspace|folder|directory)\b',
        
        # Conversational requests  
        r'\b(can you|could you|please)\s+.*(create|save|make|generate|find|search|read|review)\b',
        r'(i need|i want|i would like)\s+.*\b(file|folder|document)\b',
        
        # File extensions and workspace references
        r'\.(md|txt|json|csv|py|js|html|css)\b',
        r'\b(workspace|project|repository)\s+(folder|directory)\b',
        
        # File naming and renaming context
        r'\b(call it|name it|rename)\s+.*\b(different|another|new)\b',  # "call it different name"
        r'\b(save.*as|export.*as)\b',
        
        # File operation context
        r'\b(overwrite|replace|update)\s+.*\b(file|document)\b'
    ]
    
    # Exclude conversational questions (stronger patterns)
    exclusion_patterns = [
        r'\b(what is|what are|how do|how does|explain|describe|tell me about|why)\b',
        r'\b(when was|when did|which|where)\b',
        r'\b(difference between|compare|versus|vs\.)\b',  # Comparison questions
        r'\b(i read|i saw|i heard|reading about)\b',
        r'\b(book|article|story|tutorial)\b',
        r'\b(have you|did you)\s+(created|made|saved|written|finished)\b',  # "have you created"
        r'\b(where is|can i see|do you see)\b',  # Location/visibility questions
        r'\b(learn|understand|know|help me understand)\b'  # Learning/educational context
    ]
    
    # Check exclusions first BUT make exceptions for file-specific requests
    for pattern in exclusion_patterns:
        if re.search(pattern, prompt_lower):
            # Exception: "what's in [filename]" should still trigger tools
            if re.search(r'\b(what\'s in|what is in)\s+.*\.(py|txt|json|md|csv)\b', prompt_lower):
                break  # Don't exclude, continue to tool detection
            # Exception: "what's in my [file]" should still trigger tools  
            elif re.search(r'\b(what\'s in|what is in)\s+.*\b(my|the)\s+.*\b(file|document)\b', prompt_lower):
                break  # Don't exclude, continue to tool detection
            else:
                return False  # Exclude this as conversational
    
    # Special case: "call it a different name" should trigger tools
    if "call it" in prompt_lower and ("different" in prompt_lower or "another" in prompt_lower):
        return True
    
    # Check for file action patterns
    if any(re.search(pattern, prompt_lower) for pattern in file_action_patterns):
        return True
    
    # Fallback to enhanced keyword detection with context awareness
    enhanced_keywords = [
        'file', 'folder', 'directory', 'create', 'make', 'generate', 'build',
        'save', 'write', 'edit', 'copy', 'move', 'list', 'search', 'find',
        'compress', 'backup', 'json', 'txt', 'md', 'workspace', 'put', 'store'
    ]
    
    # Only trigger on keywords if there's action context
    has_keywords = any(keyword in prompt_lower for keyword in enhanced_keywords)
    has_action_words = any(word in prompt_lower for word in ['create', 'make', 'save', 'write', 'generate', 'build', 'put', 'find', 'search', 'list', 'show', 'delete', 'remove'])
    
    return has_keywords and has_action_words


def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        logger.info("Testing Ollama connection...")
        host = APP_CONFIG['ollama_host']
        response = requests.get(f"http://{host}/api/tags", timeout=CONSTANTS['SUMMARY_TIMEOUT'])
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            qwen_models = [m['name'] for m in models if 'qwen' in m['name'].lower()]
            
            if qwen_models:
                print(f"✅ Ollama connected! Available Qwen models: {', '.join(qwen_models)}")
                logger.info(f"Ollama connection successful. Qwen models: {qwen_models}")
                return True
            else:
                print("⚠️  Ollama connected but no Qwen models found!")
                print(f"💡 Run: ollama pull {APP_CONFIG['model']}")
                logger.warning("No Qwen models found in Ollama")
                return False
        else:
            logger.error(f"Ollama returned status {response.status_code}: {response.text}")
            print(f"❌ Ollama error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Ollama connection timeout")
        print(f"❌ Ollama connection timeout ({CONSTANTS['SUMMARY_TIMEOUT']}s)")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
        
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to Ollama")
        print("❌ Could not connect to Ollama")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from Ollama: {e}")
        print("❌ Invalid response from Ollama")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error testing Ollama connection: {e}")
        print(f"❌ Ollama connection failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False


def enhance_prompt_for_function_selection(prompt: str) -> str:
    """Pre-process prompts to improve function selection accuracy"""
    
    # Common task-to-function mappings
    task_mappings = {
        'backup': 'copy_file',
        'duplicate': 'copy_file', 
        'save copy': 'copy_file',
        'make backup': 'copy_file',
        'create csv': 'create_file',
        'make csv': 'create_file',
        'generate file': 'create_file',
        'find files': 'search_files',
        'locate files': 'search_files',
        'search for': 'search_files'
    }
    
    enhanced_prompt = prompt
    prompt_lower = prompt.lower()
    
    # Add specific hints based on detected patterns
    for task, function in task_mappings.items():
        if task in prompt_lower:
            enhanced_prompt += f"\n[FUNCTION HINT: For '{task}' operations, use '{function}']"
    
    # CRITICAL: Detect guide/documentation creation vs installation requests
    if any(word in prompt_lower for word in ['guide', 'tutorial', 'documentation', 'write', 'create']):
        if any(word in prompt_lower for word in ['file', 'document', 'guide', 'tutorial', 'doc']):
            enhanced_prompt += "\n[CRITICAL: User wants to CREATE a file/guide/document - use create_file, NOT generate_install_commands]"
    
    # Detect installation requests vs file creation
    if any(word in prompt_lower for word in ['install', 'setup', 'how to install']):
        if not any(word in prompt_lower for word in ['write', 'create', 'save', 'file', 'guide', 'document']):
            enhanced_prompt += "\n[CRITICAL: User wants installation commands - use generate_install_commands]"
    
    return enhanced_prompt


def auto_correct_function_name(function_name: str) -> tuple[str, bool]:
    """Auto-correct common function name mistakes"""
    
    # Auto-correction mappings based on testing findings
    auto_corrections = {
        'backup_files': 'copy_file',
        'create_csv_file': 'create_file',
        'make_file': 'create_file',
        'find_files': 'search_files',
        'locate_files': 'search_files',
        'duplicate_file': 'copy_file',
        'save_file': 'create_file',
        'generate_file': 'create_file',
        'create_txt_file': 'create_file',
        'create_md_file': 'create_file',
        'read_csv_file': 'read_file'
    }
    
    if function_name in auto_corrections:
        corrected = auto_corrections[function_name]
        # Only show correction in verbose mode
        current_config = load_config()
        if current_config.get('verbose_output', False):
            print(f"🔧 Auto-correcting '{function_name}' → '{corrected}'")
        return corrected, True
    
    return function_name, False


def auto_correct_parameters(function_name: str, original_function: str, function_args: dict) -> dict:
    """Auto-correct parameters when function names are corrected"""
    
    # Parameter mappings for auto-corrected functions
    parameter_mappings = {
        'create_csv_file->create_file': {
            'data': 'content',      # Convert data array to string content
            'headers': None,        # Remove headers parameter
            'filename': 'file_name' # Map filename to file_name
        },
        'create_txt_file->create_file': {
            'text': 'content',
            'filename': 'file_name'
        },
        'backup_files->copy_file': {
            'source': 'src_file',
            'destination': 'dest_file',
            'backup_name': 'dest_file'
        }
    }
    
    mapping_key = f"{original_function}->{function_name}"
    if mapping_key in parameter_mappings:
        corrected_args = {}
        mapping = parameter_mappings[mapping_key]
        
        for old_param, value in function_args.items():
            new_param = mapping.get(old_param, old_param)
            if new_param is not None:  # None means remove this parameter
                if old_param == 'data' and new_param == 'content':
                    # Convert data array to CSV string format
                    if isinstance(value, list) and len(value) > 0:
                        import csv
                        import io
                        output = io.StringIO()
                        writer = csv.writer(output)
                        for row in value:
                            writer.writerow(row)
                        corrected_args[new_param] = output.getvalue()
                    else:
                        corrected_args[new_param] = str(value)
                else:
                    corrected_args[new_param] = value
        
        # Only show parameter mapping in verbose mode
        current_config = load_config()
        if current_config.get('verbose_output', False):
            print(f"🔧 Parameter mapping applied: {mapping}")
        return corrected_args
    
    return function_args


def call_ollama_with_tools(prompt: str, model: Optional[str] = None, use_tools: bool = True):
    """Call Ollama with enhanced tool selection pipeline and conversation memory"""
    
    # Load current config to check verbose setting
    current_config = load_config()
    verbose_output = current_config.get('verbose_output', False)
    
    if model is None:
        model = APP_CONFIG['model']
    
    # Add user message to memory
    memory.add_message("user", prompt)
    
    # Enhanced Tool Selection Pipeline
    if use_tools and should_use_enhanced_selection(prompt):
        if verbose_output:
            print(f"\n{CYAN}🚀 Enhanced Tool Selection Pipeline Activated{RESET}")
        
        # Run the enhanced selection pipeline
        selected_tool, confidence_level, debug_info = enhanced_tool_selection_pipeline(prompt, verbose_output)
        
        # For high confidence selections, execute directly without LLM
        if confidence_level == "HIGH_CONFIDENCE":
            if verbose_output:
                print(f"{GREEN}✅ High confidence - executing tool directly{RESET}")
            return execute_tool_directly(selected_tool, prompt, debug_info, verbose_output)
        
        # For medium confidence, use LLM with strong guidance
        elif confidence_level == "MEDIUM_CONFIDENCE":
            if verbose_output:
                print(f"{YELLOW}⚠️  Medium confidence - using LLM with guidance{RESET}")
            return call_ollama_with_guidance(prompt, model, selected_tool, debug_info)
        
        # For low confidence, use hierarchical LLM fallback
        else:
            if verbose_output:
                print(f"{RED}🔄 Low confidence - using hierarchical LLM fallback{RESET}")
            return call_ollama_with_hierarchical_prompt(prompt, model)
    
    # Fallback to original method for non-tool requests
    else:
        return call_ollama_original_method(prompt, model, use_tools)


def execute_tool_directly(selected_tool: str, prompt: str, debug_info: dict, verbose_output: bool = False):
    """Execute tool directly for high-confidence selections"""
    if verbose_output:
        print(f"\n🔧 Direct Tool Execution: {selected_tool}")
    
    # Generate parameters based on the tool and prompt
    tool_args = generate_tool_parameters(selected_tool, prompt)
    
    if not tool_args:
        if verbose_output:
            print(f"❌ Could not generate parameters for {selected_tool}")
        return call_ollama_with_hierarchical_prompt(prompt, APP_CONFIG['model'])
    
    if verbose_output:
        print(f"📝 Generated parameters: {json.dumps(tool_args, indent=2)}")
    
    # Execute the tool
    try:
        if hasattr(file_manager, selected_tool):
            result = getattr(file_manager, selected_tool)(**tool_args)
            # Always show result for tool execution (clean format)
            if verbose_output:
                print(f"✅ Result: {result}")
            else:
                print(f"🔧 {selected_tool} → {format_tool_result(selected_tool, result)}")
            memory.add_message("assistant", f"Executed {selected_tool} successfully: {result}")
            memory.add_message("tool", f"{selected_tool}: {result}")
            return result
        elif selected_tool == "generate_install_commands":
            from .utils import generate_install_commands
            result = generate_install_commands(**tool_args)
            if verbose_output:
                print(f"✅ Generated Commands:")
                print(result)
            else:
                print(f"🔧 {selected_tool} → Installation commands generated")
            memory.add_message("assistant", f"Generated installation commands: {result}")
            memory.add_message("tool", f"Generated install commands: {result}")
            return result
        else:
            if verbose_output:
                print(f"❌ Unknown tool: {selected_tool}")
            return call_ollama_with_hierarchical_prompt(prompt, APP_CONFIG['model'])
            
    except Exception as e:
        if verbose_output:
            print(f"❌ Error executing {selected_tool}: {e}")
        return call_ollama_with_hierarchical_prompt(prompt, APP_CONFIG['model'])


def generate_tool_parameters(tool_name: str, prompt: str) -> Optional[dict]:
    """Generate parameters for tool execution based on prompt analysis"""
    prompt_lower = prompt.lower()
    
    if tool_name == "create_file":
        # Extract filename and content from prompt
        filename = extract_filename_from_prompt(prompt) or "output.txt"
        content = extract_content_from_prompt(prompt, tool_name) or f"Content generated from: {prompt}"
        return {"file_name": filename, "content": content}
    
    elif tool_name == "write_to_file":
        filename = extract_filename_from_prompt(prompt) or "output.txt"
        content = extract_content_from_prompt(prompt, tool_name) or f"Content generated from: {prompt}"
        return {"file_name": filename, "content": content}
    
    elif tool_name == "write_json_file":
        filename = extract_filename_from_prompt(prompt) or "data.json"
        content = {"generated_from": prompt, "timestamp": time.time()}
        return {"file_name": filename, "data": content}
    
    elif tool_name == "generate_install_commands":
        software = extract_software_name_from_prompt(prompt)
        if software:
            return {"software": software}
        else:
            return None
    
    elif tool_name in ["copy_file", "move_file"]:
        # Need source and destination - might need LLM help
        return None
    
    elif tool_name in ["read_file", "delete_file"]:
        filename = extract_filename_from_prompt(prompt)
        if filename:
            return {"file_name": filename}
        else:
            return None
    
    elif tool_name == "search_files":
        keyword = extract_search_keyword_from_prompt(prompt)
        if keyword:
            return {"keyword": keyword}
        else:
            return None
    
    elif tool_name == "list_files":
        return {}  # No parameters needed
    
    else:
        return None


def extract_filename_from_prompt(prompt: str) -> Optional[str]:
    """Extract filename from user prompt"""
    # Look for explicit filename patterns
    filename_patterns = [
        r'call it\s+([^\s]+\.\w+)',
        r'name it\s+([^\s]+\.\w+)',
        r'save\s+(?:it\s+)?(?:as\s+)?([^\s]+\.\w+)',
        r'create\s+(?:a\s+)?(?:file\s+)?(?:called\s+)?([^\s]+\.\w+)',
        r'write\s+(?:to\s+)?([^\s]+\.\w+)',
        r'(?:file|document)\s+(?:called\s+)?([^\s]+\.\w+)'
    ]
    
    for pattern in filename_patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            return match.group(1)
    
    # Generate filename based on content type
    if any(word in prompt.lower() for word in ['guide', 'tutorial', 'documentation']):
        return "guide.md"
    elif 'csv' in prompt.lower():
        return "data.csv"
    elif 'json' in prompt.lower():
        return "data.json"
    elif any(word in prompt.lower() for word in ['python', 'script']):
        return "script.py"
    else:
        return "output.txt"


def extract_content_from_prompt(prompt: str, tool_name: str) -> str:
    """Extract or generate content based on the prompt"""
    # Look for explicit content
    content_patterns = [
        r'content[:\s]+["\']([^"\']+)["\']',
        r'write[:\s]+["\']([^"\']+)["\']',
        r'text[:\s]+["\']([^"\']+)["\']'
    ]
    
    for pattern in content_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Generate appropriate content based on request type
    topic = extract_topic_from_prompt(prompt)
    
    if 'guide' in prompt.lower():
        if 'git' in topic.lower():
            return """# Git Guide

## What is Git?
Git is a distributed version control system that tracks changes in files and coordinates work among multiple people.

## Getting Started

### Installation
- **Windows**: Download from https://git-scm.com/
- **macOS**: `brew install git` or download from git-scm.com
- **Linux**: `sudo apt install git` (Ubuntu/Debian) or `sudo yum install git` (CentOS/RHEL)

### Initial Setup
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Basic Commands

### Creating a Repository
```bash
git init                    # Initialize a new repository
git clone <url>            # Clone an existing repository
```

### Making Changes
```bash
git add <file>             # Stage a file
git add .                  # Stage all changes
git commit -m "message"    # Commit staged changes
git status                 # Check repository status
```

### Working with Branches
```bash
git branch                 # List branches
git branch <name>          # Create a new branch
git checkout <branch>      # Switch to a branch
git checkout -b <branch>   # Create and switch to new branch
git merge <branch>         # Merge a branch
```

### Remote Repositories
```bash
git remote add origin <url>    # Add a remote repository
git push origin <branch>       # Push to remote
git pull origin <branch>       # Pull from remote
git fetch                      # Fetch changes without merging
```

## Advanced Topics

### Viewing History
```bash
git log                    # View commit history
git log --oneline         # Compact log view
git diff                  # Show changes
git blame <file>          # Show who changed what
```

### Undoing Changes
```bash
git reset <file>          # Unstage a file
git reset --hard HEAD     # Reset to last commit
git revert <commit>       # Revert a specific commit
```

### Best Practices
- Write clear, descriptive commit messages
- Commit frequently with small, logical changes
- Use branches for features and experiments
- Keep your main branch clean and stable
- Review changes before committing

## Useful Resources
- Official Git Documentation: https://git-scm.com/docs
- Pro Git Book: https://git-scm.com/book
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf"""
        
        elif 'docker' in topic.lower():
            return """# Docker Guide

## What is Docker?
Docker is a platform that uses containerization to package applications and their dependencies into lightweight, portable containers.

## Getting Started

### Installation
- **Windows**: Download Docker Desktop from https://docker.com/
- **macOS**: Download Docker Desktop from https://docker.com/
- **Linux**: Use your package manager or follow instructions at https://docs.docker.com/

### Basic Concepts
- **Image**: A read-only template used to create containers
- **Container**: A running instance of an image
- **Dockerfile**: A text file with instructions to build an image
- **Registry**: A repository for Docker images (like Docker Hub)

## Essential Commands

### Images
```bash
docker images              # List local images
docker pull <image>        # Download an image
docker build -t <name> .   # Build an image from Dockerfile
docker rmi <image>         # Remove an image
```

### Containers
```bash
docker run <image>         # Run a container
docker run -d <image>      # Run in detached mode
docker run -p 8080:80 <image>  # Map ports
docker ps                  # List running containers
docker ps -a              # List all containers
docker stop <container>    # Stop a container
docker rm <container>      # Remove a container
```

### Management
```bash
docker exec -it <container> bash  # Access container shell
docker logs <container>           # View container logs
docker inspect <container>        # View container details
```

## Creating a Dockerfile
```dockerfile
FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## Docker Compose
Use `docker-compose.yml` for multi-container applications:
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "3000:3000"
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: password
```

## Best Practices
- Use official base images when possible
- Keep images small by using multi-stage builds
- Don't run containers as root
- Use .dockerignore to exclude unnecessary files
- Tag your images with meaningful versions

## Useful Resources
- Official Docker Documentation: https://docs.docker.com/
- Docker Hub: https://hub.docker.com/
- Docker Best Practices: https://docs.docker.com/develop/best-practices/"""
        
        else:
            return f"""# {topic} Guide

## Overview
This is a comprehensive guide for {topic}.

## Getting Started
Introduction and basic setup instructions for {topic}.

## Core Concepts
Key concepts and terminology you need to understand.

## Common Tasks
Step-by-step instructions for common operations.

## Advanced Topics
More complex features and use cases.

## Best Practices
Recommended approaches and patterns.

## Troubleshooting
Common issues and how to resolve them.

## Resources
- Official documentation
- Community resources
- Useful tools and extensions"""
    
    elif 'tutorial' in prompt.lower():
        return f"""# {topic} Tutorial

## Introduction
Welcome to this step-by-step {topic} tutorial.

## Prerequisites
What you need to know before starting:
- Basic computer skills
- Relevant background knowledge

## Step 1: Setup
Set up your environment and install necessary tools.

## Step 2: Basic Operations
Learn the fundamental operations and commands.

## Step 3: Working Example
Build a simple example to practice the concepts.

## Step 4: Advanced Features
Explore more sophisticated capabilities.

## Conclusion
Summary of what you've learned and next steps.

## Additional Resources
- Further reading
- Practice exercises
- Community support"""
    
    elif 'documentation' in prompt.lower():
        return f"""# {topic} Documentation

## API Reference
Complete reference for all available functions and methods.

## Configuration
How to configure and customize {topic}.

## Usage Examples
```
# Example code snippets
example_function()
```

## Parameters
- **param1**: Description of parameter
- **param2**: Description of parameter

## Return Values
Description of what the function returns.

## Error Handling
Common errors and how to handle them.

## Changelog
- v1.0: Initial release
- v1.1: Bug fixes and improvements"""
    
    else:
        return f"Content generated from request: {prompt}"


def extract_topic_from_prompt(prompt: str) -> str:
    """Extract the main topic from a prompt"""
    # Look for "for X" or "about X" patterns
    topic_patterns = [
        r'(?:guide|tutorial|documentation)\s+(?:for|about|on)\s+(\w+)',
        r'(?:for|about|on)\s+(\w+)\s*$',
        r'(\w+)\s+(?:guide|tutorial|documentation)'
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            return match.group(1).capitalize()
    
    return "Topic"


def extract_software_name_from_prompt(prompt: str) -> Optional[str]:
    """Extract software name for installation commands"""
    install_patterns = [
        r'install\s+(\w+)',
        r'setup\s+(\w+)',
        r'(?:how\s+to\s+install|installation\s+(?:for|of))\s+(\w+)'
    ]
    
    for pattern in install_patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            return match.group(1)
    
    return None


def extract_search_keyword_from_prompt(prompt: str) -> Optional[str]:
    """Extract search keyword from prompt"""
    search_patterns = [
        r'(?:search|find)\s+(?:for\s+)?(\w+)',
        r'(?:files?\s+)?(?:containing|with)\s+(\w+)',
        r'look\s+for\s+(\w+)'
    ]
    
    for pattern in search_patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            return match.group(1)
    
    return None
    
    # Build request with conversation context
    messages = memory.get_context_messages()
    
    # If tools should be used, add enforcement message with contextual guidance
    if use_tools:
        # Check for specific ambiguous patterns and provide targeted guidance
        prompt_lower = prompt.lower()
        enforcement_msg = """CRITICAL: Use exact function names from schema. 
Common corrections: backup_files→copy_file, create_csv_file→create_file, find_files→search_files.

TOOL SELECTION RULES:
- "write/create/save/make a guide/file/document" = create_file
- "install commands/how to install" = generate_install_commands
- When in doubt about file creation vs installation, choose create_file for writing content

When use_tools=True, execute tools immediately."""
        
        # Add specific guidance for common confusions
        if any(word in prompt_lower for word in ['guide', 'tutorial', 'write', 'create', 'save']) and any(word in prompt_lower for word in ['file', 'document', 'guide']):
            enforcement_msg += "\n\n🔍 FILE CREATION DETECTED: Use create_file to write content to a file."
        elif any(word in prompt_lower for word in ['install', 'setup', 'how to install']) and not any(word in prompt_lower for word in ['write', 'create', 'save', 'file']):
            enforcement_msg += "\n\n🔍 INSTALLATION REQUEST DETECTED: Use generate_install_commands."
        elif "backup" in prompt_lower or ("copy" in prompt_lower and "file" in prompt_lower):
            enforcement_msg += "\n\n🔍 BACKUP/COPY DETECTED: Use copy_file with src_file and dest_file parameters."
        elif "csv" in prompt_lower and "create" in prompt_lower:
            enforcement_msg += "\n\n🔍 CSV CREATION DETECTED: Use create_file with .csv filename and CSV content as string."
        elif "find" in prompt_lower or "search" in prompt_lower:
            enforcement_msg += "\n\n🔍 SEARCH/FIND DETECTED: Use search_files with keyword parameter."
        elif "json" in prompt_lower and ("create" in prompt_lower or "write" in prompt_lower):
            enforcement_msg += "\n\n🔍 JSON CREATION DETECTED: Use write_json_file with dictionary content."
        
        messages.append({
            "role": "system", 
            "content": enforcement_msg
        })
    
    messages.append({"role": "user", "content": prompt})
    
    request_data = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    if use_tools:
        request_data["tools"] = get_all_tool_schemas()
    
    # Show progress for API call if it might be slow
    progress_thread = None
    if len(messages) > 10:  # Lots of context
        progress_thread = threading.Thread(target=show_progress, args=("Processing with context", 3), daemon=True)
        progress_thread.start()
    
    # Ollama API call with timeout and retry logic
    host = APP_CONFIG['ollama_host']
    max_retries = CONSTANTS['API_MAX_RETRIES']
    timeout = CONSTANTS['API_TIMEOUT']
    response = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Ollama API (attempt {attempt + 1}/{max_retries})")
            response = requests.post(
                f"http://{host}/api/chat", 
                json=request_data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                break
            else:
                logger.warning(f"Ollama API returned status {response.status_code}: {response.text}")
                if attempt == max_retries - 1:
                    print(f"Error: {response.status_code} - {response.text}")
                    return
                
        except requests.exceptions.Timeout:
            logger.warning(f"Ollama API timeout (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                print(f"Error: Ollama API timeout after {timeout}s")
                return
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"Ollama connection failed (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                print("Error: Could not connect to Ollama. Is it running?")
                return
                
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            if attempt == max_retries - 1:
                print(f"Error: {e}")
                return
        
        # Wait before retry
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    if progress_thread:
        progress_thread.join()
    
    # Check if we got a valid response
    if response is None or response.status_code != 200:
        logger.error("Failed to get valid response from Ollama after all retries")
        print("Error: Could not get response from Ollama")
        return
    
    try:
        result = response.json()
        message = result["message"]
        
        # Add space before assistant response
        print()
        assistant_content = message.get('content', '')
        print(f"{CYAN}Assistant: {assistant_content}{RESET}")
        
        # Add assistant message to memory
        tool_calls_data = message.get('tool_calls', None)
        memory.add_message("assistant", assistant_content, tool_calls_data)
        
        # Validate tool usage when expected
        if use_tools and not tool_calls_data and assistant_content:
            logger.warning(f"Expected tools but got conversational response: '{assistant_content[:100]}...'")
            print(f"{CYAN}⚠️  Note: Expected file operation but got conversational response. Try 'tools: {prompt}' to force tool usage.{RESET}")
        elif use_tools and tool_calls_data:
            logger.info(f"Tools used correctly: {len(tool_calls_data)} tool calls")
        
        # Handle tool calls
        if tool_calls_data:
            for tool_call in tool_calls_data:
                original_function_name = tool_call["function"]["name"]
                function_args = tool_call["function"]["arguments"]
                
                print(f"\n🔧 Tool Call: {original_function_name}")
                print(f"Arguments: {json.dumps(function_args, indent=2)}")
                
                # Auto-correct function name if needed
                function_name, was_corrected = auto_correct_function_name(original_function_name)
                if was_corrected:
                    print(f"📝 Using corrected function: {function_name}")
                    # Apply parameter auto-correction for the corrected function
                    function_args = auto_correct_parameters(function_name, original_function_name, function_args)
                    if function_args != tool_call["function"]["arguments"]:
                        print(f"📝 Corrected parameters: {json.dumps(function_args, indent=2)}")
                
                # Validate function exists before execution
                if not _validate_function_exists(function_name):
                    logger.error(f"Unknown function: {function_name}")
                    print(f"❌ Unknown function: {function_name}")
                    _suggest_alternative_function(function_name)
                    continue
                
                # Show progress for potentially slow operations
                slow_operations = ['search_files', 'backup_files', 'compress_file']
                progress_thread = None
                if function_name in slow_operations:
                    progress_thread = threading.Thread(target=show_progress, args=(f"Running {function_name}", 2), daemon=True)
                    progress_thread.start()
                
                # Execute the tool function
                try:
                    if hasattr(file_manager, function_name):
                        result = getattr(file_manager, function_name)(**function_args)
                        print(f"✅ Result: {result}")
                        memory.add_message("tool", f"{function_name}: {result}")
                    elif function_name == "generate_install_commands":
                        from .utils import generate_install_commands
                        result = generate_install_commands(**function_args)
                        print(f"✅ Generated Commands:")
                        print(result)
                        memory.add_message("tool", f"Generated install commands: {result}")
                    else:
                        error_msg = f"Unknown function: {function_name}"
                        logger.error(error_msg)
                        print(f"❌ {error_msg}")
                        _suggest_alternative_function(function_name)
                        memory.add_message("tool", f"Error: {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Error executing {function_name}: {e}"
                    logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    memory.add_message("tool", error_msg)
                
                if progress_thread is not None:
                    progress_thread.join()
                    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from Ollama: {e}")
        print("Error: Invalid response from Ollama")
    except KeyError as e:
        logger.error(f"Missing expected field in Ollama response: {e}")
        print("Error: Unexpected response format from Ollama")
    except Exception as e:
        logger.error(f"Error processing Ollama response: {e}")
        print(f"Error processing response: {e}")


def _validate_function_exists(function_name):
    """Validate that a function exists in our tool schemas"""
    from .tool_schemas import get_all_tool_schemas
    
    available_functions = []
    for schema in get_all_tool_schemas():
        if "function" in schema and "name" in schema["function"]:
            available_functions.append(schema["function"]["name"])
    
    return function_name in available_functions


def _suggest_alternative_function(function_name):
    """Suggest alternative function names for common mistakes"""
    from .tool_schemas import get_all_tool_schemas
    
    # Get available function names
    available_functions = []
    for schema in get_all_tool_schemas():
        if "function" in schema and "name" in schema["function"]:
            available_functions.append(schema["function"]["name"])
    
    # Common mistake mappings
    function_suggestions = {
        'backup_files': 'copy_file',
        'duplicate_file': 'copy_file', 
        'create_csv_file': 'create_file',
        'create_txt_file': 'create_file',
        'write_txt_file': 'create_file',
        'create_json_file': 'write_json_file',
        'save_json': 'write_json_file',
        'find_files': 'search_files',
        'locate_files': 'search_files',
        'list_python_files': 'search_files',
        'read_csv_file': 'read_file',
        'append_to_file': 'write_to_file'
    }
    
    if function_name in function_suggestions:
        suggested = function_suggestions[function_name]
        print(f"💡 Suggestion: Use '{suggested}' instead of '{function_name}'")
    else:
        # Find closest match by similarity
        import difflib
        closest_matches = difflib.get_close_matches(function_name, available_functions, n=3, cutoff=0.3)
        if closest_matches:
            print(f"💡 Did you mean: {', '.join(closest_matches)}?")
        else:
            print(f"💡 Available functions: {', '.join(available_functions)}")


def call_ollama_with_guidance(prompt: str, model: Optional[str], selected_tool: str, debug_info: dict):
    """Call Ollama with strong guidance toward the selected tool"""
    if model is None:
        model = APP_CONFIG['model']
        
    # Build request with conversation context
    messages = memory.get_context_messages()
    
    guidance_msg = f"""CRITICAL: Based on analysis, you should use '{selected_tool}' for this request.

Analysis results:
- Intent: {debug_info['intent']} (confidence: {debug_info['intent_confidence']:.2f})
- Context weight: {debug_info['total_weight']} {debug_info['word_breakdown']}
- Recommended tool: {selected_tool}

Use the recommended tool unless there's a compelling reason not to."""
    
    messages.append({"role": "system", "content": guidance_msg})
    messages.append({"role": "user", "content": prompt})
    
    return call_ollama_api(model, messages, use_tools=True)


def call_ollama_with_hierarchical_prompt(prompt: str, model: Optional[str]):
    """Call Ollama with hierarchical decision tree for ambiguous cases"""
    if model is None:
        model = APP_CONFIG['model']
        
    # Build request with conversation context  
    messages = memory.get_context_messages()
    
    hierarchical_prompt = f"""Follow this EXACT decision tree for: "{prompt}"

**STEP 1: PRIMARY INTENT ANALYSIS**
Identify the PRIMARY action verb:
- CREATE/WRITE/MAKE/GENERATE/BUILD → Content Creation Intent
- INSTALL/SETUP/CONFIGURE → Installation Intent  
- READ/OPEN/VIEW/LIST → File Access Intent

**STEP 2: CONTEXT CONFIRMATION** 
For Content Creation Intent, check for file/document context:
- "guide", "documentation", "file", "content", "text" → USE create_file
- "commands", "installation", "setup instructions" → USE generate_install_commands

**STEP 3: DISAMBIGUATION RULES**
When keywords conflict:
- "write [ANYTHING] guide/doc/file" → ALWAYS create_file (context overrides keyword)
- "install [SOFTWARE]" + NO file/guide context → generate_install_commands

Execute the appropriate tool immediately."""

    messages.append({"role": "system", "content": hierarchical_prompt})
    messages.append({"role": "user", "content": prompt})
    
    return call_ollama_api(model, messages, use_tools=True)


def call_ollama_original_method(prompt: str, model: Optional[str], use_tools: bool):
    """Fallback to original method for non-tool requests"""
    if model is None:
        model = APP_CONFIG['model']
        
    # Build request with conversation context
    messages = memory.get_context_messages()
    messages.append({"role": "user", "content": prompt})
    
    return call_ollama_api(model, messages, use_tools)


def call_ollama_api(model: Optional[str], messages: list, use_tools: bool = True):
    """Core Ollama API call function"""
    # Load current config to check verbose setting
    current_config = load_config()
    verbose_output = current_config.get('verbose_output', False)
    
    if model is None:
        model = APP_CONFIG['model']
        
    request_data = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    if use_tools:
        request_data["tools"] = get_all_tool_schemas()
    
    # Show progress for API call if it might be slow
    progress_thread = None
    if len(messages) > 10:  # Lots of context
        progress_thread = threading.Thread(target=show_progress, args=("Processing with context", 3), daemon=True)
        progress_thread.start()
    
    # Ollama API call with timeout and retry logic
    host = APP_CONFIG['ollama_host']
    max_retries = CONSTANTS['API_MAX_RETRIES']
    timeout = CONSTANTS['API_TIMEOUT']
    response = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Ollama API (attempt {attempt + 1}/{max_retries})")
            response = requests.post(
                f"http://{host}/api/chat", 
                json=request_data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                break
            else:
                logger.warning(f"Ollama API returned status {response.status_code}: {response.text}")
                if attempt == max_retries - 1:
                    print(f"Error: {response.status_code} - {response.text}")
                    return
                
        except requests.exceptions.Timeout:
            logger.warning(f"Ollama API timeout (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                print(f"Error: Ollama API timeout after {timeout}s")
                return
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"Ollama connection failed (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                print("Error: Could not connect to Ollama. Is it running?")
                return
                
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            if attempt == max_retries - 1:
                print(f"Error: {e}")
                return
        
        # Wait before retry
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    if progress_thread:
        progress_thread.join()
    
    # Check if we got a valid response
    if response is None or response.status_code != 200:
        logger.error("Failed to get valid response from Ollama after all retries")
        print("Error: Could not get response from Ollama")
        return
    
    # Handle the response
    return handle_ollama_response(response)


def handle_ollama_response(response):
    """Handle Ollama API response with tool execution"""
    # Load current config to check verbose setting
    current_config = load_config()
    verbose_output = current_config.get('verbose_output', False)
    
    try:
        result = response.json()
        message = result["message"]
        
        # Add space before assistant response
        print()
        assistant_content = message.get('content', '')
        print(f"{CYAN}Assistant: {assistant_content}{RESET}")
        
        # Add assistant message to memory
        tool_calls_data = message.get('tool_calls', None)
        memory.add_message("assistant", assistant_content, tool_calls_data)
        
        # Validate tool usage when expected (only show in verbose mode)
        if not tool_calls_data and assistant_content and verbose_output:
            logger.warning(f"Expected tools but got conversational response: '{assistant_content[:100]}...'")
            print(f"{CYAN}⚠️  Note: Expected file operation but got conversational response. Try 'tools: {assistant_content}' to force tool usage.{RESET}")
        elif tool_calls_data:
            logger.info(f"Tools used correctly: {len(tool_calls_data)} tool calls")
        
        # Handle tool calls
        if tool_calls_data:
            for tool_call in tool_calls_data:
                original_function_name = tool_call["function"]["name"]
                function_args = tool_call["function"]["arguments"]
                
                if verbose_output:
                    print(f"\n🔧 Tool Call: {original_function_name}")
                    print(f"Arguments: {json.dumps(function_args, indent=2)}")
                
                # Auto-correct function name if needed
                function_name, was_corrected = auto_correct_function_name(original_function_name)
                if was_corrected and verbose_output:
                    print(f"📝 Using corrected function: {function_name}")
                    # Apply parameter auto-correction for the corrected function
                    function_args = auto_correct_parameters(function_name, original_function_name, function_args)
                    if function_args != tool_call["function"]["arguments"]:
                        print(f"📝 Corrected parameters: {json.dumps(function_args, indent=2)}")
                elif was_corrected:
                    # Still apply correction even in non-verbose mode
                    function_args = auto_correct_parameters(function_name, original_function_name, function_args)
                
                # Validate function exists before execution
                if not _validate_function_exists(function_name):
                    logger.error(f"Unknown function: {function_name}")
                    if verbose_output:
                        print(f"❌ Unknown function: {function_name}")
                        _suggest_alternative_function(function_name)
                    continue
                
                # Show progress for potentially slow operations
                slow_operations = ['search_files', 'backup_files', 'compress_file']
                progress_thread = None
                if function_name in slow_operations:
                    progress_thread = threading.Thread(target=show_progress, args=(f"Running {function_name}", 2), daemon=True)
                    progress_thread.start()
                
                # Execute the tool function
                try:
                    if hasattr(file_manager, function_name):
                        result = getattr(file_manager, function_name)(**function_args)
                        # Show results based on verbose setting
                        if verbose_output:
                            print(f"✅ Result: {result}")
                        else:
                            print(f"🔧 {function_name} → {format_tool_result(function_name, result)}")
                        memory.add_message("tool", f"{function_name}: {result}")
                    elif function_name == "generate_install_commands":
                        from .utils import generate_install_commands
                        result = generate_install_commands(**function_args)
                        if verbose_output:
                            print(f"✅ Generated Commands:")
                            print(result)
                        else:
                            print(f"🔧 {function_name} → Installation commands generated")
                        memory.add_message("tool", f"Generated install commands: {result}")
                    else:
                        error_msg = f"Unknown function: {function_name}"
                        logger.error(error_msg)
                        if verbose_output:
                            print(f"❌ {error_msg}")
                            _suggest_alternative_function(function_name)
                        memory.add_message("tool", f"Error: {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Error executing {function_name}: {e}"
                    logger.error(error_msg)
                    if verbose_output:
                        print(f"❌ {error_msg}")
                    memory.add_message("tool", error_msg)
                
                if progress_thread is not None:
                    progress_thread.join()
                    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from Ollama: {e}")
        print("❌ Invalid response from Ollama")
    except Exception as e:
        logger.error(f"Error processing Ollama response: {e}")
        print(f"❌ Error processing response: {e}")
