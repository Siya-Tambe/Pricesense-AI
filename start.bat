@echo off
title PriceSense
color 0A

echo.
echo  ==========================================
echo   PriceSense - Starting up...
echo  ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed or not on PATH
    echo  Please install Python from https://python.org
    pause
    exit
)

:: Go to backend folder
cd /d "%~dp0backend"

:: Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo  Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo  No virtual environment found, using system Python...
)

:: Check if dependencies are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo  Installing dependencies...
    pip install -r requirements.txt
    echo.
)

:: Start the backend server in background
echo  Starting backend server on http://127.0.0.1:8000 ...
start "PriceSense Backend" /min python -m uvicorn main:app --host 127.0.0.1 --port 8000

:: Wait for server to boot up
echo  Waiting for server to start...
timeout /t 3 /nobreak >nul

:: Check server is actually running
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000')" >nul 2>&1
if errorlevel 1 (
    timeout /t 3 /nobreak >nul
)

:: Open the app in default browser
echo  Opening PriceSense in your browser...
start "" "%~dp0frontend\index.html"

echo.
echo  ==========================================
echo   PriceSense is running!
echo   Backend : http://127.0.0.1:8000
echo   App     : frontend/index.html
echo  ==========================================
echo.
echo  Keep this window open while using the app.
echo  Close this window to shut down the server.
echo.

:: Keep window open so server stays alive
:loop
timeout /t 60 /nobreak >nul
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000')" >nul 2>&1
if errorlevel 1 (
    echo  Server stopped unexpectedly. Restarting...
    start "PriceSense Backend" /min python -m uvicorn main:app --host 127.0.0.1 --port 8000
    timeout /t 3 /nobreak >nul
)
goto loop