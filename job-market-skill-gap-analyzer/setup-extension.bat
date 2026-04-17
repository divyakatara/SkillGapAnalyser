@echo off
REM SkillScope Extension - Development Setup Script for Windows
REM This script sets up the development environment

echo.
echo ============================================
echo  SkillScope Chrome Extension Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10 or higher.
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker found
    set DOCKER_AVAILABLE=true
) else (
    echo [WARNING] Docker not found. Will use local Python setup.
    set DOCKER_AVAILABLE=false
)

echo.
echo Installing backend dependencies...
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Downloading spaCy model...
python -m spacy download en_core_web_sm

REM Create necessary directories
echo Creating data directories...
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
if not exist "data\resumes" mkdir data\resumes
if not exist "logs" mkdir logs

echo.
echo [OK] Backend dependencies installed!
echo.

REM Start backend
echo Starting backend API...
echo.

if "%DOCKER_AVAILABLE%"=="true" (
    set /p use_docker="Do you want to use Docker? (y/n): "
    if /i "%use_docker%"=="y" (
        echo Starting backend with Docker...
        docker-compose up -d
        echo.
        echo [OK] Backend running in Docker!
        echo    API: http://localhost:8000
        echo    Health: http://localhost:8000/health
        echo.
        echo    To view logs: docker-compose logs -f
        echo    To stop: docker-compose down
    ) else (
        echo Starting backend with Python...
        start "SkillScope API" python -m uvicorn backend.main:app --reload --port 8000
        echo.
        echo [OK] Backend starting...
        echo    API: http://localhost:8000
        echo    Health: http://localhost:8000/health
    )
) else (
    echo Starting backend with Python...
    start "SkillScope API" python -m uvicorn backend.main:app --reload --port 8000
    echo.
    echo [OK] Backend starting...
    echo    API: http://localhost:8000
    echo    Health: http://localhost:8000/health
)

REM Wait for backend to start
echo.
echo Waiting for API to start...
timeout /t 5 /nobreak >nul

REM Test API health
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] API is healthy!
) else (
    echo [WARNING] API health check failed. Please check logs.
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo Next Steps:
echo.
echo 1. Load Chrome Extension:
echo    - Open Chrome
echo    - Go to chrome://extensions/
echo    - Enable 'Developer mode'
echo    - Click 'Load unpacked'
echo    - Select: %cd%\chrome-extension
echo.
echo 2. Configure Extension:
echo    - Click SkillScope icon
echo    - Settings -^> API URL: http://localhost:8000
echo    - Click 'Save Settings'
echo.
echo 3. Upload Resume:
echo    - Click SkillScope icon
echo    - Upload Resume
echo    - Select your PDF/DOCX file
echo.
echo 4. Try It Out:
echo    - Visit a LinkedIn job posting
echo    - Click 'Analyze with SkillScope'
echo.
echo Documentation:
echo    - Quick Start: chrome-extension\QUICKSTART.md
echo    - Full Guide: chrome-extension\README.md
echo    - Deployment: DEPLOYMENT.md
echo.
echo Happy job hunting!
echo.

pause
