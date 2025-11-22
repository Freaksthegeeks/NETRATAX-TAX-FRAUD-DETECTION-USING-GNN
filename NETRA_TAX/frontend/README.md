# NETRA TAX Frontend - User Guide & Setup

## Overview

NETRA TAX Frontend is a modern, responsive web application built with vanilla HTML5, CSS3, and JavaScript. It provides an intuitive interface for tax fraud detection and network analysis.

## 📁 Project Structure

```
frontend/
├── index.html                    # Main dashboard page
├── login.html                    # Authentication page
├── upload.html                   # CSV file upload center
├── company-explorer.html         # Company search and analysis
├── invoice-explorer.html         # Invoice search and analysis
├── graph-visualizer.html         # Network visualization with D3.js
├── reports.html                  # PDF report generation & management
├── admin.html                    # Administration & system settings
├── css/
│   └── style.css                 # Global stylesheet (1000+ lines)
└── js/
    ├── api.js                    # API client & utility functions
    └── dashboard.js              # Dashboard-specific logic
```

## 🎨 Design System

### Color Palette
- **Primary**: #114C5A (Arctic Powder) - Main theme color
- **Secondary**: #FFC801 (Forsythia) - Accent/CTA buttons
- **Accent**: #FF9932 (Deep Saffron) - Highlights
- **Danger**: #e74c3c - Errors/Warnings
- **Success**: #27ae60 - Confirmations
- **Info**: #3498db - Information

### Typography
- **Font Family**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Sizes**: 12px (labels) → 28px (headers)
- **Weight**: 400 (regular) → 700 (bold)

### Spacing System
- `--spacing-xs`: 4px
- `--spacing-sm`: 8px
- `--spacing-md`: 16px
- `--spacing-lg`: 24px
- `--spacing-xl`: 32px
- `--spacing-2xl`: 48px

### Border Radius
- Small: 4px
- Medium: 8px
- Large: 12px
- XL: 16px

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- FastAPI backend running on `http://localhost:8000`
- Internet connection for D3.js and Plotly CDNs

### Setup Instructions

1. **Start the Backend Server**
   ```powershell
   cd NETRA_TAX\backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Serve Frontend Files**
   - Option A: Use Python's built-in server
     ```powershell
     cd NETRA_TAX\frontend
     python -m http.server 8080
     ```
   
   - Option B: Use Live Server (VS Code Extension)
     - Install "Live Server" extension
     - Right-click on `index.html` → "Open with Live Server"

3. **Open in Browser**
   - Navigate to `http://localhost:8080/index.html` or `http://localhost:8080/login.html`

## 📄 Page Documentation

### Login Page (`login.html`)
**Purpose**: User authentication with role-based access

**Features**:
- Dual-form interface (Sign In / Create Account)
- Form validation (email, password strength)
- Remember me functionality
- Role selection (Admin, Auditor, Analyst)
- Terms of Service agreement

