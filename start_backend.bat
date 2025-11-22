@echo off
REM NETRA TAX - FastAPI Backend Startup Script for Windows

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║   NETRA TAX - Starting FastAPI Backend Server                 ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist "big\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Creating virtual environment...
    python -m venv big
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call big\Scripts\activate.bat

REM Install requirements
echo ✓ Installing dependencies...
pip install -r NETRA_TAX\backend\requirements.txt -q

REM Start FastAPI server
echo.
echo ✓ Starting FastAPI server on http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd NETRA_TAX
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
