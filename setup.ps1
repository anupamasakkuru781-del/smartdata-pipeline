
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================="
Write-Host "       SMARTDATA PIPELINE SETUP"
Write-Host "========================================="
Write-Host ""

# Check Python installation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed or not available in PATH."
}

# Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"

if ($LASTEXITCODE -ne 0) {
    throw "Please install Python 3.11 or newer."
}

Write-Host "[1/5] Python version verified."

# Check required files
if (-not (Test-Path ".\requirements.txt")) {
    throw "requirements.txt was not found."
}

if (-not (Test-Path ".\database\schema.sql")) {
    throw "database/schema.sql was not found."
}

# Create virtual environment
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[2/5] Creating virtual environment..."
    python -m venv .venv

    if ($LASTEXITCODE -ne 0) {
        throw "Virtual environment creation failed."
    }
}
else {
    Write-Host "[2/5] Virtual environment already exists."
}

$venvPython = Join-Path $PWD ".venv\Scripts\python.exe"

# Install dependencies without upgrading pip
Write-Host "[3/5] Installing project dependencies..."

& $venvPython -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed."
}

# Initialize database
Write-Host "[4/5] Initializing SQLite database..."

& $venvPython -m app.database

if ($LASTEXITCODE -ne 0) {
    throw "Database initialization failed."
}

# Seed sample customers
Write-Host "[5/5] Adding sample customer records..."

& $venvPython -m scripts.seed_customers

if ($LASTEXITCODE -ne 0) {
    throw "Customer setup failed."
}

Write-Host ""
Write-Host "========================================="
Write-Host "       SETUP COMPLETED SUCCESSFULLY"
Write-Host "========================================="
Write-Host ""
Write-Host "Launch dashboard:"
Write-Host ".\.venv\Scripts\python.exe -m streamlit run frontend/dashboard.py"
Write-Host ""
Write-Host "Run automated tests:"
Write-Host ".\.venv\Scripts\python.exe -m pytest tests/ -v"
