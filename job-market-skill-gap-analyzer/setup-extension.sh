#!/bin/bash

# SkillScope Extension - Development Setup Script
# This script sets up the development environment

set -e

echo "🚀 SkillScope Chrome Extension Setup"
echo "====================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker found: $(docker --version)"
    DOCKER_AVAILABLE=true
else
    echo "⚠️  Docker not found. Will use local Python setup."
    DOCKER_AVAILABLE=false
fi

echo ""
echo "📦 Setting up backend..."
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Install Python dependencies
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate

echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo ""
echo "✅ Backend dependencies installed!"
echo ""

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/raw data/processed data/resumes logs

# Start the backend
echo ""
echo "🎯 Starting backend API..."
echo ""

if [ "$DOCKER_AVAILABLE" = true ]; then
    read -p "Do you want to use Docker? (y/n): " use_docker
    if [ "$use_docker" = "y" ] || [ "$use_docker" = "Y" ]; then
        echo "Starting backend with Docker..."
        docker-compose up -d
        echo ""
        echo "✅ Backend running in Docker!"
        echo "   API: http://localhost:8000"
        echo "   Health: http://localhost:8000/health"
        echo ""
        echo "   To view logs: docker-compose logs -f"
        echo "   To stop: docker-compose down"
    else
        echo "Starting backend with Python..."
        cd backend
        uvicorn main:app --reload --port 8000 &
        BACKEND_PID=$!
        echo ""
        echo "✅ Backend running (PID: $BACKEND_PID)"
        echo "   API: http://localhost:8000"
        echo "   Health: http://localhost:8000/health"
        cd ..
    fi
else
    echo "Starting backend with Python..."
    cd backend
    uvicorn main:app --reload --port 8000 &
    BACKEND_PID=$!
    echo ""
    echo "✅ Backend running (PID: $BACKEND_PID)"
    echo "   API: http://localhost:8000"
    echo "   Health: http://localhost:8000/health"
    cd ..
fi

# Wait for backend to start
echo ""
echo "Waiting for API to start..."
sleep 5

# Test API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API health check failed. Please check logs."
fi

echo ""
echo "======================================"
echo "✨ Setup Complete!"
echo "======================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Load Chrome Extension:"
echo "   • Open Chrome"
echo "   • Go to chrome://extensions/"
echo "   • Enable 'Developer mode'"
echo "   • Click 'Load unpacked'"
echo "   • Select: $(pwd)/chrome-extension"
echo ""
echo "2. Configure Extension:"
echo "   • Click SkillScope icon"
echo "   • Settings → API URL: http://localhost:8000"
echo "   • Click 'Save Settings'"
echo ""
echo "3. Upload Resume:"
echo "   • Click SkillScope icon"
echo "   • Upload Resume"
echo "   • Select your PDF/DOCX file"
echo ""
echo "4. Try It Out:"
echo "   • Visit a LinkedIn job posting"
echo "   • Click 'Analyze with SkillScope'"
echo ""
echo "📚 Documentation:"
echo "   • Quick Start: chrome-extension/QUICKSTART.md"
echo "   • Full Guide: chrome-extension/README.md"
echo "   • Deployment: DEPLOYMENT.md"
echo ""
echo "Happy job hunting! 🎯"
