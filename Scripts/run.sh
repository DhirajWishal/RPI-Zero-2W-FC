#!/bin/bash

# Check if the virtual environment is set up by checking for the .venv directory.
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup script..."
    bash Scripts/setup.sh
fi

# Check if the virtual environment is already active.
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment from .venv..."
    source .venv/bin/activate
else
    echo "Virtual environment already active."
fi

# Run the main Python file.
echo "Running main Python file (Source/Main.py)..."
python3 Source/Main.py
