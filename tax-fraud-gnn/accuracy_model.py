"""
Model Accuracy and Loss Evaluation Script

This script evaluates the trained GNN fraud detection model on test data,
calculating accuracy, loss percentages, and generating comprehensive performance metrics.
"""

import torch
import torch.nn.functional as F
from torch_geometric.data import DataLoader
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix, 
    precision_score, 
    recall_score, 
    f1_score,
    roc_auc_score,
    roc_curve,
    auc
)
import seaborn as sns


class ModelAccuracyEvaluator:
    """
    Evaluates GNN model accuracy and loss on test data.
    
    Attributes:
        model_path: Path to trained model checkpoint
        device: torch device (cuda or cpu)
        metrics: Dictionary to store evaluation results
    """
    
    def __init__(self, model_path='models/best_model.pt', device=None):
        """
        Initialize the evaluator.
        
        Args:
            model_path: Path to the trained model
            device: torch device (defaults to cuda if available)
        """
        self.model_path = Path(model_path)
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.metrics = {}
        self.model = None
        self.predictions = None
        self.targets = None
        
        print(f"✓ Using device: {self.device}")
        print(f"✓ Model path: {self.model_path}")
    
    def load_model(self, model_class=None):
        """
        Load trained model from checkpoint.
        
        Args:
            model_class: The model class to instantiate (required for loading)
        
        Returns:
            Loaded model
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model_state = checkpoint['model_state_dict']
                self.training_history = checkpoint.get('history', {})
                print(f"✓ Loaded checkpoint with training history")
            else:
                model_state = checkpoint
                self.training_history = {}
            
            if model_class is None:
                raise ValueError("model_class parameter required for loading model")
            
            self.model = model_class.to(self.device)
            self.model.load_state_dict(model_state)
            self.model.eval()
            
            print(f"✓ Model loaded successfully")
            return self.model
        
        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            raise
    
    def evaluate_batch(self, data_loader, loss_fn=F.binary_cross_entropy_with_logits):
        """
        Evaluate model on entire dataset.
        
        Args:
            data_loader: DataLoader with test data
            loss_fn: Loss function to use (default: BCEWithLogitsLoss)
        
        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        self.model.eval()
        total_loss = 0.0
        all_preds = []
        all_targets = []
        num_batches = 0
        
        with torch.no_grad():
            for batch in data_loader:
                batch = batch.to(self.device)
                
                # Forward pass
                logits = self.model(batch.x, batch.edge_index, batch.batch)
                
                # Calculate loss
                loss = loss_fn(logits, batch.y.float().unsqueeze(1))
                total_loss += loss.item()
                num_batches += 1
                
                # Store predictions and targets
                probs = torch.sigmoid(logits).cpu().numpy()
                preds = (probs > 0.5).astype(int).flatten()
                targets = batch.y.cpu().numpy()
                
                all_preds.extend(preds)
                all_targets.extend(targets)
        
        self.predictions = np.array(all_preds)
        self.targets = np.array(all_targets)
        
        avg_loss = total_loss / max(num_batches, 1)
        
        # Calculate metrics
        self._calculate_metrics(avg_loss)
        
        return self.metrics
    
    def _calculate_metrics(self, loss):
        """
        Calculate comprehensive performance metrics.
        
        Args:
            loss: Average loss value
        """
        accuracy = np.mean(self.predictions == self.targets)
        
        # Binary classification metrics
        tn, fp, fn, tp = confusion_matrix(self.targets, self.predictions).ravel()
        
        precision = precision_score(self.targets, self.predictions, zero_division=0)
        recall = recall_score(self.targets, self.predictions, zero_division=0)
        f1 = f1_score(self.targets, self.predictions, zero_division=0)
        
        # Specificity
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # ROC-AUC (if we have probability predictions)
        try:
            roc_auc = roc_auc_score(self.targets, self.predictions)
        except:
            roc_auc = 0.0
        
        self.metrics = {
            'accuracy': round(accuracy * 100, 2),
            'loss': round(loss, 4),
            'loss_percentage': round(loss * 100, 2),
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1 * 100, 2),
            'specificity': round(specificity * 100, 2),
            'roc_auc': round(roc_auc * 100, 2),
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'total_samples': len(self.targets),
            'fraud_cases': int(np.sum(self.targets)),
            'legitimate_cases': int(len(self.targets) - np.sum(self.targets))
        }
    
    def print_report(self):
        """Print formatted evaluation report."""
        if not self.metrics:
            print("✗ No metrics calculated. Run evaluate_batch() first.")
            return
        
        print("\n" + "="*70)
        print("MODEL ACCURACY & LOSS EVALUATION REPORT".center(70))
        print("="*70)
        
        print("\n📊 PRIMARY METRICS:")
        print(f"  Accuracy:              {self.metrics['accuracy']}%")
        print(f"  Loss (Average):        {self.metrics['loss']}")
        print(f"  Loss Percentage:       {self.metrics['loss_percentage']}%")
        
        print("\n📈 CLASSIFICATION METRICS:")
        print(f"  Precision:             {self.metrics['precision']}%")
        print(f"  Recall (Sensitivity):  {self.metrics['recall']}%")
        print(f"  Specificity:           {self.metrics['specificity']}%")
        print(f"  F1 Score:              {self.metrics['f1_score']}%")
        print(f"  ROC-AUC:               {self.metrics['roc_auc']}%")
        
        print("\n🎯 CONFUSION MATRIX:")
        print(f"  True Positives (TP):   {self.metrics['true_positives']}")
        print(f"  True Negatives (TN):   {self.metrics['true_negatives']}")
        print(f"  False Positives (FP):  {self.metrics['false_positives']}")
        print(f"  False Negatives (FN):  {self.metrics['false_negatives']}")
        
        print("\n📋 DATA DISTRIBUTION:")
        print(f"  Total Samples:         {self.metrics['total_samples']}")
        print(f"  Fraud Cases:           {self.metrics['fraud_cases']}")
        print(f"  Legitimate Cases:      {self.metrics['legitimate_cases']}")
        
        print("\n" + "="*70)
    
    def plot_confusion_matrix(self, save_path='results/confusion_matrix.png'):
        """
        Plot and save confusion matrix heatmap.
        
        Args:
            save_path: Path to save the plot
        """
        if self.predictions is None or self.targets is None:
            print("✗ No predictions available. Run evaluate_batch() first.")
            return
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        cm = confusion_matrix(self.targets, self.predictions)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Legitimate', 'Fraud'],
                    yticklabels=['Legitimate', 'Fraud'])
        plt.title('Confusion Matrix - Fraud Detection Model')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        
        print(f"✓ Confusion matrix saved to {save_path}")
    
    def plot_metrics_comparison(self, save_path='results/metrics_comparison.png'):
        """
        Plot metrics comparison bar chart.
        
        Args:
            save_path: Path to save the plot
        """
        if not self.metrics:
            print("✗ No metrics available. Run evaluate_batch() first.")
            return
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1_score', 'specificity']
        values = [self.metrics[m] for m in metrics_to_plot]
        labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Specificity']
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(labels, values, color=['#114C5A', '#FFC801', '#FF9932', '#FF6B6B', '#4ECDC4'])
        plt.ylim(0, 100)
        plt.ylabel('Score (%)')
        plt.title('Model Performance Metrics Comparison')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        
        print(f"✓ Metrics comparison saved to {save_path}")
    
    def plot_loss_distribution(self, save_path='results/loss_distribution.png'):
        """
        Plot loss distribution across predictions.
        
        Args:
            save_path: Path to save the plot
        """
        if self.predictions is None:
            print("✗ No predictions available. Run evaluate_batch() first.")
            return
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate per-sample loss
        errors = np.abs(self.predictions - self.targets)
        
        plt.figure(figsize=(10, 6))
        plt.hist(errors, bins=50, color='#FF9932', alpha=0.7, edgecolor='black')
        plt.axvline(np.mean(errors), color='red', linestyle='--', linewidth=2, label=f'Mean Error: {np.mean(errors):.4f}')
        plt.xlabel('Prediction Error')
        plt.ylabel('Frequency')
        plt.title('Loss Distribution - Prediction Errors')
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        
        print(f"✓ Loss distribution saved to {save_path}")
    
    def save_report_json(self, save_path='results/accuracy_report.json'):
        """
        Save metrics report as JSON.
        
        Args:
            save_path: Path to save the JSON file
        """
        if not self.metrics:
            print("✗ No metrics to save. Run evaluate_batch() first.")
            return
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'device': str(self.device),
            'metrics': self.metrics
        }
        
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Report saved to {save_path}")
    
    def generate_full_report(self, data_loader, model_class=None, output_dir='results'):
        """
        Generate comprehensive evaluation report with visualizations.
        
        Args:
            data_loader: DataLoader with test data
            model_class: Model class for loading
            output_dir: Directory to save results
        """
        print("\n🔍 Starting comprehensive model evaluation...")
        
        # Load model
        if self.model is None:
            self.load_model(model_class)
        
        # Evaluate
        print("\n📊 Evaluating model on test data...")
        self.evaluate_batch(data_loader)
        
        # Print report
        self.print_report()
        
        # Generate visualizations
        print("\n📈 Generating visualizations...")
        self.plot_confusion_matrix(f'{output_dir}/confusion_matrix.png')
        self.plot_metrics_comparison(f'{output_dir}/metrics_comparison.png')
        self.plot_loss_distribution(f'{output_dir}/loss_distribution.png')
        
        # Save JSON report
        print("\n💾 Saving report...")
        self.save_report_json(f'{output_dir}/accuracy_report.json')
        
        print(f"\n✓ Evaluation complete! Results saved to {output_dir}/")