**API Endpoints Used**:
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/signup` - Register new account

**Key Functions**:
- `switchForm(formType)` - Toggle between login/signup
- `showError(message)` - Display error alerts
- Form submission handlers

### Dashboard (`index.html`)
**Purpose**: Real-time fraud detection overview and analytics

**Features**:
- 4 metric cards with KPIs
- Risk distribution pie chart
- Fraud score distribution bar chart
- 12-month trend line chart
- System health indicator
- Recent alerts section
- High-risk companies table
- Auto-refresh every 30 seconds

**API Endpoints Used**:
- `GET /api/fraud/summary` - Overall fraud statistics
- `GET /api/system/health` - System status
- `GET /api/fraud/bulk-analyze` - Company analysis

**Key Functions**:
- `loadFraudSummary()` - Fetch and display KPIs
- `renderRiskDistributionChart(summary)` - Canvas-based pie chart
- `loadHighRiskCompanies()` - Populate risk table
- `setupEventListeners()` - Attach event handlers

### Upload Center (`upload.html`)
**Purpose**: CSV file import and graph building

**Features**:
- Drag-and-drop file upload
- File validation (CSV, <100MB)
- Upload progress bar
- Data quality metrics
- Recent uploads table
- Template download
- Graph building workflow

**API Endpoints Used**:
- `POST /api/files/upload` - Upload CSV
- `POST /api/files/build-graph` - Create knowledge graph
- `GET /api/files/list` - List uploaded files
- `DELETE /api/files/delete/{file_id}` - Remove file

**Key Functions**:
- `setupDragDrop()` - Initialize drag-drop zone
- `selectFile(file)` - Validate and select file
- XMLHttpRequest for progress tracking
- `showValidationResults(response)` - Display quality metrics

### Company Explorer (`company-explorer.html`)
**Purpose**: Search and analyze company fraud profiles

**Features**:
- Full-text search by GSTIN or name
- Dynamic filtering (risk level, fraud rings)
- Pagination (20 results per page)
- Detailed company modal with tabs:
  - Overview: Network metrics and risk factors
  - Analysis: GNN risk score and anomalies
  - Invoices: Associated transactions
- Generate and download reports

**API Endpoints Used**:
- `POST /api/fraud/search/companies` - Search companies
- `GET /api/fraud/company/risk/{gstin}` - Company risk score
- `GET /api/fraud/network/analysis/{node_id}` - Network details
- `POST /api/reports/generate` - Create PDF report

**Key Functions**:
- `performSearch()` - Execute company search
- `displayResults()` - Render paginated results
- `viewCompanyDetails(gstin)` - Open detail modal
- `switchTab(tabName)` - Navigate modal tabs

### Invoice Explorer (`invoice-explorer.html`)
**Purpose**: Search and review transactions for fraud indicators

**Features**:
- Multi-filter search (GSTIN, date range, amount)
- Risk level color-coding
- Invoice detail modal showing:
  - Party details (supplier/recipient)
  - Amount and GST
  - Risk assessment score
  - Fraud risk indicators
- Flag invoices for review

**API Endpoints Used**:
- `POST /api/fraud/search/invoices` - Search invoices
- `POST /api/fraud/invoice/risk` - Analyze invoice

**Key Functions**:
- `performSearch()` - Execute invoice query
- `viewInvoiceDetails(invoiceId)` - Show invoice modal
- `flagInvoice()` - Mark for auditor review

### Graph Visualizer (`graph-visualizer.html`)
**Purpose**: Visualize fraud networks and connections using D3.js

**Features**:
- Force-directed graph simulation
- Interactive node dragging
- Color-coded nodes by risk level
- Fraud ring link highlighting
- Tooltip information on hover
- Zoom and pan controls
- Legend and graph statistics
- Download graph as PNG
- Center graph on specific entity

**Libraries**:
- D3.js v7 (from CDN)

**API Endpoints Used**:
- `GET /api/fraud/network/analysis/{node_id}` - Load network

**Key Functions**:
- `renderGraph()` - Initialize D3 visualization
- `drag(simulation)` - Node dragging behavior
- `selectNode(node)` - Show node info panel
- `updateSimulation()` - Adjust force parameters
- `downloadGraph()` - Export as PNG

**Graph Features**:
- Node size: Larger for center node
- Node color: Red (high), Orange (medium), Green (low)
- Link color: Dark red for fraud rings, gray for normal
- Link thickness: Proportional to transaction amount

### Reports (`reports.html`)
**Purpose**: Generate, manage, and distribute fraud analysis reports

**Features**:
- 3 report templates:
  - **Comprehensive** (20-30 pages): Full analysis
  - **Executive Summary** (3-5 pages): High-level overview
  - **Network Analysis** (10-15 pages): Fraud rings deep-dive
- Report generation form
- Download/view/delete reports
- Search and filter recent reports
- Report metadata tracking

**API Endpoints Used**:
- `POST /api/reports/generate` - Create report
- `GET /api/reports/download/{report_id}` - Download PDF
- `GET /api/reports/list` - List user's reports

**Key Functions**:
- `openGenerateReportModal()` - Show report generator
- `submitGenerateReport(e)` - Create report
- `downloadReport(reportId)` - Download PDF
- `filterReports()` - Search reports

### Admin Panel (`admin.html`)
**Purpose**: System configuration and user management (admin only)

**Features**:
- **System Tab**: Health status, performance metrics, backups
- **Users Tab**: User CRUD, role management, password reset
- **Logs Tab**: System event logs with filtering
- **Settings Tab**: Fraud thresholds, email configuration

**API Endpoints Used**:
- `GET /api/system/health` - System status
- `GET /api/system/stats` - Performance metrics
- `GET /api/system/logs` - System logs
- `GET /api/system/config` - Configuration (admin only)

**Restricted To**: Admin role only

## 🔐 Authentication & Security

### Token Management
```javascript
// Store tokens after login
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// Load from storage
const token = localStorage.getItem('access_token');
```

### API Authentication
All requests include JWT bearer token:
```javascript
headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
}
```

### Auto-Refresh
- Tokens automatically refresh when expired (401 response)
- Failed refresh redirects to login page
- `requireAuth()` function enforces authentication

## 🛠️ API Client (`js/api.js`)

### Class: APIClient

```javascript
const api = new APIClient('http://localhost:8000/api');

// Authentication
api.login(username, password)
api.signup(username, email, password, full_name, role)
api.getCurrentUser()
api.logout()

