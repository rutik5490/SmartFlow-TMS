# Quick Start Guide

## 3-Step Setup

### Step 1: Start All Services
```bash
docker-compose up --build
```

Wait 30 seconds for all services to initialize.

### Step 2: Verify Backend
Open browser: http://localhost:8000/docs

You should see the Swagger UI with all API endpoints.

### Step 3: Open Frontend
Double-click: `traffic_management_system.html`

---

## Windows Users

Just run:
```bash
start.bat
```

---

## First-Time Setup (Optional)

### Train ML Models
```bash
cd spark
python ml_training.py
```

### Initialize Kafka Topics
```bash
docker-compose exec kafka bash
./kafka/init-topics.sh
```

---

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Sensors only
docker-compose logs -f sensors
```

### Restart Services
```bash
docker-compose restart backend
docker-compose restart sensors
```

### Stop Everything
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d
```

---

## Testing the System

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

### 2. Get Junction Data
```bash
curl http://localhost:8000/api/intersections
```

### 3. Change Signal
```bash
curl -X PUT http://localhost:8000/api/signals/1/state \
  -H "Content-Type: application/json" \
  -d '{"state": "Red"}'
```

### 4. View Sensor Logs
```bash
docker-compose logs -f sensors
```

---

## Troubleshooting

### Backend won't start
```bash
docker-compose logs backend
docker-compose restart postgres
docker-compose restart backend
```

### Sensors not connecting to Kafka
```bash
docker-compose logs kafka
docker-compose restart kafka
docker-compose restart sensors
```

### Database connection failed
```bash
docker-compose exec postgres psql -U smartflow -d traffic_system -c "\dt"
```

### Port already in use
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

---

## System Architecture

```
Frontend (HTML) 
    ↓
FastAPI (Port 8000)
    ↓
PostgreSQL (Port 5432) ←→ Redis (Port 6379)
    ↑
Kafka (Port 9092)
    ↑
Sensors (Python scripts)
```

---

## Next Steps

1. Explore API documentation at http://localhost:8000/docs
2. Try different endpoints
3. Modify sensor data in `sensors/traffic_sensor.py`
4. Train custom ML models in `spark/ml_training.py`
5. Customize frontend dashboard

---

For full documentation, see README.md
