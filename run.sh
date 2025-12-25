#!/bin/bash

# YouTube MP3 Downloader - Run Script
# This script activates the virtual environment and runs the application

echo "🎵 Starting YouTube MP3 Downloader..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run the application
source venv/bin/activate
python main.py

echo "👋 YouTube MP3 Downloader closed."