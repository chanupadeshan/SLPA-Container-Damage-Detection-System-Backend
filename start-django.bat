@echo off
REM Django Server Startup Script for Windows

echo ========================================
echo   Starting Django Server
echo ========================================
echo.
echo Django API will be available at:
echo   http://localhost:9000
echo.
echo Django Admin Panel:
echo   http://localhost:9000/admin
echo.
echo Database: SQLite by default (set DB_ENGINE=mysql for MySQL)
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
    echo Then: venv\Scripts\activate ^&^& pip install -r requirements.txt
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

REM Run Django server on port 9000 (matches frontend default)
echo Starting Django on 0.0.0.0:9000...
echo.
python manage.py runserver 0.0.0.0:9000

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ERROR: Django failed to start
    pause
)
