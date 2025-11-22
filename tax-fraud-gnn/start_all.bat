@echo off
echo ========================================
echo Tax Fraud Detection - Startup Script
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Node.js not found in PATH!
    echo Please install Node.js from https://nodejs.org/
    echo.
    echo Starting Flask only (HTML templates mode)...
    echo.
    goto :start_flask
)

REM Check if npm dependencies are installed
if not exist "frontend\node_modules" (
    echo [INFO] Installing npm dependencies...
    cd frontend
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] npm install failed!
        echo.
        goto :start_flask
    )
    cd ..
    echo [SUCCESS] npm dependencies installed!
    echo.
)

echo ========================================
echo Starting Flask Backend...
echo ========================================
echo Flask will run on http://localhost:5000
echo.
start "Flask Backend" cmd /k "python app.py"

timeout /t 3 /nobreak >nul

echo ========================================
echo Starting React Frontend...
echo ========================================
echo React will run on http://localhost:3000
echo.
echo Opening browser in 5 seconds...
echo.
cd frontend
start "React Frontend" cmd /k "npm run dev"

timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Flask Backend:  http://localhost:5000
echo React Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
echo (Servers will continue running in separate windows)
pause >nul

:start_flask
echo ========================================
echo Starting Flask Backend (HTML Mode)...
echo ========================================
echo Flask will run on http://localhost:5000
echo.
python app.py

