#!/bin/bash
# Setup script for FreeFall deployment

echo "🚀 FreeFall Setup"
echo "=================="

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
cd freefall_web
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env created - please edit with your settings"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run locally:"
echo "  source venv/bin/activate"
echo "  cd freefall_web"
echo "  FLASK_ENV=development python App.py"
echo ""
echo "To run with Gunicorn:"
echo "  gunicorn app:app"