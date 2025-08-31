#!/bin/bash
# WorkspaceAI Linux Installation Script
# Usage: chmod +x install_linux.sh && ./install_linux.sh

echo "WorkspaceAI Linux Setup v2.2"
echo "============================="

# Function to detect package manager
detect_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

# Check if script is run with proper permissions
if [[ $EUID -eq 0 ]]; then
    echo "Warning: Running as root. Consider running as regular user."
fi

# Detect package manager
PKG_MANAGER=$(detect_package_manager)
echo "Detected package manager: $PKG_MANAGER"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first:"
    
    # Show package manager specific command
    case $PKG_MANAGER in
        "apt")
            echo "   sudo apt update && sudo apt install python3 python3-pip"
            ;;
        "dnf")
            echo "   sudo dnf install python3 python3-pip"
            ;;
        "yum")
            echo "   sudo yum install python3 python3-pip"
            ;;
        "pacman")
            echo "   sudo pacman -S python python-pip"
            ;;
        "zypper")
            echo "   sudo zypper install python3 python3-pip"
            ;;
        *)
            echo "   Please install Python 3 using your distribution's package manager"
            ;;
    esac
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "pip is not available. Please install python3-pip"
    exit 1
fi

echo "pip found"

# Install dependencies
echo "Installing dependencies..."

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found. Creating minimal requirements..."
    echo "requests>=2.31.0" > requirements.txt
    echo "tqdm>=4.66.0" >> requirements.txt
fi

# Install dependencies with better error handling
if command -v pip3 &> /dev/null; then
    if pip3 install -r requirements.txt --user; then
        echo "Dependencies installed successfully!"
    else
        echo "Failed to install dependencies with pip3"
        echo "Try: python3 -m pip install -r requirements.txt --user"
        exit 1
    fi
else
    if python3 -m pip install -r requirements.txt --user; then
        echo "Dependencies installed successfully!"
    else
        echo "Failed to install dependencies"
        echo "You may need to install pip: sudo $PKG_MANAGER install python3-pip"
        exit 1
    fi
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing Ollama..."
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        echo "curl is required to install Ollama. Please install curl first:"
        case $PKG_MANAGER in
            "apt") echo "   sudo apt install curl" ;;
            "dnf") echo "   sudo dnf install curl" ;;
            "yum") echo "   sudo yum install curl" ;;
            "pacman") echo "   sudo pacman -S curl" ;;
            "zypper") echo "   sudo zypper install curl" ;;
            *) echo "   Install curl using your package manager" ;;
        esac
        exit 1
    fi
    
    # Install Ollama
    if curl -fsSL https://ollama.ai/install.sh | sh; then
        echo "Ollama installed successfully!"
        echo "You may need to restart your terminal or run: source ~/.bashrc"
    else
        echo "Failed to install Ollama. Please install manually:"
        echo "   curl -fsSL https://ollama.ai/install.sh | sh"
        echo "   Or visit: https://ollama.ai/download"
        exit 1
    fi
else
    echo "Ollama found: $(ollama --version 2>/dev/null || echo 'installed')"
fi

echo ""
echo "Setup complete! Next steps:"
echo "1. Start Ollama service: ollama serve"
echo "2. Pull Qwen model: ollama pull qwen2.5:3b"  
echo "3. Run assistant: python3 workspaceai.py"
echo ""
echo "The assistant will create a WorkspaceAI/ directory with:"
echo "   workspace/  - Your secure file operations area"
echo "   memory/     - Persistent conversation history"
echo "   config.json - Settings and preferences"
echo ""
echo "Helpful commands in chat:"
echo "   /tools    - List all file management tools"
echo "   /memory   - Show conversation history status"
echo "   /config   - Configure settings"
echo "   /new      - Start fresh conversation"
echo "   exit      - Quit assistant"
echo ""
echo "Troubleshooting:"
echo "   - If Ollama command not found: restart terminal or 'source ~/.bashrc'"
echo "   - If Python packages missing: 'python3 -m pip install --user requests tqdm'"
echo "   - For permission issues: ensure user is in docker/ollama groups"
echo "   - All file operations are safely contained in the workspace directory"
echo ""
echo "Features:"
echo "   • Rolling memory system (remembers conversations across sessions)"
echo "   • 18+ file management tools with safety protections" 
echo "   • Cross-platform software installation commands"
echo "   • Color-coded chat interface for better readability"
echo ""
