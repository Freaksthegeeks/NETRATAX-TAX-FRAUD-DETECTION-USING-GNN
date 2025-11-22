"""
Initialize required directories and create empty __init__.py files
"""

from pathlib import Path

# Create __init__.py files for packages
packages = [
    "src/data_processing",
    "src/graph_construction",
    "src/gnn_models",
    "src/api",
]

for pkg in packages:
    init_file = Path(__file__).parent / pkg / "__init__.py"
    init_file.touch()
    print(f"Created {init_file}")

print("✅ Package initialization complete")
