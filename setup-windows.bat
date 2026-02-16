@echo off
REM Windows Setup Script for SLPA Container Damage Detection System

echo ========================================
echo   Initial Setup for Windows
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo OK - Python is installed
echo.

echo [2/5] Creating virtual environment...
if exist "venv\" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo OK - Virtual environment created
)
echo.

echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)
echo OK - Virtual environment activated
echo.

echo [4/5] Installing Python dependencies...
echo This may take several minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo You may need to install Visual C++ Build Tools
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
)
echo.

echo [5/5] Checking MySQL connection...
echo.
echo IMPORTANT: Make sure you have:
echo   1. MySQL Server installed and running
echo   2. Created database: slpa_container_detection
echo   3. Updated .env file with your MySQL password
echo.
pause

echo Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo.
    echo ERROR: Database migration failed!
    echo Please check:
    echo   1. MySQL is running (XAMPP or MySQL service)
    echo   2. Database 'slpa_container_detection' exists
    echo   3. .env file has correct MySQL password
    echo   4. DB_USER and DB_PASSWORD in .env are correct
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Start MySQL (XAMPP or: net start MySQL80)
echo   2. Run: start-django.bat
echo   3. Access Django: http://localhost:8000
echo   4. Access phpMyAdmin: http://localhost/phpmyadmin
echo.
echo To create an admin user, run:
echo   venv\Scripts\activate
echo   python manage.py createsuperuser
echo.
pause
