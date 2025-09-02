# Testing Suite - WorkspaceAI v3.0

Comprehensive testing infrastructure for WorkspaceAI with unit, security, and system tests.

## 🎯 Test Coverage Status

**Overall Coverage: 82.32%** ✅  
**Modules Above 80%: 11 out of 13** (84.6% success rate)

### Coverage by Module
- `__init__.py`: **100%** 🎯
- `config.py`: **97%** 🎯  
- `enhanced_interface.py`: **100%** 🎯
- `enhanced_tool_instructions.py`: **88%** ✅
- `exceptions.py`: **100%** 🎯
- `file_manager.py`: **89%** ✅
- `memory.py`: **83%** ✅
- `ollama_client.py`: **91%** ✅
- `ollama_connection_test.py`: **100%** 🎯
- `ollama_universal_interface.py`: **96%** ✅
- `progress.py`: **100%** 🎯
- `software_installer.py`: **82%** ✅
- `tool_schemas.py`: **90%** ✅
- `app.py`: **79%** 📈
- `universal_tool_handler.py`: **75%** 📈
- `utils.py`: **77%** 📈

## 🚀 Quick Start

### Run All Tests
```bash
# Full test suite with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Quick run without coverage
python -m pytest tests/ -q

# Verbose output
python -m pytest tests/ -v
```

### Run Specific Test Categories

#### Unit Tests (Individual Module Testing)
```bash
# All unit tests
python -m pytest tests/unit/ -v

# Specific module tests
python -m pytest tests/unit/test_app.py -v
python -m pytest tests/unit/test_universal_tool_handler.py -v
python -m pytest tests/unit/test_file_manager.py -v
python -m pytest tests/unit/test_memory.py -v
python -m pytest tests/unit/test_ollama_client.py -v
```

#### Security Tests
```bash
# All security tests
python -m pytest tests/security/ -v

# Input validation and sanitization
python -m pytest tests/security/test_security.py -v
```

#### System Tests (Integration Testing)
```bash
# All system tests
python -m pytest tests/system/ -v

# Infrastructure tests
python -m pytest tests/system/test_infrastructure.py -v
```

## 📊 Coverage Analysis

### Generate Coverage Reports
```bash
# HTML coverage report (opens in browser)
python -m pytest tests/ --cov=src --cov-report=html
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS

# Terminal coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing

# XML coverage report (for CI/CD)
python -m pytest tests/ --cov=src --cov-report=xml
```

### Coverage Targeting
```bash
# Test specific module coverage
python -m pytest tests/unit/test_app.py --cov=src/app.py --cov-report=term-missing

# Multiple modules
python -m pytest tests/unit/ --cov=src/file_manager.py --cov=src/memory.py --cov-report=term-missing
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Individual module testing with comprehensive coverage:
- **Isolated Testing**: Each module tested independently
- **Mock Dependencies**: External dependencies mocked for reliability
- **Edge Cases**: Boundary conditions and error scenarios
- **Function-Level**: Granular testing of all public functions

### Security Tests (`tests/security/`)
Security validation and vulnerability testing:
- **Input Sanitization**: Prevents injection attacks
- **File System Security**: Workspace boundary enforcement
- **Path Traversal**: Directory escape prevention
- **Code Execution Safety**: Safe execution environment validation

### System Tests (`tests/system/`)
Integration and end-to-end testing:
- **Workflow Testing**: Complete user scenarios
- **Module Integration**: Inter-module communication
- **Performance Testing**: Resource usage and timing
- **Cross-Platform**: Platform compatibility validation

## 🎯 Advanced Testing Options

### Filter Tests by Markers
```bash
# Run only fast tests
python -m pytest tests/ -m "not slow"

# Run integration tests only
python -m pytest tests/ -m "integration"

# Skip tests requiring external services
python -m pytest tests/ -m "not external"
```

### Parallel Testing
```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
python -m pytest tests/ -n auto
```

### Debugging Tests
```bash
# Stop on first failure
python -m pytest tests/ -x

# Show local variables on failure
python -m pytest tests/ -l

# Enter debugger on failure
python -m pytest tests/ --pdb
```

## 📁 Test File Organization

```
tests/
├── README.md                    # This file - testing documentation
├── conftest.py                  # Pytest configuration and shared fixtures
├── unit/                        # Unit tests for individual modules
├── security/                    # Security and vulnerability tests
└── system/                      # Integration and system-level tests
```

## 🔧 Test Configuration

### pytest.ini Configuration
Testing behavior configured in `pyproject.toml`:
- Test discovery patterns
- Coverage settings
- Output formatting
- Marker definitions

### Fixtures (`conftest.py`)
Shared test fixtures for consistent testing:
- Temporary workspace creation
- Mock configurations
- Test data generators
- Cleanup utilities

## 📈 Continuous Integration

### GitHub Actions Integration
```yaml
# Example CI configuration
- name: Run Tests
  run: |
    python -m pytest tests/ --cov=src --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

### Local Pre-commit Testing
```bash
# Run before committing
python -m pytest tests/ --cov=src --cov-fail-under=80
```

## 🎨 Testing Best Practices

### Writing New Tests
1. **One test per function/method**: Keep tests focused and isolated
2. **Descriptive names**: Use clear, descriptive test method names
3. **Mock external dependencies**: Isolate units under test
4. **Test edge cases**: Include boundary conditions and error scenarios
5. **Maintain coverage**: Aim for 80%+ coverage on new modules

### Test Organization
- **Group related tests**: Use test classes for logical grouping
- **Use fixtures**: Leverage conftest.py for common setup
- **Document complex tests**: Add docstrings for non-obvious test logic
- **Keep tests fast**: Mock slow operations, use small test data

## 🚨 Troubleshooting

### Common Issues
```bash
# Import errors
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Clear pytest cache
python -m pytest --cache-clear

# Run with full output
python -m pytest tests/ -s --tb=long
```

### Performance Issues
- Use `pytest-benchmark` for performance testing
- Profile slow tests with `pytest-profiling`
- Consider parallel execution for large test suites

---

**Note**: Test coverage targets 80%+ per module with 85%+ overall coverage goal. Current status: **82.32% overall coverage achieved** with **11 out of 13 modules above 80%**.
