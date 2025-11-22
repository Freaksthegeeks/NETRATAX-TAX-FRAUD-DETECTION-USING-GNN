@echo off
REM Setup script for Tax Fraud Detection GNN on Windows

echo.
echo ========================================================
echo   Tax Fraud Detection Using Graph Neural Networks
echo   Setup & Installation Script (Windows)
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [5/5] Initializing project structure...
python init_project.py

echo.
echo ========================================================
echo   ✅ Setup Complete!
echo ========================================================
echo.
echo Next steps:
echo.
echo   1. Generate sample data:
echo      cd src\data_processing
echo      python generate_sample_data.py
echo.
echo   2. Process data:
echo      python clean_data.py
echo.
echo   3. Build graph:
echo      cd ..\graph_construction
echo      python build_graph.py
echo.
echo   4. Train model:
echo      cd ..\gnn_models
echo      python train_gnn.py
echo.
echo   5. Launch dashboard:
echo      cd ..\..\dashboard
echo      streamlit run app.py
echo.
echo ========================================================
echo.
pause
