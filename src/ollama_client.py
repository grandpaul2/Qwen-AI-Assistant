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

from .config import APP_CONFIG, CONSTANTS, CYAN, RESET
from .memory import memory
from .file_manager import file_manager
from .utils import show_progress
from .tool_schemas import get_all_tool_schemas

# Configure logging
logger = logging.getLogger(__name__)


def detect_file_intent(prompt: str) -> bool:
    """Enhanced contextual detection for file operations"""
    prompt_lower = prompt.lower()
    
    # File action patterns (contextual)
    file_action_patterns = [
        # Direct commands
        r'\b(create|make|generate|build)\s+.*\b(file|folder|directory)\b',
        r'\b(save|write|store|put)\s+.*\b(to|in|into)\s+.*\b(workspace|folder|directory)\b',
        r'\b(read|open|view|show|display)\s+.*\b(file|document)\b',
        
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
    
    for task, function in task_mappings.items():
        if task in prompt_lower:
            enhanced_prompt += f"\n[FUNCTION HINT: For '{task}' operations, use '{function}']"
    
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
        
        print(f"🔧 Parameter mapping applied: {mapping}")
        return corrected_args
    
    return function_args


def call_ollama_with_tools(prompt: str, model: Optional[str] = None, use_tools: bool = True):
    """Call Ollama with conversation memory and tools"""
    
    if model is None:
        model = APP_CONFIG['model']
    
    # Enhance prompt for better function selection
    if use_tools:
        prompt = enhance_prompt_for_function_selection(prompt)
    
    # Add user message to memory
    memory.add_message("user", prompt)
    
    # Build request with conversation context
    messages = memory.get_context_messages()
    
    # If tools should be used, add enforcement message
    if use_tools:
        # Check for specific ambiguous patterns and provide targeted guidance
        prompt_lower = prompt.lower()
        enforcement_msg = """🚨 CRITICAL FUNCTION SELECTION RULES 🚨

ONLY USE THESE EXACT FUNCTION NAMES (verify before calling):
✅ create_file, write_to_file, read_file, write_json_file, read_json_file, copy_file, delete_file, create_folder, delete_folder, list_files, search_files, move_file, write_txt_file, write_md_file, write_json_from_string

🚫 THESE FUNCTIONS DO NOT EXIST (common mistakes):
❌ backup_files → ✅ use copy_file instead
❌ create_csv_file → ✅ use create_file instead
❌ create_txt_file → ✅ use create_file instead
❌ find_files → ✅ use search_files instead
❌ duplicate_file → ✅ use copy_file instead
❌ read_csv_file → ✅ use read_file instead
❌ make_file → ✅ use create_file instead
❌ generate_file → ✅ use create_file instead

⚠️ MANDATORY CHECK: Before calling ANY function, verify the exact function name exists in the ✅ list above. If it doesn't exist, choose the correct alternative from the ✅ list.

🚨 CRITICAL ENFORCEMENT: When use_tools=True is detected, you MUST use tools immediately. Never provide conversational instructions when tools are available. Execute the file operation directly."""
        
        # Add specific guidance for common confusions
        if "backup" in prompt_lower or ("copy" in prompt_lower and "file" in prompt_lower):
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
