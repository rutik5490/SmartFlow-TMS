from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import (
    intersections,
    alerts,
    signals,
    predictions,
    routes,
    vehicles,
    analytics,
    websocket,
    environment
)
from datetime import datetime

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartFlow TMS API",
    description="Real-Time Traffic Management System Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(intersections.router, prefix="/api/intersections", tags=["Intersections"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(routes.router, prefix="/api/routes", tags=["Routes"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(environment.router, prefix="/api/environment", tags=["Environment"])
app.include_router(websocket.router, tags=["WebSocket"])

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "SmartFlow TMS API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "kafka": "running",
            "redis": "running"
        }
    }

@app.get("/api/stats")
def get_system_stats():
    """Get overall system statistics"""
    return {
        "total_endpoints": 25,
        "active_services": [
            "Traffic Monitoring",
            "Signal Control",
            "Alert System",
            "Route Optimization",
            "ML Predictions",
            "Vehicle Tracking",
            "Analytics",
            "Environmental Impact"
        ],
        "timestamp": datetime.now().isoformat()
    }