// Fraud Detection
api.getCompanyRisk(gstin)
api.analyzeInvoice(invoice_data)
api.getNetworkAnalysis(node_id)
api.getFraudRings(node_id)
api.explainFraudPrediction(node_id)
api.getFraudSummary()
api.bulkAnalyze(company_list)
api.searchCompanies(query, skip, limit)
api.searchInvoices(query, skip, limit)

// File Management
api.uploadCSV(file)
api.buildGraph(upload_id)
api.listUploads(skip, limit)
api.deleteFile(file_id)
api.batchProcess(upload_id)

// System
api.getHealth()
api.getModelInfo()
api.getConfig()
api.getStats()
api.getLogs(skip, limit)

// Reports
api.generateReport(company_id, report_type)
api.downloadReport(report_id)
```

### Utility Functions

```javascript
// Formatting
formatNumber(num) → "1,234"
formatCurrency(amount) → "₹ 1,234.00"
formatDate(dateString) → "15 Jan 2024"
formatTimeAgo(dateString) → "2 hours ago"

// Validation
validateGSTIN(gstin) → boolean
validateEmail(email) → boolean

// UI
showNotification(message, type, duration)
showSpinner(container)
hideSpinner()
getRiskLevelBadge(riskScore) → {level, color, icon}

// Auth
isAuthenticated() → boolean
requireAuth() → redirect if needed
getCurrentUser() → user object
setCurrentUser(user)
logoutUser()
```

## 📊 Canvas Charts

Dashboard uses native HTML5 Canvas for performance:

### Pie Chart (Risk Distribution)
- Center-aligned chart
- 3 colored slices (high, medium, low)
- Legend with counts
- Responsive sizing

### Bar Chart (Fraud Score Distribution)
- 5 score ranges (0-0.2, 0.2-0.4, etc.)
- Color-coded bars
- Labeled axes
- Grid background

### Line Chart (Trends)
- 12-month data points
- Smooth line connection
- Point markers
- Legend/labels

## 🎯 Responsive Design

### Breakpoints
```css
@media (max-width: 1024px) {
    /* Tablet layout */
}

@media (max-width: 768px) {
    /* Mobile layout */
    - Single column layouts
    - Collapsed sidebars
    - Hamburger menu
}

@media (max-width: 480px) {
    /* Small mobile layout */
    - Minimal padding
    - Stack elements vertically
    - Hide non-essential content
}
```

### Mobile Features
- Responsive grid system
- Touch-friendly buttons (48px minimum)
- Flexible navigation
- Full-width tables with horizontal scroll

## 🚨 Error Handling

### HTTP Errors
```javascript
// APIClient handles:
// - 401 (Unauthorized) → Auto-refresh token
// - 4xx (Client) → Show error message
// - 5xx (Server) → Show error message
```

### User Feedback
- Toast notifications (success, error, warning, info)
- Modal confirmation dialogs
- Inline form validation
- Loading spinners

## 📦 Dependencies

### External Libraries (via CDN)
- **D3.js v7**: Graph visualization
- **Plotly.js**: Interactive charts
- **Font Awesome 6.4**: Icons (in original)

### No Build Tools Required
- Pure HTML/CSS/JavaScript
- Works in any modern browser
- No npm/webpack setup needed

## 🔧 Development

### Making Changes
1. Edit HTML/CSS/JS files directly
2. Save and refresh browser
3. Use browser DevTools (F12) for debugging

### Testing Authentication
```javascript
// In console:
localStorage.setItem('access_token', 'test_token');
localStorage.setItem('current_user', JSON.stringify({
    username: 'admin',
    role: 'admin'
}));
```

### Debugging API Calls
```javascript
// All API calls log to console
api.searchCompanies('18AABCT1234H1Z0')
// Check Network tab in DevTools
```

## 📝 Best Practices

1. **Always call `requireAuth()` on page load**
2. **Handle API errors with `showNotification()`**
3. **Use `showSpinner()` during data loading**
4. **Format numbers/dates for display**
5. **Validate user input before sending**
6. **Keep functions under 30 lines**
7. **Use semantic HTML elements**
8. **Test on mobile devices**

## 🆘 Troubleshooting

### "API is not responding"
- Check backend is running: `http://localhost:8000/api/system/health`
- Verify CORS settings in `main.py`
- Check browser console for errors

### "Login page redirects to itself"
- Clear localStorage: `localStorage.clear()`
- Check token in DevTools → Application → Local Storage

### "Charts not rendering"
- Verify Canvas elements exist in HTML
- Check browser console for JavaScript errors
- Ensure data is loading from API

### "Styles not loading"
- Clear browser cache (Ctrl+Shift+Delete)
- Check CSS file path is correct
- Verify server is serving static files

## 📞 Support

For issues or questions:
1. Check browser console (F12 → Console)
2. Inspect Network tab for API errors
3. Review this documentation
4. Check backend logs for server-side errors

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Status**: Production Ready ✅
