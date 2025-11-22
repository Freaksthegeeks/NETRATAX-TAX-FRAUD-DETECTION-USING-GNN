"""
NETRA TAX - System Diagnostic and Verification Script
Checks if all components are properly configured
"""

import os
import sys
import subprocess
from pathlib import Path

def check_directory_structure():
    """Check if all required directories exist"""
    print("\n" + "="*70)
    print("1️⃣  DIRECTORY STRUCTURE CHECK")
    print("="*70)
    
    required_dirs = [
        "NETRA_TAX/backend",
        "NETRA_TAX/frontend",
        "NETRA_TAX/frontend/js",
        "NETRA_TAX/frontend/css",
        "tax-fraud-gnn/data/processed",
        "tax-fraud-gnn/models",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} NOT FOUND")
            all_exist = False
    
    return all_exist

def check_files():
    """Check if required files exist"""
    print("\n" + "="*70)
    print("2️⃣  REQUIRED FILES CHECK")
    print("="*70)
    
    required_files = [
        ("NETRA_TAX/backend/main.py", "FastAPI backend"),
        ("NETRA_TAX/backend/requirements.txt", "Python dependencies"),
        ("NETRA_TAX/frontend/index.html", "Dashboard page"),
        ("NETRA_TAX/frontend/js/api.js", "API client"),
        ("NETRA_TAX/frontend/css/style.css", "Styling"),
        ("tax-fraud-gnn/models/best_model.pt", "Trained GNN model"),
        ("tax-fraud-gnn/data/processed/graphs/graph_data.pt", "Graph data"),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            print(f"✅ {file_path} ({size_mb:.1f} MB) - {description}")
        else:
            print(f"⚠️  {file_path} NOT FOUND - {description}")
            all_exist = False
    
    return all_exist

def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n" + "="*70)
    print("3️⃣  PYTHON PACKAGES CHECK")
    print("="*70)
    
    required_packages = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("torch", "PyTorch"),
        ("torch_geometric", "PyTorch Geometric"),
        ("pandas", "Data processing"),
        ("numpy", "Numerical computing"),
        ("networkx", "Network analysis"),
        ("pydantic", "Data validation"),
    ]
    
    all_installed = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} NOT INSTALLED - {description}")
            all_installed = False
    
    return all_installed

def check_ports():
    """Check if required ports are available"""
    print("\n" + "="*70)
    print("4️⃣  PORTS AVAILABILITY CHECK")
    print("="*70)
    
    import socket
    
    ports = [
        (8000, "FastAPI Backend"),
        (8080, "Frontend HTTP Server"),
        (5432, "PostgreSQL (optional)"),
    ]
    
    available = True
    for port, service in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} ({service}) - IN USE")
            available = False
        else:
            print(f"✅ Port {port} ({service}) - AVAILABLE")
    
    return available

def check_api_endpoints():
    """Check if API endpoints are responding"""
    print("\n" + "="*70)
    print("5️⃣  API ENDPOINTS CHECK")
    print("="*70)
    
    print("⏳ Checking API endpoints...")
    print("(Backend must be running on port 8000)")
    
    endpoints_to_check = [
        "/api/health",
        "/api/system/stats",
        "/api/fraud/summary",
    ]
    
    try:
        import requests
        base_url = "http://localhost:8000"
        
        for endpoint in endpoints_to_check:
            try:
                response = requests.get(base_url + endpoint, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Responding")
                else:
                    print(f"⚠️  {endpoint} - Status {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - {str(e)}")
                print("   (Make sure backend is running: python -m uvicorn backend.main:app)")
    except ImportError:
        print("⚠️  'requests' module not installed, skipping endpoint check")
        print("   Install with: pip install requests")

def check_frontend_pages():
    """Check if all frontend pages exist"""
    print("\n" + "="*70)
    print("6️⃣  FRONTEND PAGES CHECK")
    print("="*70)
    
    pages = [
        "index.html",
        "login.html",
        "company-explorer.html",
        "invoice-explorer.html",
        "graph-visualizer.html",
        "reports.html",
        "admin.html",
        "upload.html",
    ]
    
    frontend_dir = Path("NETRA_TAX/frontend")
    all_exist = True
    
    for page in pages:
        page_path = frontend_dir / page
        if page_path.exists():
            size_kb = page_path.stat().st_size / 1024
            print(f"✅ {page} ({size_kb:.1f} KB)")
        else:
            print(f"❌ {page} NOT FOUND")
            all_exist = False
    
    return all_exist

def generate_report(results):
    """Generate final diagnostic report"""
    print("\n" + "="*70)
    print("📊 DIAGNOSTIC REPORT SUMMARY")
    print("="*70)
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)
    
    print(f"\nPassed: {passed_checks}/{total_checks} checks")
    
    if passed_checks == total_checks:
        print("\n🎉 All systems operational! You're ready to:")
        print("   1. Run: .\start_backend.bat")
        print("   2. Run: python -m http.server 8080 (in frontend dir)")
        print("   3. Open: http://localhost:8080/index.html")
    else:
        print("\n⚠️  Some checks failed. Please review:")
        for check_name, result in results.items():
            if not result:
                print(f"   - {check_name}")

def main():
    """Run all diagnostic checks"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║   NETRA TAX - System Diagnostic Tool                          ║
║   Verifying all components are properly configured            ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Change to project root if needed
    if Path("NETRA_TAX").exists():
        os.chdir(".")
    
    results = {
        "Directory Structure": check_directory_structure(),
        "Required Files": check_files(),
        "Python Packages": check_python_packages(),
        "Port Availability": check_ports(),
        "Frontend Pages": check_frontend_pages(),
    }
    
    check_api_endpoints()
    
    generate_report(results)
    
    print("\n" + "="*70)
    print("✅ Diagnostic complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
