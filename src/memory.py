"""
Memory management for WorkspaceAI
Handles conversation history, summarization, and context building
"""

import os
import json
import shutil
import requests
from datetime import datetime
from .config import CONSTANTS, get_memory_path

class MemoryManager:
    """Manages conversation memory with rolling history"""
    
    def __init__(self, config=None):
        if config is None:
            from .config import APP_CONFIG
            config = APP_CONFIG
        
        self.memory_file = os.path.join(get_memory_path(), "memory.json")
        self.current_conversation = []
        self.recent_conversations = []  # Last 2 full conversations
        self.summarized_conversations = []  # Next 20 summarized
        self.load_memory()
    
    def load_memory(self):
        """Load persistent memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.current_conversation = data.get('current_conversation', [])
                self.recent_conversations = data.get('recent_conversations', [])
                self.summarized_conversations = data.get('summarized_conversations', [])
                print(f"📖 Loaded memory: {len(self.recent_conversations)} recent + {len(self.summarized_conversations)} summarized conversations")
            except Exception as e:
                print(f"⚠️ Could not load memory: {e}")
                self.reset_memory()
        else:
            self.reset_memory()
    
    def save_memory(self):
        """Save memory to file after each response"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            data = {
                'current_conversation': self.current_conversation,
                'recent_conversations': self.recent_conversations,
                'summarized_conversations': self.summarized_conversations,
                'last_updated': datetime.now().isoformat()
            }
            
            # Create backup before overwriting
            if os.path.exists(self.memory_file):
                backup_file = self.memory_file + ".backup"
                shutil.copy2(self.memory_file, backup_file)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.memory_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            if os.path.exists(self.memory_file):
                os.replace(temp_file, self.memory_file)
            else:
                os.rename(temp_file, self.memory_file)
                
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")
    
    def add_message(self, role, content, tool_calls=None):
        """Add message to current conversation"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        if tool_calls:
            message['tool_calls'] = tool_calls
        
        self.current_conversation.append(message)
        
        # Auto-save after each message (synchronous for reliability)
        self.save_memory()
        
        # Import logger here to avoid circular imports
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Added {role} message to conversation, total messages: {len(self.current_conversation)}")
    
    def start_new_conversation(self):
        """Move current conversation to recent and start fresh"""
        if not self.current_conversation:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug("No current conversation to save")
            return
        
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Moving conversation with {len(self.current_conversation)} messages to recent")
        
        # Add current to recent conversations
        conversation_data = {
            'date': datetime.now().isoformat(),
            'messages': self.current_conversation.copy()
        }
        self.recent_conversations.insert(0, conversation_data)
        
        # Keep only last 2 recent conversations
        if len(self.recent_conversations) > CONSTANTS['MAX_RECENT_CONVERSATIONS']:
            # Move oldest recent to summarized
            oldest = self.recent_conversations.pop()
            logger.debug(f"Moving oldest recent conversation to summarized (had {len(oldest['messages'])} messages)")
            summary = self.summarize_conversation(oldest['messages'])
            self.summarized_conversations.insert(0, {
                'date': oldest['date'],
                'summary': summary
            })
        
        # Keep only 20 summarized conversations
        self.summarized_conversations = self.summarized_conversations[:CONSTANTS['MAX_SUMMARIZED_CONVERSATIONS']]
        
        # Clear current conversation
        self.current_conversation = []
        self.save_memory()
        print(f"Started new conversation (previous conversation with {len(conversation_data['messages'])} messages saved to memory)")
        logger.info(f"New conversation started - Recent: {len(self.recent_conversations)}, Summarized: {len(self.summarized_conversations)}")
    
    def summarize_conversation(self, messages):
        """Create AI summary of conversation"""
        try:
            # Build summary prompt
            conversation_text = ""
            for msg in messages[-CONSTANTS['MEMORY_CONTEXT_MESSAGES']:]:  # Last 10 messages only
                if msg['role'] in ['user', 'assistant']:
                    conversation_text += f"{msg['role']}: {msg['content'][:200]}\n"
            
            if not conversation_text.strip():
                return "Empty conversation"
            
            summary_prompt = f"Summarize this conversation in 2-3 sentences, focusing on key topics, files created/modified, and important context:\n\n{conversation_text}"
            
            response = requests.post("http://localhost:11434/api/chat", json={
                "model": "qwen2.5:3b",
                "messages": [{"role": "user", "content": summary_prompt}],
                "stream": False
            }, timeout=CONSTANTS['SUMMARY_TIMEOUT'])
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Conversation from {messages[0]['timestamp'][:10]} with {len(messages)} messages"
        except:
            return f"Conversation from {messages[0]['timestamp'][:10]} with {len(messages)} messages"
    
    def get_context_messages(self):
        """Build context from memory for API calls"""
        context_messages = []
        
        # Add system prompt for tool usage
        context_messages.append({
            "role": "system", 
            "content": CONSTANTS['SYSTEM_PROMPT']
        })
        
        # Add summaries as system context
        if self.summarized_conversations:
            summaries_text = "Previous conversation context:\n"
            for conv in reversed(self.summarized_conversations):  # Oldest first
                date = conv['date'][:10]
                summaries_text += f"- {date}: {conv['summary']}\n"
            context_messages.append({"role": "system", "content": summaries_text})
        
        # Add recent conversations
        for conv in reversed(self.recent_conversations):  # Oldest first
            for msg in conv['messages']:
                if msg['role'] in ['user', 'assistant']:
                    context_messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        # Add current conversation
        for msg in self.current_conversation:
            if msg['role'] in ['user', 'assistant']:
                context_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        return context_messages
    
    def reset_memory(self):
        """Reset all memory"""
        self.current_conversation = []
        self.recent_conversations = []
        self.summarized_conversations = []


# Global memory manager instance
memory = MemoryManager()
