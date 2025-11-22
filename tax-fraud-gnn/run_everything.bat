echo ✅ Virtual environment activated
@echo off
REM ============================================================================
REM Tax Fraud Detection - Model Training & Deployment Script (venv-aware)
REM ============================================================================
REM This script runs the pipeline using the project's virtualenv Python directly
REM (avoids needing to run Activate.ps1). It installs requirements, prepares data,
REM trains the GNN, and starts the Flask app using the venv Python executable.
REM ============================================================================

set "VENV_PY=C:\BIG HACK\big\Scripts\python.exe"

if not exist "app.py" (
    echo Error: app.py not found. Please run this script from the tax-fraud-gnn directory
    pause
    exit /b 1
)

echo [1/4] Installing dependencies into virtualenv (may take a few minutes)...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some packages may not have installed correctly. Check the output above.
)

echo.
echo [2/4] Preparing real data...
"%VENV_PY%" prepare_real_data.py
if errorlevel 1 (
    echo Error during data preparation
    pause
    exit /b 1
)

echo.
echo [3/4] Training GNN model (this may take a few minutes)...
"%VENV_PY%" train_gnn_model.py
if errorlevel 1 (
    echo Error during model training
    pause
    exit /b 1
)

echo.
echo [4/4] Starting Flask application (press Ctrl+C to stop)...
"%VENV_PY%" app.py

pause
