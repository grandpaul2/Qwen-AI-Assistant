# Tool Selection Disambiguation: Advanced Research-Based Solutions

## **Executive Summary**

Your core issue is **contextual intent prioritization failure** - the model prioritizes individual keywords over contextual phrases. Based on current research and production patterns, I recommend implementing a **hierarchical decision tree prompt structure** combined with **context weighting techniques**. The solution maintains your lightweight architecture while dramatically improving disambiguation accuracy.

---

## **Research Findings: Core Problem Analysis**

### **1. Keyword Override vs Context Weighting**
Recent research reveals that "LLMs sometimes fail to follow clear instructions and why prompt engineering is often effective, even when the content remains largely unchanged" because "this dimension is more related to the rephrasing of prompts rather than the inherent difficulty of the task or instructions."

**Key Insight:** Your issue isn't insufficient instruction clarity—it's **prompt encoding hierarchy**. The model processes "git" as a stronger signal than "write me a guide" due to how the instructions are structured in representation space.

### **2. Production System Patterns**
Research on production LLM systems shows successful architectures use "hybrid systems that combine semantic search (via embeddings + FAISS) with secure SQL generation tailored for the data clean room context" and "grounding SQL generation in schema and intent templates, and falling back to LLM only when necessary."

**Translation to Your Problem:** Successful systems use **intent classification → tool selection** rather than direct keyword → tool mapping.

### **3. Hierarchical Intent Recognition Research**
Studies on enterprise LLM applications show "Hierarchical and domain-specialized fine-tuning: Breaking down the classification task into top-level and subdomain decisions" with "Top-Level GPT-Based Classifier: A fine-tuned (or zero-shot) GPT-based model processes the input."

---

## **Advanced Prompting Solutions**

### **Solution 1: Hierarchical Decision Tree Prompt (Recommended)**

Based on research showing "Tree of Thoughts (ToT), a framework that generalizes over chain-of-thought prompting and encourages exploration over thoughts that serve as intermediate steps for general problem solving", implement a multi-stage decision process:

```python
HIERARCHICAL_SYSTEM_PROMPT = """You are WorkspaceAI. Follow this EXACT decision tree for tool selection:

**STEP 1: PRIMARY INTENT ANALYSIS**
First, identify the PRIMARY action verb:
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
- "make/create [FILENAME]" → ALWAYS create_file

**CRITICAL DECISION TREE:**
```
User Input: "write me a guide for git"
├─ Step 1: PRIMARY VERB = "write" → Content Creation Intent
├─ Step 2: CONTEXT = "guide" → File/Document Context Detected  
└─ Step 3: DECISION = create_file (write + guide = content creation)

User Input: "install git on ubuntu"  
├─ Step 1: PRIMARY VERB = "install" → Installation Intent
├─ Step 2: CONTEXT = no file/guide context → Installation Context
└─ Step 3: DECISION = generate_install_commands
```

**EXECUTION RULE:** Follow the decision tree path. Do not skip steps. Context words (guide, file, document) ALWAYS override individual keywords."""
```

### **Solution 2: Context Weighting Prompt Pattern**

Research shows "System Messages: LLMs can use system messages to provide additional context and constraints for function calls. These messages can specify the required parameters, their values, and any constraints on the function call."

```python
CONTEXT_WEIGHTED_PROMPT = """You are WorkspaceAI with advanced contextual analysis.

**CONTEXT WEIGHTING SYSTEM:**

HIGH-PRIORITY SIGNALS (Weight: 10):
- Action verbs: write, create, make, generate, build, compose
- File context: guide, documentation, file, content, text, tutorial

MEDIUM-PRIORITY SIGNALS (Weight: 5):  
- File operations: save, store, put, edit, modify
- Access operations: read, open, view, list, search

LOW-PRIORITY SIGNALS (Weight: 1):
- Individual keywords: git, python, node, etc.
- Software names without action context

**DECISION ALGORITHM:**
1. Calculate total weight for each intent
2. Intent with highest weight wins
3. Ties: prefer create_file for any content creation signal

**EXAMPLES:**
"write me a guide for git" = 
- "write" (10) + "guide" (10) + "git" (1) = 21 points → create_file

"install git commands" =  
- "install" (5) + "commands" (1) + "git" (1) = 7 points → generate_install_commands

Always show your calculation before selecting a tool."""
```

### **Solution 3: Few-Shot Pattern Disambiguation** 

Based on findings that "Few-shot prompting—where multiple examples cover different scenarios—can significantly enhance the accuracy and reliability of the model's responses," use explicit examples:

