# Run this script from the project root directory.

# Check if the virtual environment is active; if not, activate it.
if (-not $env:VIRTUAL_ENV) {
    Write-Output "Activating virtual environment..."
    . .\.venv\Scripts\Activate.ps1
} else {
    Write-Output "Virtual environment already active."
}

Write-Output "Running main Python file (Source/main.py)..."
python Source/main.py
