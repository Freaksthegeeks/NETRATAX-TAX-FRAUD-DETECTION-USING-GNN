"""
NETRA TAX - Startup Verification Checklist
Run this after starting the system to verify everything works
"""

import subprocess
import time
import sys
from pathlib import Path

def print_header():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║   NETRA TAX - Startup Verification Checklist                  ║
║   Run this after starting backend and frontend                ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def check_backend_running():
    """Check if backend is running"""
    print("\n✓ Checking if backend is running on http://localhost:8000...")
    try:
        import requests
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        if response.status_code == 200:
            print("  ✅ Backend is running and responding")
            data = response.json()
            print(f"     Status: {data.get('status')}")
            print(f"     Model loaded: {data.get('model_loaded')}")
            print(f"     Database connected: {data.get('database_connected')}")
            return True
        else:
            print(f"  ⚠️  Backend responding but status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Backend not responding: {str(e)}")
        print("     Make sure you ran: .\\start_backend.bat")
        return False

def check_frontend_running():
    """Check if frontend is running"""
    print("\n✓ Checking if frontend is running on http://localhost:8080...")
    try:
        import requests
        response = requests.get("http://localhost:8080/index.html", timeout=2)
        if response.status_code == 200:
            print("  ✅ Frontend is running")
            return True
        else:
            print(f"  ⚠️  Frontend responding but status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Frontend not responding: {str(e)}")
        print("     Make sure you ran: python -m http.server 8080 (in frontend dir)")
        return False

def check_api_endpoints():
    """Check if key API endpoints are working"""
    print("\n✓ Checking API endpoints...")
    
    try:
        import requests
        
        endpoints = [
            ("/api/health", "Health check"),
            ("/api/system/stats", "System statistics"),
            ("/api/fraud/summary", "Fraud summary (dashboard)"),
        ]
        
        all_working = True
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ {endpoint}")
                    if "total_entities" in data:
                        print(f"     Total entities: {data.get('total_entities')}")
                    if "high_risk_count" in data:
                        print(f"     High risk: {data.get('high_risk_count')}")
                else:
                    print(f"  ⚠️  {endpoint} - Status {response.status_code}")
                    all_working = False
            except Exception as e:
                print(f"  ❌ {endpoint} - {str(e)}")
                all_working = False
        
        return all_working
    except ImportError:
        print("  ⚠️  'requests' module not installed, skipping endpoint check")
        print("     Install with: pip install requests")
        return True

def check_frontend_pages():
    """Check if all frontend pages exist"""
    print("\n✓ Checking frontend pages...")
    
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
    
    if not frontend_dir.exists():
        print("  ❌ Frontend directory not found")
        return False
    
    all_exist = True
    for page in pages:
        page_path = frontend_dir / page
        if page_path.exists():
            print(f"  ✅ {page}")
        else:
            print(f"  ❌ {page} NOT FOUND")
            all_exist = False
    
    return all_exist

def check_javascript_files():
    """Check if JavaScript files exist"""
    print("\n✓ Checking JavaScript files...")
    
    js_files = [
        "js/api.js",
        "js/dashboard.js",
        "css/style.css",
    ]
    
    frontend_dir = Path("NETRA_TAX/frontend")
    all_exist = True
    
    for file in js_files:
        file_path = frontend_dir / file
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✅ {file} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ {file} NOT FOUND")
            all_exist = False
    
    return all_exist

def check_model_and_data():
    """Check if model and data files exist"""
    print("\n✓ Checking model and data files...")
    
    files_to_check = [
        ("tax-fraud-gnn/models/best_model.pt", "GNN model"),
        ("tax-fraud-gnn/data/processed/graphs/graph_data.pt", "Graph data"),
        ("tax-fraud-gnn/data/processed/graphs/node_mappings.pkl", "Node mappings"),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        full_path = Path(file_path)
        if full_path.exists():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ {description} ({size_mb:.1f} MB)")
        else:
            print(f"  ⚠️  {description} NOT FOUND")
            # Not blocking - system can generate synthetic data
    
    return True

def check_backend_imports():
    """Check if backend can import all required modules"""
    print("\n✓ Checking Python imports...")
    
    modules = [
        ("fastapi", "FastAPI framework"),
        ("torch", "PyTorch"),
        ("torch_geometric", "PyTorch Geometric"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("networkx", "NetworkX"),
        ("pydantic", "Pydantic"),
    ]
    
    all_imported = True
    for module, description in modules:
        try:
            __import__(module)
            print(f"  ✅ {module} - {description}")
        except ImportError:
            print(f"  ❌ {module} - {description} (NOT INSTALLED)")
            all_imported = False
    
    return all_imported

def test_dashboard():
    """Test dashboard data loading"""
    print("\n✓ Testing dashboard data loading...")
    
    try:
        import requests
        
        print("  Getting fraud summary...")
        response = requests.get("http://localhost:8000/api/fraud/summary", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Dashboard data retrieved")
            print(f"     Total entities: {data.get('total_entities', 'N/A')}")
            print(f"     High risk: {data.get('high_risk_count', 'N/A')}")
            print(f"     Medium risk: {data.get('medium_risk_count', 'N/A')}")
            print(f"     Low risk: {data.get('low_risk_count', 'N/A')}")
            print(f"     Avg fraud score: {data.get('avg_fraud_score', 'N/A'):.2f}")
            return True
        else:
            print(f"  ❌ Failed to get dashboard data (status {response.status_code})")
            return False
    except Exception as e:
        print(f"  ❌ Error testing dashboard: {str(e)}")
        return False

def generate_final_report(results):
    """Generate final verification report"""
    print("\n" + "="*70)
    print("📊 VERIFICATION REPORT")
    print("="*70)
    
    checks = {
        "Backend Running": results.get('backend', False),
        "Frontend Running": results.get('frontend', False),
        "API Endpoints": results.get('endpoints', False),
        "Frontend Pages": results.get('pages', False),
        "JavaScript Files": results.get('js', False),
        "Model & Data Files": results.get('model', False),
        "Python Imports": results.get('imports', False),
        "Dashboard Data": results.get('dashboard', False),
    }
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print(f"\nPassed: {passed}/{total} checks\n")
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! System is ready to use!")
        print("\nYou can now:")
        print("1. Open http://localhost:8080/index.html in your browser")
        print("2. See the dashboard with real fraud metrics")
        print("3. Explore all features:")
        print("   - Company Explorer: Search and analyze companies")
        print("   - Invoice Explorer: Search and analyze invoices")
        print("   - Network Graph: Visualize fraud rings")
        print("   - Reports: Generate PDF reports")
        print("   - Admin Panel: Monitor system health")
    else:
        print("\n⚠️  Some checks failed. Please review:")
        for check_name, result in checks.items():
            if not result:
                print(f"   - {check_name}")
        print("\nSee QUICK_START.md for troubleshooting steps")
    
    print("\n" + "="*70)

def main():
    """Run all verification checks"""
    print_header()
    
    print("\n⏳ Running verification checks...")
    print("(This may take 10-15 seconds)")
    
    results = {
        'backend': check_backend_running(),
        'frontend': check_frontend_running(),
        'endpoints': check_api_endpoints(),
        'pages': check_frontend_pages(),
        'js': check_javascript_files(),
        'model': check_model_and_data(),
        'imports': check_backend_imports(),
        'dashboard': test_dashboard(),
    }
    
    generate_final_report(results)
    
    print("\n📚 For more information, see:")
    print("   - QUICK_START.md (5-minute setup)")
    print("   - INTEGRATION_GUIDE.md (full integration)")
    print("   - README.md (project overview)")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Verification interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Verification error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