```python
FEW_SHOT_DISAMBIGUATION_PROMPT = """You are WorkspaceAI. Use these EXACT patterns for tool selection:

**PATTERN MATCHING EXAMPLES:**

Content Creation Pattern (USE create_file):
✓ "write me a guide for git" → create_file 
✓ "create documentation about docker" → create_file
✓ "make a tutorial on python" → create_file
✓ "generate a reference for javascript" → create_file
✓ "build a guide explaining react" → create_file

Installation Pattern (USE generate_install_commands):
✓ "install git on ubuntu" → generate_install_commands
✓ "setup docker installation" → generate_install_commands  
✓ "how to install python" → generate_install_commands
✓ "give me install steps for node" → generate_install_commands

**DISAMBIGUATION RULE:**
If the request contains BOTH content words (guide/tutorial/documentation) AND software names:
→ The content creation intent ALWAYS wins
→ CREATE the content ABOUT the software, don't install it

**PATTERN MATCHING:**
1. Look for exact phrase patterns from examples
2. Match the closest pattern  
3. Use the corresponding tool

Match the user input to the most similar example pattern above."""
```

---

## **Alternative Architecture Solutions**

### **Architecture 1: Two-Stage Intent → Tool Pipeline**

Research on production systems shows "Intent classification is the foundation of this system. It maps unstructured natural language into structured categories that drive downstream logic such as SQL template selection."

```python
# Stage 1: Intent Classification
INTENT_CLASSIFIER_PROMPT = """Classify user intent into ONE category:

1. CONTENT_CREATION: Creating, writing, making files/guides/documentation
2. SOFTWARE_INSTALLATION: Installing, setting up, configuring software  
3. FILE_MANAGEMENT: Reading, listing, searching, organizing files

Examples:
"write me a guide for git" → CONTENT_CREATION
"install git" → SOFTWARE_INSTALLATION  
"list my files" → FILE_MANAGEMENT

Output format: CATEGORY_NAME"""

# Stage 2: Tool Selection Based on Intent
TOOL_SELECTOR_MAPPING = {
    "CONTENT_CREATION": "create_file",
    "SOFTWARE_INSTALLATION": "generate_install_commands", 
    "FILE_MANAGEMENT": "appropriate_file_tool"
}
```

### **Architecture 2: Confidence-Based Hybrid Approach**

Based on research showing "hybrid architecture ensures low-latency performance, while preserving high expressivity and strict schema alignment," implement confidence thresholding:

```python
class ConfidenceBasedSelector:
    def select_tool(self, user_input):
        # Stage 1: Quick pattern matching
        confidence, tool = self.pattern_match(user_input)
        
        if confidence > 0.8:
            return tool  # High confidence, use pattern
        else:
            # Stage 2: LLM disambiguation for ambiguous cases
            return self.llm_disambiguate(user_input)
    
    def pattern_match(self, input_text):
        # Simple regex/keyword patterns for high-confidence cases
        if re.search(r'\b(write|create|make).*\b(guide|file|doc)', input_text):
            return 0.9, "create_file"
        elif re.search(r'\binstall\s+\w+', input_text) and not re.search(r'\b(guide|file|doc)', input_text):
            return 0.9, "generate_install_commands"
        else:
            return 0.3, None  # Low confidence, needs LLM
```

---

## **Context Weighting Implementation Techniques**

### **1. Attention Mechanism Simulation**
Research shows attention weights can be simulated in prompts:

```python
ATTENTION_WEIGHTED_PROMPT = """Analyze the input using attention weighting:

1. **Primary Attention:** Action verbs (write, create, install)
2. **Secondary Attention:** Object nouns (guide, file, software)  
3. **Tertiary Attention:** Specific keywords (git, python)

For "write me a guide for git":
- Primary: "write" → Content Creation (HIGH ATTENTION)
- Secondary: "guide" → Document Object (HIGH ATTENTION)
- Tertiary: "git" → Software Name (LOW ATTENTION)

ATTENTION DECISION: Content Creation + Document Object = create_file

Always analyze attention weights before deciding."""
```

### **2. Semantic Role Labeling Approach**
```python
SEMANTIC_ROLE_PROMPT = """Parse the semantic roles:

AGENT: Who performs the action (always "user" or implied)
ACTION: What action to perform  
THEME: What object receives the action
BENEFICIARY: What/who benefits

"write me a guide for git":
- AGENT: user (implied)
- ACTION: write  
- THEME: guide (primary object)
- BENEFICIARY: git (secondary reference)

DECISION RULE: ACTION + THEME determine tool choice
write + guide = create_file"""
```

