#!/bin/bash
# NETRA TAX - FastAPI Backend Startup Script

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   NETRA TAX - Starting FastAPI Backend Server                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "✓ Installing dependencies..."
pip install -r backend/requirements.txt -q

# Start FastAPI server
echo ""
echo "✓ Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd NETRA_TAX
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
