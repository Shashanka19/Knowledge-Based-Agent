#!/bin/bash

echo "================================"
echo "  KnowledgeBase Agent Launcher"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/lib/python*/site-packages/streamlit/__init__.py" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install requirements"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found"
    echo "Please copy .env.example to .env and configure your API keys"
    read -p "Press Enter to continue..."
fi

# Launch the application
echo ""
echo "Starting KnowledgeBase Agent..."
echo ""
echo "Open your browser to: http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run main.py

echo ""
echo "KnowledgeBase Agent stopped."