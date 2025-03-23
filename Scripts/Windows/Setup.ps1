# Run this script from the project root directory.

# Check if .venv exists; if not, create it.
if (-Not (Test-Path -Path ".venv")) {
    Write-Output "Creating virtual environment in .venv directory..."
    python -m venv .venv
} else {
    Write-Output "Virtual environment already exists in .venv."
}

# Activate the virtual environment.
Write-Output "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

# Upgrade pip and install required libraries.
Write-Output "Upgrading pip..."
pip install --upgrade pip
Write-Output "Installing required libraries from requirements.txt..."
pip install -r requirements.txt

Write-Output "Setup complete. Your virtual environment is ready."
