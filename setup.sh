#!/bin/bash

# Create virtual environment with Python 3.10
echo "Creating virtual environment with Python 3.10..."

# Try to find python3.10 executable
if command -v python3.10 &> /dev/null; then
    echo "Using python3.10 to create virtual environment..."
    python3.10 -m venv .venv
elif [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 10 ]; then
    # If python3 is version 3.10 or higher
    echo "Using python3 (version $python_version) to create virtual environment..."
    python3 -m venv .venv
else
    echo "Error: Could not find python3.10 executable and current python3 is not 3.10+."
    echo "Please ensure Python 3.10 or higher is installed and available in your PATH."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env with your actual API credentials."
fi

echo "Setup complete! You can now run the application with:"
echo "source .venv/bin/activate && streamlit run Briefing_Agent.py"