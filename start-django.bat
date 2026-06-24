@echo off
REM Django Server Startup Script for Windows

echo ========================================
echo   Starting Django Server
echo ========================================
echo.
echo Django API will be available at:
echo   http://localhost:8000
echo.
echo Django Admin Panel:
echo   http://localhost:8000/admin
echo.
echo Database: MySQL (slpa_container_detection)
echo.
echo ========================================
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)

REM Run Django server
echo Starting Django...
echo.
python manage.py runserver

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ERROR: Django failed to start
    pause
)