def main():
    """
    Main evaluation script.
    Demonstrates how to use the ModelAccuracyEvaluator.
    """
    # Initialize evaluator
    evaluator = ModelAccuracyEvaluator(model_path='models/best_model.pt')
    
    # Example: Load model and evaluate
    # Note: You need to provide your actual model class and data loader
    
    # This is a template showing how to use the evaluator:
    """
    # Define your model class
    from src.gnn_models.gnn_detector import GNNFraudDetector
    
    # Create data loader with test data
    from torch_geometric.data import DataLoader
    from prepare_real_data import load_processed_data
    
    # Load test dataset
    test_data = load_processed_data('data/processed/test_data.pt')
    test_loader = DataLoader(test_data, batch_size=32, shuffle=False)
    
    # Run evaluation
    evaluator.generate_full_report(
        data_loader=test_loader,
        model_class=GNNFraudDetector,
        output_dir='results'
    )
    """
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║      MODEL ACCURACY & LOSS EVALUATION SCRIPT                  ║
╚═══════════════════════════════════════════════════════════════╝

This script evaluates GNN fraud detection model performance.

USAGE INSTRUCTIONS:
───────────────────

1. Ensure you have:
   - A trained model at 'models/best_model.pt'
   - Test data prepared and accessible
   
2. Modify the main() function to:
   - Import your model class
   - Load your test data
   - Create a DataLoader
   
3. Call evaluator.generate_full_report() with:
   - data_loader: Your test data loader
   - model_class: Your GNN model class
   - output_dir: Where to save results

EXAMPLE:
────────

    from accuracy_model import ModelAccuracyEvaluator
    from src.gnn_models.gnn_detector import GNNFraudDetector
    from torch_geometric.data import DataLoader
    
    # Load test data
    test_loader = DataLoader(test_data, batch_size=32)
    
    # Evaluate
    evaluator = ModelAccuracyEvaluator('models/best_model.pt')
    evaluator.generate_full_report(
        test_loader,
        GNNFraudDetector,
        'results'
    )

OUTPUTS GENERATED:
──────────────────
✓ Console report with all metrics
✓ Confusion matrix heatmap (PNG)
✓ Metrics comparison bar chart (PNG)
✓ Loss distribution histogram (PNG)
✓ JSON report file with detailed metrics

METRICS TRACKED:
────────────────
- Accuracy, Loss, Loss Percentage
- Precision, Recall, Specificity, F1 Score
- ROC-AUC Score
- True Positives/Negatives, False Positives/Negatives
- Data distribution (fraud vs legitimate cases)
    """)


if __name__ == '__main__':
    main()
