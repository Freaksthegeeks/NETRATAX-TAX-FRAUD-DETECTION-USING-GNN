"""
Full Pipeline Runner - Execute entire workflow
"""

import subprocess
import sys
import os
from pathlib import Path

class PipelineRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.steps = [
            ("Generate Sample Data", "python src/data_processing/generate_sample_data.py"),
            ("Clean Data", "python src/data_processing/clean_data.py"),
            ("Build Graph", "python src/graph_construction/build_graph.py"),
            ("Train GNN Model", "python src/gnn_models/train_gnn.py"),
        ]
    
    def run_step(self, name, command):
        """Run a single pipeline step"""
        print("\n" + "=" * 60)
        print(f"📍 Step: {name}")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.project_root),
                capture_output=False
            )
            
            if result.returncode != 0:
                print(f"\n❌ {name} failed with return code {result.returncode}")
                return False
            
            print(f"\n✅ {name} completed successfully")
            return True
        
        except Exception as e:
            print(f"\n❌ Error running {name}: {e}")
            return False
    
    def run_all(self):
        """Execute complete pipeline"""
        print("\n" + "=" * 60)
        print("🚀 TAX FRAUD DETECTION PIPELINE")
        print("=" * 60)
        
        failed_steps = []
        
        for step_name, command in self.steps:
            success = self.run_step(step_name, command)
            if not success:
                failed_steps.append(step_name)
                response = input(f"\n{step_name} failed. Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("\n❌ Pipeline aborted")
                    return False
        
        print("\n" + "=" * 60)
        if not failed_steps:
            print("✅ PIPELINE COMPLETE - All steps successful!")
        else:
            print(f"⚠️  PIPELINE COMPLETE - {len(failed_steps)} step(s) failed:")
            for step in failed_steps:
                print(f"   - {step}")
        print("=" * 60)
        print("\n🎉 Next: Run 'streamlit run dashboard/app.py' to launch dashboard")
        print("=" * 60 + "\n")
        
        return len(failed_steps) == 0


if __name__ == "__main__":
    runner = PipelineRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
