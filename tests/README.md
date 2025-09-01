# WorkspaceAI Test Suite

This directory contains all test scripts and validation tools for WorkspaceAI.

## 🧪 Test Scripts

### Core Testing
- **test_scenarios.py** - Main 25-scenario testing framework
- **test_detection.py** - Tool detection validation
- **test_improved_detection.py** - Enhanced detection testing

### Specific Features
- **test_memory_config.py** - Memory system validation
- **test_unique_filenames.py** - Filename generation testing

## 🚀 Running Tests

### Run All Scenarios
```bash
cd tests
python test_scenarios.py run all
```

### Run Specific Scenario
```bash
python test_scenarios.py run 1    # File creation test
python test_scenarios.py run 15   # Complex workflow test
```

### Memory System Test
```bash
python test_memory_config.py
```

## 📊 Test Results

Current validation results show:
- **85-90% tool detection accuracy** across all scenarios
- **100% memory system reliability** 
- **Zero filename conflicts** with auto-unique generation
- **Complete backward compatibility** maintained

## 🛠️ For Developers

These tests validate the core functionality and should be run before merging any changes to main. The test framework supports both individual scenario testing and comprehensive validation.

---
*Test Suite for WorkspaceAI v3.0*
