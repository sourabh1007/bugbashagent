@echo off
REM Bug Bash Copilot React Frontend Setup Script for Windows
REM This script sets up the complete React frontend with backend integration

echo 🚀 Setting up Bug Bash Copilot React Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Install backend dependencies
echo 📦 Installing dependencies...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Setup frontend
echo 📦 Setting up React frontend...
cd frontend

REM Install npm dependencies
npm install

if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

echo ✅ Frontend dependencies installed

REM Go back to main directory
cd ..

echo 🎉 Setup complete!
echo.
echo To start the application:
echo 1. Start the backend server:
echo    python backend_server.py
echo.
echo 2. In another terminal, start the frontend:
echo    cd frontend ^&^& npm start
echo.
echo 3. Open your browser to http://localhost:3000
echo.
echo 🔧 Make sure your Azure OpenAI configuration is set up correctly!
pause
