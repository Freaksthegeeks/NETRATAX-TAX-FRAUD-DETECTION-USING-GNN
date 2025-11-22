#!/bin/bash
# Setup script for Tax Fraud Detection GNN on Linux/macOS

echo ""
echo "========================================================"
echo "  Tax Fraud Detection Using Graph Neural Networks"
echo "  Setup & Installation Script (Linux/macOS)"
echo "========================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.9+ from python.org"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[5/5] Initializing project structure..."
python init_project.py

echo ""
echo "========================================================"
echo "   ✅ Setup Complete!"
echo "========================================================"
echo ""
echo "Next steps:"
echo ""
echo "   1. Generate sample data:"
echo "      cd src/data_processing"
echo "      python generate_sample_data.py"
echo ""
echo "   2. Process data:"
echo "      python clean_data.py"
echo ""
echo "   3. Build graph:"
echo "      cd ../graph_construction"
echo "      python build_graph.py"
echo ""
echo "   4. Train model:"
echo "      cd ../gnn_models"
echo "      python train_gnn.py"
echo ""
echo "   5. Launch dashboard:"
echo "      cd ../../dashboard"
echo "      streamlit run app.py"
echo ""
echo "========================================================"
echo ""
