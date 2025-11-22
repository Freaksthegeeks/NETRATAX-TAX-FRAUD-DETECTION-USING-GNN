# 🚀 Quick Start Guide - Tax Fraud Detection GNN

## ⚡ 5-Minute Setup (Windows)

### Step 1: Run Setup Script

```powershell
cd "c:\BIG HACK\tax-fraud-gnn"
.\setup.bat
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Initialize project structure

### Step 2: Generate Sample Data

```powershell
cd src\data_processing
python generate_sample_data.py
```

Output: Creates `companies.csv` and `invoices.csv`

### Step 3: Process & Build Graph

```powershell
python clean_data.py
cd ..\graph_construction
python build_graph.py
```

### Step 4: Train Model

```powershell
cd ..\gnn_models
python train_gnn.py
```

Training will take 2-5 minutes depending on your system.

### Step 5: Launch Dashboard

```powershell
cd ..\..\dashboard
streamlit run app.py
```

Open browser → `http://localhost:8501`

---

## 📊 Dashboard Features

Once dashboard is running:

1. **📈 Overview Tab**
   - Total companies & high-risk statistics
   - Fraud distribution charts
   - Risk score histogram

2. **🔍 Detailed Analysis Tab**
   - Search companies by ID
   - View detailed company information
   - Analyze transaction networks

3. **⚠️ Risk Scoring Tab**
   - Risk distribution by location
   - Turnover vs Risk scatter plot
   - Model explanations

4. **📡 Network Insights Tab**
   - Graph statistics (nodes, edges, density)
   - Top invoice senders/receivers
   - Transaction pattern analysis

---

## 🎯 What's Happening Behind the Scenes?

### Data Flow

```
Raw CSV Data
    ↓
[Clean & Engineer Features]
    ↓
[Build Transaction Network Graph]
    ↓
[Train GNN Model]
    ↓
[Make Predictions]
    ↓
[Visualize in Dashboard]
```

### Model Architecture

```
Node Features (3):
  ├─ Turnover
  ├─ Sent Invoice Count
  └─ Received Invoice Count
        ↓
    [GCN Layer 1: 64 neurons]
        ↓
    [GCN Layer 2: 64 neurons]
        ↓
    [GCN Layer 3: 2 classes]
        ↓
    Output: [P(Normal), P(Fraud)]
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/data_processing/generate_sample_data.py` | Create synthetic tax data |
| `src/data_processing/clean_data.py` | Clean & engineer features |
| `src/graph_construction/build_graph.py` | Build network graphs |
| `src/gnn_models/train_gnn.py` | Train fraud detection model |
| `dashboard/app.py` | Interactive Streamlit dashboard |
| `src/api/app.py` | REST API for predictions |

---

## 🔧 Useful Commands

### Reactivate Virtual Environment (if terminal closed)

```powershell
# Windows
cd "c:\BIG HACK\tax-fraud-gnn"
.\venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### Run Individual Steps

```powershell
# Generate new sample data
cd src\data_processing
python generate_sample_data.py

# Rebuild graph
cd ..\graph_construction
python build_graph.py

# Retrain model
cd ..\gnn_models
python train_gnn.py

# Launch dashboard
cd ..\..\dashboard
streamlit run app.py

# Start REST API
cd ..\src\api
python app.py
```

### Run Complete Pipeline

```powershell
python run_pipeline.py
```

---

## 📊 Expected Results

After training, you should see:

```
STARTING MODEL TRAINING
========================================================
Epoch  10 | Train Loss: 0.4231 | Val Loss: 0.3821 | Val Acc: 0.8234
Epoch  20 | Train Loss: 0.3122 | Val Loss: 0.2956 | Val Acc: 0.8512
...
Epoch 100 | Train Loss: 0.1823 | Val Loss: 0.1945 | Val Acc: 0.8745

========================================================
TEST RESULTS
========================================================
ACCURACY: 0.8612
PRECISION: 0.8234
RECALL: 0.7856
F1: 0.8043
AUC_ROC: 0.8834
========================================================
✅ TRAINING COMPLETE
```

---

## 🐛 Common Issues & Fixes

### Issue: "ModuleNotFoundError"
**Solution:** Make sure venv is activated
```powershell
.\venv\Scripts\activate
```

### Issue: "torch-geometric installation error"
**Solution:** Install system dependencies first
```powershell
pip install torch-geometric --no-build-isolation
```

### Issue: "Port 8501 already in use"
**Solution:** Use different port
```powershell
streamlit run dashboard/app.py --server.port 8502
```

### Issue: "CUDA out of memory"
**Solution:** Use CPU instead
```powershell
# Edit train_gnn.py, change: self.device = torch.device("cpu")
```

---

## 🎓 Next Steps

1. **Experiment with hyperparameters:**
   - Edit `MODEL_CONFIG` in `config.py`
   - Change learning rate, epochs, hidden channels
   - See how it affects accuracy

2. **Use real data:**
   - Replace `companies.csv` and `invoices.csv` in `data/raw/`
   - Run the same pipeline steps
   - Evaluate on real fraud patterns

3. **Deploy to production:**
   - Use API (`src/api/app.py`) for backend integration
   - Containerize with Docker
   - Deploy to cloud (AWS, Azure, GCP)

4. **Improve model:**
   - Try GAT (Graph Attention Networks)
   - Add temporal features
   - Ensemble with other models

---

## 📚 Learn More

- **PyTorch Geometric:** https://pytorch-geometric.readthedocs.io/
- **Streamlit:** https://streamlit.io/
- **GNN Fundamentals:** https://arxiv.org/abs/1812.04202

---

## 🆘 Need Help?

1. Check `README.md` for detailed documentation
2. Review `config.py` for configuration options
3. Check logs in terminal output
4. Verify data files exist: `ls data/raw/`

---

**You're all set! Happy fraud detection! 🚨**

