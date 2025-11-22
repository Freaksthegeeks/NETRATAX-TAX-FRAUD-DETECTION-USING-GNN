# NETRA TAX - Complete System Architecture & Implementation Guide

## 🎯 System Overview

**NETRA TAX** is a government-grade AI-powered tax fraud detection platform that uses Graph Neural Networks (GNNs) to analyze company relationships, invoice patterns, and detect complex fraud schemes.

### Key Components:

1. **FastAPI Backend** - Modern async Python API
2. **GNN Fraud Detection Engine** - PyTorch-based threat detection
3. **HTML/CSS/JavaScript Frontend** - Responsive web interface
4. **D3.js Graph Visualization** - Interactive network graphs
5. **PDF Report Generation** - Auditor-friendly summaries
6. **PostgreSQL Database** - Scalable data storage

---

## 📁 Project Structure

```
NETRA_TAX/
│
├── backend/                          # FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── core/
│   │   │   ├── config.py            # Configuration management
│   │   │   ├── security.py          # JWT, authentication
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── auth.py              # Login, signup, tokens
│   │   │   ├── fraud.py             # Fraud detection endpoints
│   │   │   ├── files.py             # CSV upload & processing
│   │   │   ├── system.py            # Health, logs, config
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── schemas.py           # Pydantic models
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── upload_service.py   # File processing
│   │   │   └── __init__.py
│   │   ├── fraud/
│   │   │   ├── detection_engine.py # GNN inference
│   │   │   └── __init__.py
│   │   ├── graph/
│   │   │   └── __init__.py
│   │   └── logs/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                         # HTML/CSS/JavaScript UI
│   ├── index.html                   # Dashboard
│   ├── upload.html                  # CSV Upload Center
│   ├── company-explorer.html        # Company Risk Explorer
│   ├── invoice-explorer.html        # Invoice Risk Explorer
│   ├── graph-visualizer.html        # D3.js Network Graph
│   ├── reports.html                 # Report Generation
│   ├── admin.html                   # Admin Panel
│   ├── css/
│   │   ├── style.css               # Main styles
│   │   ├── dashboard.css           # Dashboard styles
│   │   └── theme.css               # Color theme
│   ├── js/
│   │   ├── api.js                  # API client
│   │   ├── dashboard.js            # Dashboard logic
│   │   ├── graph.js                # D3.js graphs
│   │   └── utils.js                # Utilities
│   └── assets/
│       └── (images, fonts, etc)
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md              # System design
│   ├── API_SPEC.md                  # API documentation
│   ├── DEPLOYMENT.md                # Deployment guide
│   ├── SETUP.md                     # Setup instructions
│   └── TROUBLESHOOTING.md           # Common issues
│
└── README.md                         # Project overview

```

---

## 🔌 API Endpoints Summary

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Current user info
- `POST /api/v1/auth/change-password` - Change password

### Fraud Detection
- `GET /api/v1/fraud/company/risk/{gstin}` - Company risk score
- `POST /api/v1/fraud/invoice/risk` - Invoice fraud probability
- `GET /api/v1/fraud/network/analysis/{node_id}` - Network analysis
- `GET /api/v1/fraud/fraud-rings/{node_id}` - Detect fraud rings
- `GET /api/v1/fraud/explain/{node_id}` - Fraud explanation
- `GET /api/v1/fraud/summary` - Fraud summary
- `POST /api/v1/fraud/bulk-analyze` - Batch analysis
- `POST /api/v1/fraud/company/search` - Search companies
- `POST /api/v1/fraud/invoice/search` - Search invoices

### File Upload & Processing
- `POST /api/v1/files/upload` - Upload CSV file
- `POST /api/v1/files/build-graph` - Build knowledge graph
- `POST /api/v1/files/batch-process` - Batch processing
- `GET /api/v1/files/batch-status/{batch_id}` - Batch status
- `GET /api/v1/files/list` - List uploaded files
- `DELETE /api/v1/files/delete/{file_id}` - Delete file

### System & Health
- `GET /api/v1/system/health` - Health check
- `GET /api/v1/system/model-info` - Model information
- `GET /api/v1/system/config` - System configuration
- `GET /api/v1/system/stats` - System statistics
- `GET /api/v1/system/logs` - System logs (admin)
- `POST /api/v1/system/restart` - Restart system (admin)
- `POST /api/v1/system/clear-cache` - Clear cache (admin)

---

## 🔐 Authentication & Authorization

### User Roles:
- **Admin** - Full system access, configuration, monitoring
- **Auditor** - Fraud analysis, report generation, approval
- **GST Officer** - Invoice verification, compliance review
- **Analyst** - Data exploration, pattern analysis
- **Viewer** - Read-only access to dashboards

### JWT Token Flow:
1. User logs in with credentials
2. Server returns `access_token` (short-lived) and `refresh_token` (long-lived)
3. Client includes `Authorization: Bearer <token>` in requests
4. On expiration, client exchanges `refresh_token` for new `access_token`

---

## 🧠 Fraud Detection Engine

### Core Functions:

