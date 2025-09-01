# Automated Bot Enhancement Testing

Quick command-line tools for testing and recording bot logic enhancement data.

## 🚀 Quick Start

### Windows (PowerShell)
```powershell
.\test_bot.ps1 quick
```

### Windows (Command Prompt)
```cmd
test_bot.bat quick
```

### Linux/Mac
```bash
./test_bot.sh quick
```

### Direct Python
```bash
python tests/quick_test_commands.py quick
```

## 📋 Available Commands

| Command | Description | Duration | Output |
|---------|-------------|----------|---------|
| `quick` | Quick validation (3 scenarios) | ~30 seconds | Pass/Fail + Score |
| `context` | Context awareness test | ~45 seconds | Context building analysis |
| `single` | Complex scenario test | ~15 seconds | Multi-tool handling |
| `benchmark` | Performance timing | ~10 seconds | Response time metrics |
| `full` | Complete automated suite | ~2-3 minutes | Comprehensive report |
| `report` | Show latest results | ~5 seconds | Last test summary |
| `all` | Run all test types | ~5 minutes | Complete validation |

## 🧪 Test Types Explained

### ⚡ Quick Test (`quick`)
**Purpose**: Fast validation of core enhancements
**Scenarios**:
- "Create a file called test.txt"
- "Add some content to that file" 
- "Create a Python project structure"

**Measures**: Context awareness, tool selection, basic enhancement functionality

**Success Criteria**: Average score ≥ 5.0/10

### 🧠 Context Test (`context`)
**Purpose**: Validate context building and reference resolution
**Scenarios**:
- "Create a Python script called data_processor.py"
- "Add error handling to that script"
- "Create a test file for it"
- "Show me both files"

**Measures**: Context accumulation, implicit references ("that script", "it", "both files")

**Success Criteria**: Average score ≥ 6.0/10

### 🎯 Single Complex Test (`single`)
**Purpose**: Test handling of complex multi-step requests
**Scenario**: "Create a complete Python project structure with src/, tests/, docs/, and all the standard config files. Make it ready for git."

**Measures**: Multi-step detection, parameter extraction, complex tool coordination

**Success Criteria**: Score ≥ 6.0/10

### ⚡ Benchmark Test (`benchmark`)
**Purpose**: Validate response time performance
**Scenarios**: 5 simple commands with timing measurement

**Measures**: Average response time, maximum response time

**Success Criteria**: Average < 0.5s, Max < 1.0s

### 📊 Full Automated Test (`full`)
**Purpose**: Comprehensive enhancement validation
**Scenarios**: 10 diverse scenarios covering all enhancement phases

**Measures**: All enhancement features, detailed metrics, feature analysis

**Success Criteria**: Average score ≥ 6.0/10

## 📊 Understanding Results

### Scoring System (0-10 scale):
- **8-10**: Excellent - Full enhancement working
- **6-8**: Good - Most enhancements working  
- **4-6**: Partial - Some enhancements working
- **0-4**: Needs Work - Limited enhancements

### Key Metrics:
- **Context Awareness**: Bot remembers previous operations
- **Smart Tool Selection**: Appropriate tools chosen based on context
- **Reference Resolution**: Understanding of "that file", "it", etc.
- **Multi-step Detection**: Recognition of complex requests
- **Response Time**: Speed of processing

## 💾 Results Storage

All test results are automatically saved in `test_results/`:

```
test_results/
├── quick_test_20250901_143022.json
├── context_test_20250901_143105.json
├── single_test_20250901_143145.json
├── benchmark_20250901_143200.json
└── automated_test_results_20250901_143300.json
```

### Result File Format:
```json
{
  "test_type": "quick_validation",
  "timestamp": "2025-09-01T14:30:22",
  "scenarios": [...],
  "scores": [7.0, 8.5, 6.0],
  "average_score": 7.17,
  "status": "PASS"
}
```

## 🔄 Regular Testing Workflow

### Daily Development:
```bash
# Quick check during development
.\test_bot.ps1 quick

# Check context awareness after changes
.\test_bot.ps1 context
```

### Before Commits:
```bash
# Full validation before committing
.\test_bot.ps1 all
```

### Performance Monitoring:
```bash
# Regular performance checks
.\test_bot.ps1 benchmark
```

### Results Review:
```bash
# Check latest results
.\test_bot.ps1 report
```

## 🎯 Enhancement Validation

### What Good Results Look Like:

#### ✅ Enhanced Context Awareness:
- References to previous operations
- Context factors > 0 in subsequent requests
- Higher scores on sequence tests

#### ✅ Smart Tool Selection:
- Appropriate primary tools chosen
- Confidence scores > 0.7
- Multi-step detection for complex requests

#### ✅ Response Intelligence:
- Fast response times (< 0.5s average)
- Consistent high scores across scenarios
- Error-free processing

### What to Investigate:

#### ⚠️ Low Context Scores:
- Context awareness not working
- No memory between requests
- Generic responses regardless of history

#### ⚠️ Poor Tool Selection:
- Wrong tools chosen for scenarios
- Low confidence scores
- No multi-step detection

#### ⚠️ Slow Performance:
- Response times > 1.0s
- Processing bottlenecks
- Inefficient algorithms

## 🐛 Troubleshooting

### Common Issues:

**Import Errors**: 
```bash
# Ensure you're in the project root
cd /path/to/WorkspaceAI_project
python tests/quick_test_commands.py quick
```

**Permission Errors (Linux/Mac)**:
```bash
chmod +x test_bot.sh
./test_bot.sh quick
```

**PowerShell Execution Policy (Windows)**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\test_bot.ps1 quick
```

**Module Not Found**:
```bash
# Install requirements
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

## 📈 Tracking Progress

### Baseline Measurements:
1. Run initial tests: `.\test_bot.ps1 all`
2. Record baseline scores
3. Set improvement targets

### Regular Monitoring:
1. Daily quick tests during development
2. Weekly full test runs
3. Compare scores over time
4. Track enhancement effectiveness

### Success Metrics:
- **Quick Test**: Consistently ≥ 7.0/10
- **Context Test**: Consistently ≥ 7.5/10  
- **Complex Test**: Consistently ≥ 7.0/10
- **Benchmark**: Average < 0.3s
- **Full Test**: Average ≥ 7.5/10

Use these automated tests to validate your bot logic enhancements and track improvement over time! 🎉
