#!/bin/bash
# Run this script from the project root directory.

# Check if the virtual environment is already active; if not, activate it.
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment already active."
fi

echo "Running main Python file (Source/main.py)..."
python3 Source/main.py
