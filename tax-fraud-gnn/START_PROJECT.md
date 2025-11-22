# 🚀 Complete Project Startup Guide

## Quick Start - Run Everything

### Option 1: Development Mode (React + Flask)

**Step 1: Install Node.js Dependencies**
```powershell
cd tax-fraud-gnn\frontend
npm install
```

**Step 2: Start Flask Backend (Terminal 1)**
```powershell
cd tax-fraud-gnn
python app.py
```

**Step 3: Start React Dev Server (Terminal 2)**
```powershell
cd tax-fraud-gnn\frontend
npm run dev
```

**Access:**
- React Frontend: http://localhost:3000 (with animations & color palette)
- Flask API: http://localhost:5000

---

### Option 2: Production Mode (Flask Serves React Build)

**Step 1: Build React App**
```powershell
cd tax-fraud-gnn\frontend
npm install
npm run build
```

**Step 2: Start Flask (Serves React Build)**
```powershell
cd tax-fraud-gnn
python app.py
```

**Access:**
- Full App: http://localhost:5000 (React app served by Flask)

---

### Option 3: Traditional Mode (HTML Templates - Fallback)

If React isn't set up, Flask will automatically fall back to HTML templates:
```powershell
cd tax-fraud-gnn
python app.py
```

**Access:**
- App: http://localhost:5000

---

## 🔧 Setup Checklist

### Prerequisites
- [x] Python 3.9+ installed
- [ ] Node.js 16+ installed (for React)
- [ ] npm installed (comes with Node.js)

### Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Install Node.js Dependencies (for React)
```powershell
cd frontend
npm install
```

---

## 📋 What's Integrated

### ✅ React Frontend
- Modern UI with animations
- Custom color palette
- Interactive charts
- Responsive design

### ✅ Flask Backend
- REST API endpoints
- Serves React build in production
- Falls back to HTML templates
- CORS enabled for development

### ✅ Features
- Dashboard with metrics
- Company search & filtering
- Analytics & network insights
- Real-time fraud detection

---

## 🐛 Troubleshooting

### npm not found
1. Install Node.js from https://nodejs.org/
2. Restart terminal/PowerShell
3. Verify: `node --version` and `npm --version`

### Port 5000 already in use
```powershell
# Find process using port 5000
Get-NetTCPConnection -LocalPort 5000

# Kill it
Stop-Process -Id <PID> -Force
```

### Port 3000 already in use
Edit `frontend/vite.config.js` and change port:
```js
server: { port: 3001 }
```

### Module not found errors
```powershell
# Reinstall Python packages
pip install -r requirements.txt

# Reinstall Node packages
cd frontend
rm -rf node_modules
npm install
```

---

## 🎯 Recommended: Development Mode

For the best experience with hot-reload and animations:

1. **Terminal 1:**
   ```powershell
   cd tax-fraud-gnn
   python app.py
   ```

2. **Terminal 2:**
   ```powershell
   cd tax-fraud-gnn\frontend
   npm run dev
   ```

3. **Open:** http://localhost:3000

Enjoy your beautiful, animated dashboard! 🎉

