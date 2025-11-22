# Quick Start Guide - NETRA TAX

## ⚡ 5-Minute Setup

### Prerequisites
- Python 3.9+
- Node.js 16+ (optional, for frontend development)
- PostgreSQL 12+ (for production)

### Step 1: Clone Repository
```bash
cd C:\BIG HACK\NETRA_TAX\backend
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
Create `.env` file:
```bash
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-dev-secret-key-change-in-production
DATABASE_URL=sqlite:///./netra_tax.db
DEVICE=cpu
```

### Step 5: Initialize Database
```bash
# First time setup
python -c "from app.core.config import settings; from pathlib import Path; Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)"
```

### Step 6: Run Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Access Application
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/v1/system/health

---

## 🧪 Testing the API

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Health Status
```bash
curl "http://localhost:8000/api/v1/system/health"
```

### Upload CSV
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@invoices.csv" \
  -F "file_type=invoice"
```

### Get Company Risk
```bash
curl -X GET "http://localhost:8000/api/v1/fraud/company/risk/27AABCT1234H1Z0" \
  -H "Authorization: Bearer <your-token>"
```

---

## 📦 Database Setup (Production)

### PostgreSQL Installation
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows - Download from postgresql.org
# macOS
brew install postgresql
```

### Create Database
```bash
psql -U postgres

CREATE DATABASE netra_tax;
CREATE USER netra_user WITH PASSWORD 'secure_password';
ALTER ROLE netra_user SET client_encoding TO 'utf8';
ALTER ROLE netra_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE netra_user SET default_transaction_devel TO ON;
GRANT ALL PRIVILEGES ON DATABASE netra_tax TO netra_user;
\q
```

### Update .env
```bash
DATABASE_URL=postgresql://netra_user:secure_password@localhost/netra_tax
```

### Run Migrations
```bash
alembic upgrade head
```

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t netra-tax-api .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db/netra_tax \
  -e SECRET_KEY=your-secret \
  netra-tax-api
```

### Docker Compose (with PostgreSQL)
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: netra_tax
      POSTGRES_USER: netra_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://netra_user:secure_password@db/netra_tax
      DEBUG: "false"
    depends_on:
      - db

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

---

## 📊 Load Testing

### Install Locust
```bash
pip install locust
```

### Create locustfile.py
```python
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login first
        response = self.client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        self.token = response.json()["access_token"]
    
    @task(1)
    def health_check(self):
        self.client.get("/api/v1/system/health")
    
    @task(2)
    def get_company_risk(self):
        self.client.get(
            "/api/v1/fraud/company/risk/27AABCT1234H1Z0",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

### Run Load Test
```bash
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089
```

---

## 🔍 Monitoring & Logging

### Check Logs
```bash
tail -f logs/netra_tax.log
```

### System Health
```bash
curl http://localhost:8000/api/v1/system/health
```

### Monitor Resources
```bash
# CPU and Memory
watch -n 1 'ps aux | grep python'

# Database connections
psql -U netra_user -d netra_tax -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

---

## 🚀 Production Checklist

- [ ] Set `DEBUG=false` in environment
- [ ] Use strong `SECRET_KEY`
- [ ] Configure PostgreSQL with backups
- [ ] Setup HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Setup log rotation
- [ ] Configure monitoring (Prometheus, DataDog, etc.)
- [ ] Setup alerts for high-risk detections
- [ ] Configure email for notifications
- [ ] Implement rate limiting
- [ ] Setup CI/CD pipeline
- [ ] Document API for team
- [ ] Train users on platform

---

## 📞 Support

For issues or questions:
1. Check `TROUBLESHOOTING.md`
2. Review API documentation at `/api/docs`
3. Check logs in `logs/netra_tax.log`
4. Contact development team

---

## 🎯 Next Steps

1. ✅ Upload CSV files (invoices + companies)
2. ✅ Build knowledge graph
3. ✅ Run fraud detection
4. ✅ Generate reports
5. ✅ Explore dashboards
6. ✅ Configure alerts

---

**NETRA TAX v1.0.0** | Government-Grade Tax Fraud Detection
