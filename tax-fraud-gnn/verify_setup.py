"""
Verification script to check if project is set up correctly
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Verify all required directories exist"""
    print("\n📁 Checking Directory Structure...")
    
    required_dirs = [
        "data/raw",
        "data/processed",
        "data/processed/graphs",
        "models",
        "notebooks",
        "src/data_processing",
        "src/graph_construction",
        "src/gnn_models",
        "src/api",
        "dashboard",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ (MISSING)")
            all_exist = False
    
    return all_exist


def check_files():
    """Verify all required files exist"""
    print("\n📄 Checking Key Files...")
    
    required_files = {
        "requirements.txt": "Dependencies",
        "README.md": "Main documentation",
        "QUICKSTART.md": "Quick start guide",
        "PROBLEM_STATEMENT_ANALYSIS.md": "Problem analysis",
        "config.py": "Configuration",
        "setup.bat": "Windows setup script",
        "setup.sh": "Linux/macOS setup script",
        "run_pipeline.py": "Pipeline runner",
        "init_project.py": "Project initializer",
        "src/data_processing/generate_sample_data.py": "Data generator",
        "src/data_processing/clean_data.py": "Data cleaner",
        "src/graph_construction/build_graph.py": "Graph builder",
        "src/gnn_models/train_gnn.py": "GNN trainer",
        "dashboard/app.py": "Streamlit dashboard",
        "src/api/app.py": "Flask API",
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        full_path = Path(file_path)
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            print(f"  ✅ {file_path} ({size_kb:.1f} KB) - {description}")
        else:
            print(f"  ❌ {file_path} (MISSING) - {description}")
            all_exist = False
    
    return all_exist


def check_virtual_env():
    """Check if virtual environment exists"""
    print("\n🐍 Checking Virtual Environment...")
    
    if sys.prefix != sys.base_prefix:
        print(f"  ✅ Virtual environment is ACTIVE")
        print(f"     Location: {sys.prefix}")
        return True
    else:
        if Path("venv").exists():
            print(f"  ⚠️  Virtual environment exists but NOT ACTIVATED")
            print(f"     Activate with: .\\venv\\Scripts\\activate (Windows)")
            print(f"     Or: source venv/bin/activate (Linux/macOS)")
            return True
        else:
            print(f"  ❌ Virtual environment NOT FOUND")
            print(f"     Create with: python -m venv venv")
            return False


def check_dependencies():
    """Check if key packages are installed"""
    print("\n📦 Checking Dependencies...")
    
    packages = [
        ("pandas", "Data manipulation"),
        ("numpy", "Numerical computing"),
        ("torch", "PyTorch"),
        ("torch_geometric", "Graph Neural Networks"),
        ("networkx", "Network analysis"),
        ("streamlit", "Dashboard"),
        ("flask", "REST API"),
        ("sklearn", "Machine learning"),
    ]
    
    all_installed = True
    for package_name, description in packages:
        try:
            __import__(package_name)
            print(f"  ✅ {package_name} - {description}")
        except ImportError:
            print(f"  ❌ {package_name} - {description} (NOT INSTALLED)")
            all_installed = False
    
    return all_installed


def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("  Project Setup Verification")
    print("=" * 60)
    
    checks = {
        "Directory Structure": check_directory_structure(),
        "Required Files": check_files(),
        "Virtual Environment": check_virtual_env(),
        "Dependencies": check_dependencies(),
    }
    
    print("\n" + "=" * 60)
    print("  Verification Summary")
    print("=" * 60)
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name}: {status}")
    
    all_passed = all(checks.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✅ ALL CHECKS PASSED!")
        print("  Ready to start the pipeline.")
        print("\n  Next steps:")
        print("  1. cd src/data_processing")
        print("  2. python generate_sample_data.py")
        print("  3. python clean_data.py")
        print("  4. cd ../graph_construction")
        print("  5. python build_graph.py")
        print("  6. cd ../gnn_models")
        print("  7. python train_gnn.py")
        print("  8. cd ../../dashboard")
        print("  9. streamlit run app.py")
    else:
        print("  ⚠️  Some checks failed.")
        print("  Please fix issues before running pipeline.")
        print("\n  For detailed setup, see QUICKSTART.md")
    
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
