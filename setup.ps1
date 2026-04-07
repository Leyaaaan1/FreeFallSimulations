# Setup script for FreeFall deployment (Windows)

Write-Host "🚀 FreeFall Setup (Windows)" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
cd freefall_web
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env created - please edit with your settings" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run locally:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  cd freefall_web" -ForegroundColor White
Write-Host "  python App.py" -ForegroundColor White
Write-Host ""
Write-Host "To run with Gunicorn:" -ForegroundColor Cyan
Write-Host "  gunicorn app:app" -ForegroundColor White