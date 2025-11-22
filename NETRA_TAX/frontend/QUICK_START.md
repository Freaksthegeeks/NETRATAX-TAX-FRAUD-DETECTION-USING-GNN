# NETRA TAX Frontend - Quick Start Guide

## 5-Minute Setup

### Step 1: Start Backend
```powershell
cd NETRA_TAX\backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start Frontend Server
```powershell
cd NETRA_TAX\frontend
python -m http.server 8080
```

### Step 3: Open Browser
Navigate to: **`http://localhost:8080/login.html`**

---

## Default Credentials

```
Username: admin
Password: admin123
Role: Administrator
```

Or create a new account during signup.

---

## Page Navigation

### Dashboard (`/index.html`)
- **KPIs**: Total entities, high-risk count, medium-risk count, fraud rings
- **Charts**: Risk distribution, fraud scores, 12-month trends
- **Alerts**: Recent high-priority notifications
- **Table**: High-risk companies with details

### Upload (`/upload.html`)
- Drag-and-drop CSV files
- Download template
- View validation results
- Build knowledge graph

### Company Explorer (`/company-explorer.html`)
- Search by GSTIN or name
- Filter by risk level
- View company details
- Generate PDF reports
- View network analysis

### Invoice Explorer (`/invoice-explorer.html`)
- Search invoices by ID, GSTIN
- Filter by amount, date, risk
- View invoice details
- Flag for review

### Network Graph (`/graph-visualizer.html`)
- Interactive D3.js visualization
- Center on specific entity
- Drag nodes to rearrange
- Download as PNG
- View fraud rings in red

### Reports (`/reports.html`)
- 3 template types
- Generate new reports
- Download PDFs
- Search existing reports

### Admin (`/admin.html`)
- System health monitoring
- User management
- System logs
- Configuration settings

---

## Common Tasks

### Search for a Company
1. Go to **Company Explorer**
2. Enter GSTIN (e.g., `18AABCT1234H1Z0`)
3. Click **Search**
4. Click **View** to see details
5. Click **Network** to visualize connections

### Analyze an Invoice
1. Go to **Invoice Explorer**
2. Enter invoice ID or GSTIN
3. Click **Search**
4. Click **View** to see details
5. Click **Flag for Review** if needed

### Generate a Report
1. Go to **Reports**
2. Click **Generate New Report**
3. Select template type:
   - **Comprehensive**: Full 20-30 page analysis
   - **Executive Summary**: Quick 3-5 page overview
   - **Network Analysis**: Fraud ring deep-dive
4. Enter GSTIN
5. Check desired sections
6. Click **Generate**
7. Download when ready

### Upload Company Data
1. Go to **Upload Center**
2. Download CSV template
3. Fill with your data
4. Drag-drop the file
5. Review validation results
6. Click **Process & Build Graph**

### View Network Visualization
1. Go to **Network Graph**
2. Enter a GSTIN in the search box
3. Click **Load**
4. Interact:
   - **Drag nodes** to rearrange
   - **Scroll to zoom**
   - **Click nodes** for details
   - **Check "Highlight Fraud Rings"** to see suspicious links

---

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/signup` - Register
- `GET /api/auth/me` - Current user
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token

### Fraud Detection
- `GET /api/fraud/company/risk/{gstin}` - Company risk
- `POST /api/fraud/invoice/risk` - Invoice risk
- `GET /api/fraud/network/analysis/{node_id}` - Network details
- `GET /api/fraud/fraud-rings/{node_id}` - Fraud cliques
- `GET /api/fraud/summary` - Overall summary
- `POST /api/fraud/search/companies` - Search companies
- `POST /api/fraud/search/invoices` - Search invoices

### Files
- `POST /api/files/upload` - Upload CSV
- `POST /api/files/build-graph` - Build graph
- `GET /api/files/list` - List uploads
- `DELETE /api/files/delete/{file_id}` - Delete

### Reports
- `POST /api/reports/generate` - Create report
- `GET /api/reports/download/{report_id}` - Download PDF
- `GET /api/reports/list` - List reports

### System
- `GET /api/system/health` - Health check
- `GET /api/system/stats` - Statistics
- `GET /api/system/logs` - System logs
- `GET /api/system/config` - Configuration (admin)

---

## File Structure

```
NETRA_TAX/
├── frontend/
│   ├── index.html                # Dashboard
│   ├── login.html                # Auth
│   ├── upload.html               # File upload
│   ├── company-explorer.html     # Company search
│   ├── invoice-explorer.html     # Invoice search
│   ├── graph-visualizer.html     # D3.js network
│   ├── reports.html              # Report management
│   ├── admin.html                # Admin panel
│   ├── css/
│   │   └── style.css             # Main stylesheet
│   ├── js/
│   │   ├── api.js                # API client
│   │   └── dashboard.js          # Dashboard JS
│   └── README.md                 # Full documentation
│
└── backend/
    ├── app/
    │   ├── main.py               # FastAPI app
    │   ├── core/
    │   │   ├── config.py         # Settings
    │   │   └── security.py       # Auth & JWT
    │   ├── routers/
    │   │   ├── auth.py           # Auth endpoints
    │   │   ├── fraud.py          # Fraud detection
    │   │   ├── files.py          # File upload
    │   │   └── system.py         # System endpoints
    │   ├── services/
    │   │   └── upload_service.py # CSV processing
    │   ├── fraud/
    │   │   └── detection_engine.py # GNN inference
    │   ├── models/
    │   │   └── schemas.py        # Pydantic models
    │   └── __init__.py
    ├── requirements.txt          # Dependencies
    └── README.md                 # Backend docs
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F12` | Open DevTools |
| `Ctrl+Shift+Delete` | Clear browser cache |
| `Ctrl+L` | Focus address bar |
| `Cmd+Option+I` (Mac) | Open DevTools |

---

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome 90+ | ✅ Full |
| Firefox 88+ | ✅ Full |
| Safari 14+ | ✅ Full |
| Edge 90+ | ✅ Full |
| IE 11 | ❌ Not supported |

---

## Performance Tips

1. **Disable auto-refresh** on Dashboard (if not needed) to save API calls
2. **Close unused modal dialogs** to free memory
3. **Use search filters** instead of loading all data
4. **Download large reports** in off-peak hours
5. **Clear browser cache** weekly

---

## Troubleshooting

### "Blank white page"
→ Check browser console (F12), look for JavaScript errors

### "API connection failed"
→ Verify backend is running: `http://localhost:8000/api/system/health`

### "Login says invalid credentials"
→ Use default credentials: `admin` / `admin123`

### "Styles look broken"
→ Hard refresh browser (Ctrl+Shift+R)

### "Graphs not displaying"
→ Check Canvas is supported in your browser

---

## Support & Resources

- **Documentation**: `/frontend/README.md`
- **Backend API**: `http://localhost:8000/docs` (Swagger UI)
- **Backend Schema**: `http://localhost:8000/redoc` (ReDoc)

---

## Next Steps

1. ✅ Login successfully
2. ✅ Upload sample CSV data
3. ✅ Search for a company
4. ✅ View network visualization
5. ✅ Generate a report
6. ✅ Check admin settings

**Congratulations!** 🎉 You're ready to detect fraud.

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Status**: Production Ready ✅
