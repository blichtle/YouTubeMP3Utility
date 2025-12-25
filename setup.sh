#!/bin/bash

# YouTube MP3 Downloader - Setup Script
# This script sets up the development environment

echo "🔧 Setting up YouTube MP3 Downloader..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "⚠️  tkinter is not available. Installing..."
    
    # Detect OS and provide installation instructions
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS, run: brew install python-tk"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Ubuntu/Debian, run: sudo apt-get install python3-tk"
    fi
    
    echo "Please install tkinter and run this script again."
    exit 1
fi

echo "✅ Python 3 and tkinter are available"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "🎉 Setup complete! You can now run the application with:"
echo "   ./run.sh"
echo ""
echo "Or manually with:"
echo "   source venv/bin/activate"
echo "   python main.py"