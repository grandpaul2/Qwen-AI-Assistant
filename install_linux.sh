#!/bin/bash
# Qwen Assistant Linux Installation Script
# Usage: chmod +x install_linux.sh && ./install_linux.sh

echo "🐧 Qwen Assistant Linux Setup"
echo "==============================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first:"
    
    # Detect package manager and show appropriate command
    if command -v apt &> /dev/null; then
        echo "   sudo apt update && sudo apt install python3 python3-pip"
    elif command -v dnf &> /dev/null; then
        echo "   sudo dnf install python3 python3-pip"
    elif command -v yum &> /dev/null; then
        echo "   sudo yum install python3 python3-pip"
    elif command -v pacman &> /dev/null; then
        echo "   sudo pacman -S python python-pip"
    else
        echo "   Please install Python 3 using your distribution's package manager"
    fi
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is not available. Please install python3-pip"
    exit 1
fi

echo "✅ pip found"

# Install dependencies
echo "📦 Installing dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    python3 -m pip install -r requirements.txt
fi

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully!"
    else
        echo "❌ Failed to install Ollama. Please install manually:"
        echo "   curl -fsSL https://ollama.ai/install.sh | sh"
        exit 1
    fi
else
    echo "✅ Ollama found: $(ollama --version 2>/dev/null || echo 'installed')"
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Start Ollama service: ollama serve"
echo "2. Pull Qwen model: ollama pull qwen2.5:3b"  
echo "3. Run assistant: python3 qwen_assistant.py"
echo ""
echo "� Helpful commands:"
echo "   /tools    - List all file management tools"
echo "   /config   - Configure settings"
echo "   exit      - Quit assistant"
echo ""