#### 1. **node_risk(node_id)**
```python
risk_score = engine.node_risk(company_id)
# Returns: RiskScore(score: 0-1, level: LOW|MEDIUM|HIGH, factors: [])
```

#### 2. **invoice_risk(invoice_id)**
```python
fraud_result = engine.invoice_risk(invoice_number)
# Returns: FraudResult(fraud_score: 0-100, risk_level, reasons, patterns)
```

#### 3. **network_analysis(node_id)**
```python
analysis = engine.network_analysis(company_id)
# Returns: Network metrics, patterns, connected entities
```

#### 4. **fraud_explanation(node_id)**
```python
explanation = engine.fraud_explanation(company_id)
# Returns: Detailed explanation with confidence and recommendations
```

### Pattern Detection:
- **Circular Trading** - Detect loops: A→B→C→A
- **High-Degree Nodes** - Identify hub companies
- **Fraud Rings** - Find cliques of suspicious entities
- **Chain Analysis** - Analyze transaction depth
- **Spike Detection** - Identify sudden transaction increases
- **Clustering Anomalies** - Find isolated groups

---

## 📊 Data Flow

```
1. CSV Upload
   ↓
2. Validation & Cleaning
   ↓
3. Graph Building (PyTorch Geometric)
   ↓
4. GNN Inference
   ↓
5. Pattern Detection
   ↓
6. Risk Scoring
   ↓
7. Report Generation
   ↓
8. Frontend Visualization
```

---

## 🚀 Deployment

### Development:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Production:
```bash
# Using Gunicorn + Uvicorn workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t netra-tax-api .
docker run -p 8000:8000 netra-tax-api
```

### Environment Variables:
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/netra_tax
DEVICE=cuda  # or cpu
GRAPH_DATA_PATH=/models/graph_data.pt
MODEL_PATH=/models/gnn_model.pt
```

---

## 📈 Performance & Scalability

### Optimization Strategies:
1. **Batch Processing** - Process multiple entities concurrently
2. **Caching** - Cache model outputs and network analysis
3. **Database Indexing** - Optimize queries
4. **Async Operations** - Non-blocking I/O
5. **Model Quantization** - Reduce model size
6. **Horizontal Scaling** - Multiple API instances behind load balancer

### Expected Performance:
- **API Response Time**: <500ms per request
- **Fraud Ring Detection**: <2s for 1000-node network
- **Batch Analysis**: 10,000 entities/minute
- **Concurrent Users**: 100+ with proper infrastructure

---

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Coverage
pytest --cov=app tests/

# Load testing
locust -f locustfile.py

# Integration tests
pytest tests/integration/
```

---

## 📝 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    full_name VARCHAR(100),
    hashed_password VARCHAR(255),
    role VARCHAR(20),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Uploads Table
```sql
CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    filename VARCHAR(255),
    file_type VARCHAR(20),
    file_size INT,
    data_hash VARCHAR(64),
    status VARCHAR(20),
    created_at TIMESTAMP
);
```

### Companies Table
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    gstin VARCHAR(15) UNIQUE,
    name VARCHAR(255),
    director_name VARCHAR(255),
    location VARCHAR(100),
    fraud_score FLOAT,
    risk_level VARCHAR(10),
    transaction_count INT,
    created_at TIMESTAMP
);
```

### Invoices Table
```sql
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE,
    supplier_gstin VARCHAR(15),
    buyer_gstin VARCHAR(15),
    amount DECIMAL(15,2),
    cgst DECIMAL(10,2),
    sgst DECIMAL(10,2),
    igst DECIMAL(10,2),
    itc_claimed DECIMAL(10,2),
    fraud_score FLOAT,
    risk_level VARCHAR(10),
    created_at TIMESTAMP
);
```

---

## 🔒 Security Best Practices

1. **JWT Expiration** - Access tokens: 30 min, Refresh: 7 days
2. **Password Hashing** - bcrypt with 12 rounds
3. **HTTPS Only** - Enforce SSL/TLS
4. **CORS** - Restrict to known origins
5. **Rate Limiting** - Prevent brute force attacks
6. **Input Validation** - Pydantic models enforce schema
7. **SQL Injection Prevention** - SQLAlchemy ORM
8. **Audit Logging** - Track all user actions
9. **Role-Based Access** - Granular permissions
10. **Environment Variables** - No hardcoded secrets

---

## 📞 Support & Troubleshooting

### Common Issues:

**Q: Model not loading**
- Check `MODEL_PATH` environment variable
- Verify file exists and is readable
- Check PyTorch version compatibility

**Q: Graph building fails**
- Verify CSV format (required columns)
- Check for duplicate GSTINs
- Ensure sufficient disk space

**Q: Slow API responses**
- Enable caching
- Check database indices
- Monitor system resources

See `TROUBLESHOOTING.md` for more solutions.

---

## 📜 License

Proprietary - Government of India Project

---

## 👥 Authors

- NETRA TAX Development Team
- Built for Indian Tax Administration

---

## 🔄 Version History

- **v1.0.0** (2024-Nov) - Initial release with complete fraud detection suite
  - GNN-based detection engine
  - CSV upload and processing
  - Interactive dashboards
  - PDF report generation
  - Role-based access control
