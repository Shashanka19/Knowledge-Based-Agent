@echo off
echo ================================
echo   KnowledgeBase Agent Launcher
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\streamlit" (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found
    echo Please copy .env.example to .env and configure your API keys
    pause
)

REM Launch the application
echo.
echo Starting KnowledgeBase Agent...
echo.
echo Open your browser to: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

streamlit run main.py

echo.
echo KnowledgeBase Agent stopped.
pause