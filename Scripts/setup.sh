#!/bin/bash

# Check if the virtual environment directory (.venv) exists in the project root.
if [ ! -d "../.venv" ]; then
    echo "Creating virtual environment in .venv directory..."
    python3 -m venv ../.venv
else
    echo "Virtual environment already exists in .venv."
fi

# Activate the virtual environment.
echo "Activating virtual environment..."
source ../.venv/bin/activate

# Upgrade pip to the latest version.
echo "Upgrading pip..."
pip install --upgrade pip

# Install the required libraries from requirements.txt (located in the project root).
echo "Installing required libraries..."
pip install -r ../requirements.txt

# Set the required permissions for the runner script (run.sh in the project root)
echo "Setting executable permissions for run.sh..."
chmod +x Scripts/run.sh

echo "Setup complete. Your virtual environment is ready and runner script permissions are set."
