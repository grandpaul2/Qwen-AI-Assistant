# WorkspaceAI v3.0 - Project Setup Guide

## 🚀 Setting Up on a New Computer

### Method 1: Git Clone (Recommended)

#### Prerequisites
```bash
# Install Git
https://git-scm.com/downloads

# Install Python 3.11+
https://python.org/downloads/

# Verify installations
git --version
python --version
pip --version
```

#### Clone the Repository
```bash
# Clone the repository
git clone https://github.com/grandpaul2/WorkspaceAI.git
cd WorkspaceAI

# Switch to the feature branch (with all latest fixes)
git checkout feature/modular-architecture
```

#### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest tests/ --tb=no -q
```

### Method 2: Manual Copy (Alternative)

If you need to copy files manually, here's what to include:

#### Essential Files & Directories (Git-Tracked)
```
WorkspaceAI_project/
├── src/                        # Core source code (REQUIRED)
├── tests/                      # Test suite (REQUIRED)
├── docs/                       # Project documentation (REQUIRED)
├── requirements.txt            # Dependencies (REQUIRED)
├── pyproject.toml             # Project configuration (REQUIRED)
├── README.md                  # Main project documentation (REQUIRED)
├── main.py                    # Entry point (REQUIRED)
├── install_linux.sh           # Linux installation script (RECOMMENDED)
├── .gitignore                 # Git ignore rules (RECOMMENDED)
├── .github/                   # GitHub workflows/templates (RECOMMENDED)
└── test_failures_analysis.md  # Testing documentation (RECOMMENDED)
```

#### Important Non-Git Files (Manual Backup Required)
```
WorkspaceAI_project/
├── WorkspaceAI/               # User data & configuration (IMPORTANT)
│   ├── config.json            # User settings & preferences (BACKUP)
│   ├── workspaceai.log        # Application logs (OPTIONAL)
│   ├── memory/                # Conversation memory (BACKUP IF IMPORTANT)
│   └── workspace/             # User workspace files (BACKUP IF IMPORTANT)
├── archive/                   # Historical project versions (OPTIONAL)
│   ├── deprecated_components/ # Old code for reference (OPTIONAL)
│   └── old tests/            # Previous test versions (OPTIONAL)
├── PROJECT_SETUP_GUIDE.md    # This setup guide (RECOMMENDED)
└── .venv/                    # Virtual environment (SKIP - recreate)
```

#### Files to EXCLUDE (Generated/Temporary)
```
# Don't copy these - they'll be regenerated:
__pycache__/                   # Python cache
.pytest_cache/                 # Test cache
htmlcov/                       # Coverage reports
coverage.xml                   # Coverage data
.venv/                        # Virtual environment (recreate instead)
*.pyc                         # Compiled Python files
*.pyo                         # Optimized Python files
```

### Method 3: Complete Backup Strategy

For a complete transfer including all data and history:

#### Step 1: Git Repository + User Data
```bash
# Clone the repository (gets all source code)
git clone https://github.com/grandpaul2/WorkspaceAI.git
cd WorkspaceAI
git checkout feature/modular-architecture

# Separately copy user data folder
# From old computer:
# Copy: WorkspaceAI_project/WorkspaceAI/ 
# To new computer: WorkspaceAI/WorkspaceAI/
```

#### Step 2: Important Configuration Files
```bash
# Copy these files manually if they contain important customizations:
config.json              # User preferences
workspaceai.log          # Recent activity logs (if needed)
memory/                  # Conversation history (if important)
workspace/               # User workspace files
```

#### Step 3: Optional Archives & Documentation  
```bash
# If you want to preserve development history:
archive/                 # Old versions and deprecated code
PROJECT_SETUP_GUIDE.md  # This setup guide
test_failures_analysis.md # Testing research documentation
```

## 🔧 Post-Setup Configuration

### 1. Transfer User Data (Important!)
```bash
# After cloning the repository, copy your user data:
# From old computer, copy these folders/files:

WorkspaceAI/config.json        # Your personal settings & preferences
WorkspaceAI/memory/            # Conversation history & context
WorkspaceAI/workspace/         # Your workspace files & projects
WorkspaceAI/workspaceai.log    # Recent activity logs (optional)

# To new computer location:
# Place in: WorkspaceAI/WorkspaceAI/ (inside the cloned repository)
```

### 2. Verify Project Structure
```bash
# Check that all core modules are present
python -c "import src.app; print('✅ Core modules accessible')"

# Run test suite to verify everything works
python -m pytest tests/ --tb=no -q
# Should show: "790+ passed, 0 failed"
```

### 2. Configure Environment
```bash
# Create WorkspaceAI data directory if needed
mkdir WorkspaceAI
mkdir WorkspaceAI/memory
mkdir WorkspaceAI/workspace

# Optional: Create config file
echo '{"verbose_output": true}' > WorkspaceAI/config.json
```

### 3. Test Core Functionality
```bash
# Test basic functionality
python main.py --help

# Test with a simple command
python main.py "test connection"
```

## 🛠️ Development Setup (If Contributing)

### Additional Setup for Development
```bash
# Install development dependencies
pip install pytest pytest-cov pytest-mock hypothesis

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Verify development environment
python -m pytest tests/ --cov=src --cov-report=html
```

### IDE Configuration
- **VS Code**: Install Python extension, configure workspace settings
- **PyCharm**: Set Python interpreter to your venv
- **Any IDE**: Ensure PYTHONPATH includes project root

## 📊 Verification Checklist

After setup, verify these work:

- [ ] `python -c "import src.app"` (no errors)
- [ ] `python -m pytest tests/ -q` (all tests pass)  
- [ ] `python main.py --help` (shows help)
- [ ] Core modules importable from src/
- [ ] Test coverage >80% if running with coverage
- [ ] No import or dependency errors

## 🚨 Troubleshooting

### Common Issues
```bash
# Python path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows

# Dependencies missing
pip install -r requirements.txt --upgrade

# Test failures
python -m pytest tests/ --tb=long -v  # Get detailed error info
```

### Platform-Specific Notes
- **Windows**: Use `venv\Scripts\activate` for virtual environment
- **macOS/Linux**: Use `source venv/bin/activate` for virtual environment
- **Python Version**: Requires Python 3.11+ for optimal compatibility

---

## 📈 What's Included in This Project

### ✅ Stable Test Suite (790+ Tests Passing)
- Complete unit test coverage for all modules
- Security and system integration tests
- Established testing patterns for maintainability

### ✅ Enhanced Error Handling
- Graceful degradation patterns
- Comprehensive exception handling
- Robust fallback mechanisms

### ✅ Modular Architecture
- Clean separation of concerns
- Dynamic import patterns
- Backward compatibility maintained

### ✅ Documentation
- Comprehensive README files
- Testing best practices guide
- Setup and configuration instructions

---

**Last Updated**: September 2, 2025 - Post test suite stabilization
**Status**: ✅ Production Ready - All tests passing, 80%+ coverage maintained
