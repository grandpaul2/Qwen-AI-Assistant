# Implementation Plan Analysis - Tool Selection Research Results

## Key Insights from Research

### Core Problem Identification
The research confirms our issue is **"contextual intent prioritization failure"** - the model prioritizes individual keywords over contextual phrases due to **prompt encoding hierarchy** problems, not insufficient instructions.

### Most Promising Solutions (In Order of Impact)

## 1. Hierarchical Decision Tree Prompt (IMMEDIATE IMPLEMENTATION)
**Why This First:** Direct solution to our "git guide" vs "git install" problem
**Expected Impact:** 70-85% accuracy improvement
**Implementation Complexity:** Low - just replace system prompt

### Current System Prompt Structure:
```
You are WorkspaceAI... [big block of rules and patterns]
```

### Proposed Hierarchical Structure:
```
STEP 1: PRIMARY INTENT ANALYSIS (Action Verb Priority)
STEP 2: CONTEXT CONFIRMATION (File/Document Context)  
STEP 3: DISAMBIGUATION RULES (Context Overrides Keywords)
```

## 2. Context Weighting Implementation (WEEK 2)
**Why Second:** Builds on decision tree with numerical prioritization
**Expected Impact:** 85-95% accuracy
**Implementation:** Add weight calculations to prompt

## 3. Two-Stage Architecture (WEEK 3) 
**Why Third:** Fundamental architecture change for scalability
**Expected Impact:** 95%+ accuracy + better debugging
**Implementation:** Separate intent classification from tool selection

## Implementation Strategy

### Phase 1: Hierarchical Decision Tree (This Week)

#### Files to Modify:
1. `src/config.py` - Replace SYSTEM_PROMPT
2. `src/ollama_client.py` - Update enforcement message to align
3. Test with exact failing examples

#### Specific Changes:

**Step 1:** Replace the current SYSTEM_PROMPT in `src/config.py`:
```python
'SYSTEM_PROMPT': """You are WorkspaceAI. Follow this EXACT decision tree for tool selection:

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

**EXECUTION RULE:** Follow the decision tree path. Do not skip steps. Context words (guide, file, document) ALWAYS override individual keywords."""
```

**Step 2:** Update enforcement message in `ollama_client.py`:
```python
enforcement_msg = """CRITICAL: Follow the 3-step decision tree from system prompt.
Step 1: Identify primary verb (CREATE/INSTALL/READ)
Step 2: Confirm context (file/guide vs commands/setup)  
Step 3: Apply disambiguation (context overrides keywords)

DECISION EXAMPLES:
"write me a guide for git" → Step 1: CREATE, Step 2: guide context → create_file
"install git" → Step 1: INSTALL, Step 2: no file context → generate_install_commands"""
```

**Step 3:** Test with failing examples:
- "write me a guide for git"
- "create documentation about docker" 
- "install git on ubuntu"

### Phase 2: Context Weighting (Week 2)

Add numerical weighting system to the decision tree:
- HIGH-PRIORITY SIGNALS (Weight: 10): Action verbs + file context
- MEDIUM-PRIORITY SIGNALS (Weight: 5): File operations  
- LOW-PRIORITY SIGNALS (Weight: 1): Individual keywords

### Phase 3: Two-Stage Architecture (Week 3)

Split into separate functions:
1. `classify_intent()` - Returns CONTENT_CREATION/SOFTWARE_INSTALLATION/FILE_MANAGEMENT
2. `select_tool_for_intent()` - Maps intent to specific tool

## Risk Assessment

### Low Risk Changes (Phase 1):
- System prompt replacement
- Enforcement message update
- No architectural changes

### Medium Risk Changes (Phase 2):
- Adding weight calculations
- More complex prompt logic
- Potential performance impact

### High Risk Changes (Phase 3):
- Architectural restructuring
- Two API calls instead of one
- Major code changes

## Validation Plan

### Phase 1 Testing:
```
Test Cases:
1. "write me a guide for git" → Expected: create_file
2. "create documentation about docker" → Expected: create_file  
3. "install git on ubuntu" → Expected: generate_install_commands
4. "make a tutorial on python" → Expected: create_file
5. "setup docker installation" → Expected: generate_install_commands
```

### Success Criteria:
- Phase 1: 4/5 test cases correct (80% improvement)
- Phase 2: 5/5 test cases correct + complex scenarios
- Phase 3: Consistent behavior + improved debugging

## Questions Before Implementation:

1. **Should we implement Phase 1 immediately?** The hierarchical decision tree is low-risk and directly addresses our core problem.

2. **Do you want to backup the current system before changes?** We should save current working config.

3. **Should we implement all phases or evaluate after each?** Recommend implementing Phase 1, testing thoroughly, then deciding on Phase 2.

4. **Any concerns about the decision tree approach?** It's more explicit than our current system but should be more reliable.

## My Recommendation:

**Start with Phase 1 immediately** because:
- Low risk (just prompt changes)
- Direct solution to our core problem
- Research-backed approach
- Easy to revert if it doesn't work
- Expected 70-85% improvement

The hierarchical decision tree directly addresses the "write me a guide for git" → installation commands problem by making the AI explicitly analyze the primary verb first, then context, then apply disambiguation rules.

**Ready to implement Phase 1?**
