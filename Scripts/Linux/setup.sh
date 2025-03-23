#!/bin/bash
# Run this script from the project root directory.

# Check if .venv exists; if not, create it.
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv directory..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists in .venv."
fi

# Activate the virtual environment.
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install required libraries.
echo "Upgrading pip..."
pip install --upgrade pip
echo "Installing required libraries from requirements.txt..."
pip install -r requirements.txt

# Set executable permission for the runner script.
echo "Setting executable permissions for Scripts/Linux/run.sh..."
chmod +x Scripts/Linux/run.sh

echo "Setup complete. Your virtual environment is ready."
