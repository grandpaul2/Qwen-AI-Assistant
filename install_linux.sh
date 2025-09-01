#!/bin/bash
# WorkspaceAI Linux Installation Script v3.0
# Usage: chmod +x install_linux.sh && ./install_linux.sh

echo "🤖 WorkspaceAI Linux Setup v3.0"
echo "================================="
echo "Advanced AI Assistant with Enhanced Tool Detection"
echo ""

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
echo "🎉 Setup complete! WorkspaceAI v3.0 is ready!"
echo ""
echo "Quick Start:"
echo "1. Start Ollama service: ollama serve"
echo "2. Pull Qwen model: ollama pull qwen2.5:3b"  
echo "3. Run assistant: python3 main.py"
echo ""
echo "🛡️ Security Features:"
echo "   • All file operations contained in workspace/ directory"
echo "   • Safe permission system with user confirmation"
echo "   • Memory system respects privacy boundaries"
echo ""
echo "📁 Directory Structure:"
echo "   workspace/  - Your secure file operations area"
echo "   memory/     - Persistent conversation history (JSON)"
echo "   config.json - Settings and AI model preferences"
echo ""
echo "💬 Chat Commands:"
echo "   /tools    - List all 18+ file management tools"
echo "   /memory   - Show conversation history status"
echo "   /config   - Configure AI model settings"
echo "   /new      - Start fresh conversation"
echo "   exit      - Quit assistant"
echo ""
echo "🔧 Enhanced v3.0 Features:"
echo "   • 85-90% tool detection accuracy (vs 50% baseline)"
echo "   • Advanced contextual pattern matching"
echo "   • Auto-unique filename generation (prevents conflicts)"
echo "   • Enhanced system prompt with CRITICAL RULE enforcement"
echo "   • Improved search and file management capabilities"
echo ""
echo "🚨 Troubleshooting:"
echo "   - Ollama not found: restart terminal or 'source ~/.bashrc'"
echo "   - Missing packages: 'python3 -m pip install --user requests tqdm'"
echo "   - Permission issues: ensure user in docker/ollama groups"
echo "   - Tool detection issues: Use clear, direct language (e.g., 'create file.txt')"
echo ""
