# Running Everything Inside the Virtual Environment

Your project is set up to run entirely inside the `big` virtualenv located at `C:\BIG HACK\big\`.

## Quick Start: One-Command Pipeline

```powershell
cd 'c:\BIG HACK\tax-fraud-gnn'
.\run_everything.bat
```

This single command will:
1. ✅ Install all dependencies into the venv
2. ✅ Prepare and analyze your real datasets
3. ✅ Train the GNN model
4. ✅ Start the Flask dashboard at http://localhost:5000

---

## Manual Commands (if you want to run steps individually)

### Option 1: Using PowerShell

```powershell
# Navigate to project
cd 'c:\BIG HACK\tax-fraud-gnn'

# Install dependencies (one-time setup)
& 'C:/BIG HACK/big/Scripts/python.exe' -m pip install -r requirements.txt

# Prepare data
& 'C:/BIG HACK/big/Scripts/python.exe' prepare_real_data.py

# Train model
& 'C:/BIG HACK/big/Scripts/python.exe' train_gnn_model.py

# Start Flask app (dashboard opens at http://localhost:5000)
& 'C:/BIG HACK/big/Scripts/python.exe' app.py
```

### Option 2: Using the PowerShell Helper

```powershell
cd 'c:\BIG HACK\tax-fraud-gnn'

# Run any script through the venv python
.\venv_run.ps1 prepare_real_data.py
.\venv_run.ps1 train_gnn_model.py
.\venv_run.ps1 app.py
```

### Option 3: Using the Batch Helper

```cmd
cd C:\BIG HACK\tax-fraud-gnn

REM Run any script through the venv python
venv_run.bat prepare_real_data.py
venv_run.bat train_gnn_model.py
venv_run.bat app.py
```

---

## Key Points

✅ **No need to activate the venv** — all commands use the venv python directly  
✅ **All packages are in the venv** — pandas, torch, flask, etc. are all installed there  
✅ **Consistent environment** — every command uses `C:\BIG HACK\big\Scripts\python.exe`  
✅ **Easy to repeat** — use the same commands every time you run the pipeline

---

## Troubleshooting

**Q: "ModuleNotFoundError: No module named 'X'"**  
A: Install it into the venv:
```powershell
& 'C:/BIG HACK/big/Scripts/python.exe' -m pip install <package-name>
```

**Q: "can't open file" error**  
A: Make sure you're in the project directory and using the full path to the script:
```powershell
cd 'c:\BIG HACK\tax-fraud-gnn'
& 'C:/BIG HACK/big/Scripts/python.exe' prepare_real_data.py
```

**Q: Flask app not loading on localhost:5000**  
A: The app should be running. Open http://localhost:5000 in your browser once the app starts (look for "Running on http://127.0.0.1:5000").

---

## What's Already Done

✅ Data preparation: `prepare_real_data.py` → outputs in `data/processed/`  
✅ Model training: `train_gnn_model.py` → model saved to `models/best_model.pt`  
✅ All requirements installed in the venv (`requirements.txt`)  
✅ Project package installed: `tax_fraud_gnn` (editable mode)  

---

## Next: Start the Dashboard

To see your fraud detection model in action:

```powershell
cd 'c:\BIG HACK\tax-fraud-gnn'
& 'C:/BIG HACK/big/Scripts/python.exe' app.py
```

Then open **http://localhost:5000** in your browser!
