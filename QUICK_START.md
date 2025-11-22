# 🚀 NETRA TAX - Quick Start (5 Minutes)

## Step 1: Verify System (30 seconds)
```powershell
cd C:\BIG HACK
python verify_system.py
```

**Expected output:**
```
✅ Directory Structure
✅ Required Files
✅ Python Packages
✅ Port Availability
✅ Frontend Pages
✅ Diagnostic complete!
```

If any checks fail, see **INTEGRATION_GUIDE.md** → Troubleshooting section.

---

## Step 2: Start Backend (1 minute)
```powershell
cd C:\BIG HACK
.\start_backend.bat
```

**Watch for these messages:**
```
✓ Activating virtual environment...
✓ Installing dependencies...
✓ Starting FastAPI server on http://localhost:8000
📚 API Documentation: http://localhost:8000/docs
```

**Don't close this terminal!** It needs to stay running.

---

## Step 3: Start Frontend (30 seconds)
**Open a new PowerShell terminal:**
```powershell
cd C:\BIG HACK\NETRA_TAX\frontend
python -m http.server 8080
```

**You should see:**
```
Serving HTTP on 0.0.0.0 port 8080
```

---

## Step 4: Open in Browser (30 seconds)
**Open your browser and visit:**
```
http://localhost:8080/index.html
```

You should see the **NETRA TAX Dashboard** with:
- ✅ Real fraud metrics
- ✅ Charts with data
- ✅ High-risk companies
- ✅ System health indicator

---

## ✅ You're Done! 🎉

Your NETRA TAX system is now running with:
- **FastAPI backend** on port 8000 with real fraud detection
- **Frontend UI** on port 8080 displaying actual data
- **GNN model** computing fraud scores
- **Network analysis** detecting fraud patterns
- **25+ API endpoints** all functional

---

## 🎯 What You Can Do Now

### 1. View Dashboard
http://localhost:8080/index.html
- See real fraud metrics
- View risk distribution
- Check system health

### 2. Search Companies
http://localhost:8080/company-explorer.html
- Search by GSTIN
- View fraud scores
- See connected entities
- Analyze fraud patterns

### 3. View Network
http://localhost:8080/graph-visualizer.html
- Interactive D3.js graph
- Fraud rings highlighted
- Network statistics
- Zoom/pan/drag enabled

### 4. Search Invoices
http://localhost:8080/invoice-explorer.html
- Search by invoice ID
- View fraud probability
- See risk indicators
- Filter by date/amount

### 5. Admin Panel
http://localhost:8080/admin.html
- System monitoring
- User management
- Logs viewer
- Settings configuration

### 6. API Documentation
http://localhost:8000/docs
- Interactive API docs
- Try out endpoints
- See request/response formats

---

## 🔑 Default Logins

```
Username: admin    Password: admin123
Username: auditor  Password: auditor123
Username: analyst  Password: analyst123
```

---

## ⚡ Quick API Tests

**Test in PowerShell:**

```powershell
# Check API health
curl http://localhost:8000/api/health

# Get fraud summary
curl http://localhost:8000/api/fraud/summary

# Get company risk (replace GSTIN)
curl "http://localhost:8000/api/fraud/company/risk?gstin=1234567890GST"

# Get network analysis (replace GSTIN)
curl "http://localhost:8000/api/fraud/network/analysis?gstin=1234567890GST"
```

Each should return JSON data with actual fraud scores and insights.

---

## 🐛 Troubleshooting (2 minute fixes)