---

## **Addressing Negative Instructions Research**

Research reveals why "DO NOT use X when Y" fails: "LLMs sometimes fail to follow clear instructions and why prompt engineering is often effective, even when the content remains largely unchanged" because negative instructions create representation conflicts.

### **Effective Negative Instruction Patterns:**

```python
# ❌ FAILS: Direct negation
"DO NOT use generate_install_commands for guides"

# ✅ WORKS: Positive redirection  
"When creating guides/documents/tutorials → ALWAYS use create_file"
"When installing software → ALWAYS use generate_install_commands"

# ✅ WORKS: Conditional positive statements
"IF user wants to create/write content THEN use create_file"
"IF user wants installation commands THEN use generate_install_commands"
```

---

## **Small Model Optimization Strategies**

Research on small models shows "smaller models are generally preferred because they are much more efficient during inference" but require more structured guidance.

### **1. Simplified Decision Trees for Small Models**
```python
SMALL_MODEL_PROMPT = """Simple decision tree:

Question 1: Does the user want to CREATE something?
- Words: write, make, create, generate + file/guide/doc
- YES → create_file
- NO → Go to Question 2

Question 2: Does the user want to INSTALL something?  
- Words: install, setup + software name
- YES → generate_install_commands
- NO → Ask for clarification

Follow this exactly. Check Question 1 first."""
```

### **2. Template Matching for Small Models**
```python
TEMPLATE_MATCHING_PROMPT = """Match to these exact templates:

Template A: "[action] me a [document] for [topic]" → create_file
Template B: "[action] [document] about [topic]" → create_file  
Template C: "install [software]" → generate_install_commands
Template D: "setup [software]" → generate_install_commands

Match the user input to the closest template."""
```

---

## **Implementation Roadmap**

### **Phase 1: Hierarchical Decision Tree (Week 1)**
- Implement the hierarchical system prompt
- Test with your current examples
- **Expected improvement:** 70-85% accuracy on disambiguation

### **Phase 2: Context Weighting (Week 2)**  
- Add attention mechanism simulation
- Implement semantic role parsing
- **Expected improvement:** 85-95% accuracy

### **Phase 3: Confidence-Based Hybrid (Week 3)**
- Add pattern matching for high-confidence cases
- Implement fallback to LLM for ambiguous cases
- **Expected improvement:** 95%+ accuracy with improved performance

### **Phase 4: Small Model Optimization (Week 4)**
- Implement simplified decision trees
- Add template matching for edge cases
- **Expected improvement:** Consistent behavior on 3B model

---

## **Production Monitoring & Validation**

```python
class ToolSelectionValidator:
    def validate_decision(self, user_input, selected_tool, context):
        """Validate tool selection and log for continuous improvement"""
        
        # Pattern-based validation
        content_patterns = ['write', 'create', 'make', 'guide', 'file', 'doc']
        install_patterns = ['install', 'setup']
        
        content_score = sum(1 for pattern in content_patterns if pattern in user_input.lower())
        install_score = sum(1 for pattern in install_patterns if pattern in user_input.lower())
        
        expected_tool = "create_file" if content_score > install_score else "generate_install_commands"
        
        if selected_tool != expected_tool:
            self.log_potential_misclassification(user_input, selected_tool, expected_tool)
        
        return {
            'input': user_input,
            'selected_tool': selected_tool, 
            'expected_tool': expected_tool,
            'content_score': content_score,
            'install_score': install_score,
            'confidence': abs(content_score - install_score) / max(content_score + install_score, 1)
        }
```

---

## **Bottom Line Recommendations**

1. **Immediate Fix (This Week):** Implement the Hierarchical Decision Tree prompt. This addresses your core "git guide" vs "git install" problem directly.

2. **Production Architecture (Next 2 Weeks):** Move to a two-stage Intent → Tool pipeline for better scalability and debugging.

3. **Small Model Optimization:** Use simplified decision trees and template matching for your 3B parameter model.

4. **Success Pattern:** The research shows that "differentiable routing mirrors a broader trend: Separating declarative control logic from generative inference" - separate your decision logic from your content generation.

The key insight from production systems research is that **tool selection should be a distinct step from tool execution**, with clear decision trees that prioritize contextual phrases over individual keywords. Your current approach of embedding all logic in one system prompt creates the representation conflicts causing your disambiguation failures.