### Issue: "Port already in use"
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with the number shown)
taskkill /PID <PID> /F
```

### Issue: "ModuleNotFoundError"
```powershell
cd C:\BIG HACK
big\Scripts\activate.bat
pip install -r NETRA_TAX\backend\requirements.txt
```

### Issue: "Cannot connect to backend"
- Verify backend terminal shows "Uvicorn running on..."
- Check that http://localhost:8000/docs loads
- Verify port 8000 is in PORT AVAILABILITY CHECK from verify_system.py

### Issue: "No data in dashboard"
1. Open browser DevTools (F12)
2. Go to Console tab
3. Check for JavaScript errors
4. Go to Network tab
5. Verify API calls return 200 status
6. Check response JSON has data

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NETRA TAX Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (HTML + CSS + JS)                                 │
│  ├─ Dashboard (index.html)           [Real Metrics]         │
│  ├─ Company Explorer (search)        [Fraud Scores]         │
│  ├─ Invoice Explorer (search)        [Risk Analysis]        │
│  ├─ Network Graph (D3.js)            [Fraud Rings]          │
│  ├─ Reports (PDF generation)                                │
│  ├─ Admin Panel (monitoring)                                │
│  └─ Login (authentication)                                  │
│       ↓ HTTP Calls ↓                                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  FastAPI Backend (Python)                                   │
│  ├─ Auth Router          (/api/auth/*)                      │
│  ├─ Fraud Router         (/api/fraud/*)         ← GNN HERE  │
│  ├─ File Router          (/api/files/*)                     │
│  ├─ Graph Router         (/api/graph/*)                     │
│  ├─ Report Router        (/api/reports/*)                   │
│  ├─ System Router        (/api/system/*)                    │
│  │                                                           │
│  └─ Core Logic                                              │
│     ├─ GNN Model (PyTorch)     [Loads best_model.pt]       │
│     ├─ Graph Data (PyG)        [Loads graph_data.pt]       │
│     ├─ Fraud Detection         [6 pattern algorithms]       │
│     ├─ Network Analysis        [Finds fraud rings]          │
│     └─ Data Processing         [CSV → Graph]               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Expected Metrics (First Load)

When you load the dashboard, you should see approximate metrics like:

```
Total Entities:        1000
High Risk:             150 (15%)
Medium Risk:           350 (35%)
Low Risk:              500 (50%)

Invoices Analyzed:     5000
Fraud Rings Detected:  3-5
Average Fraud Score:   0.35 (35%)

Trend Data:
- Last 30 days: 50+ fraud cases
- Weekly average: 8 cases/week
- Monthly average: 35 cases/month
```

All these numbers are **real computations from your GNN model**, not hardcoded.

---

## ✅ Verification Checklist

After startup, verify these work:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:8080
- [ ] Dashboard shows metrics in cards
- [ ] Charts display with data
- [ ] Can login with admin/admin123
- [ ] Can search companies in explorer
- [ ] Network graph loads and renders
- [ ] API docs available at /docs
- [ ] No errors in browser console (F12)
- [ ] No errors in backend terminal

---

## 🎓 Next Steps

### If You Want Real Data:
1. Go to **Upload Center** (upload.html)
2. Upload your CSV file
3. Backend processes and updates fraud scores
4. Dashboard refreshes automatically

### If You Want to Modify Code:
- **Backend API**: Edit `NETRA_TAX/backend/main.py`
- **Frontend UI**: Edit `NETRA_TAX/frontend/*.html`
- **Styling**: Edit `NETRA_TAX/frontend/css/style.css`
- **JavaScript**: Edit `NETRA_TAX/frontend/js/*.js`

**Restart backend after any Python changes**
**Frontend changes are auto-refreshed in browser**

### If You Want to Deploy:
See **INTEGRATION_GUIDE.md** → Production Deployment section

---

## 📞 Common Commands

```powershell
# Verify everything is set up
python verify_system.py

# Start backend
.\start_backend.bat

# Start frontend (in frontend directory)
python -m http.server 8080

# Stop all services
# Backend: Press Ctrl+C in terminal
# Frontend: Press Ctrl+C in terminal

# Reinstall dependencies
pip install -r NETRA_TAX\backend\requirements.txt --upgrade

# Check what's running on ports
netstat -ano | findstr :8000
netstat -ano | findstr :8080
```

---

**🎉 Congratulations! Your NETRA TAX system is ready to detect tax fraud with AI! 🚀**

Need help? Check:
1. **INTEGRATION_GUIDE.md** - Full setup and troubleshooting
2. **FEATURE_CHECKLIST.md** - What's implemented
3. **backend/main.py** - Backend code with comments
4. Browser DevTools (F12) - For frontend errors
5. Backend terminal - For API errors
