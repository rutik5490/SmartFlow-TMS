from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/active")
def get_active_vehicles(db: Session = Depends(get_db)):
    """Get count of active vehicles being tracked"""
    # Vehicles with position updates in last 5 minutes
    five_min_ago = datetime.now() - timedelta(minutes=5)
    
    active_count = db.query(models.VehiclePosition).filter(
        models.VehiclePosition.timestamp >= five_min_ago
    ).distinct(models.VehiclePosition.vehicle_id).count()
    
    return {
        "active_vehicles": active_count,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/{vehicle_id}/track")
def track_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Get vehicle trajectory (last 10 positions)"""
    positions = db.query(models.VehiclePosition).filter(
        models.VehiclePosition.vehicle_id == vehicle_id
    ).order_by(models.VehiclePosition.timestamp.desc()).limit(10).all()
    
    if not positions:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return positions[::-1]  # Reverse to chronological order

@router.get("/congestion-map")
def get_congestion_heatmap(db: Session = Depends(get_db)):
    """Get heatmap data for congestion visualization"""
    junctions = db.query(models.Junction).all()
    
    heatmap_data = []
    for junction in junctions:
        latest = db.query(models.SensorReading).filter(
            models.SensorReading.junction_id == junction.id
        ).order_by(models.SensorReading.timestamp.desc()).first()
        
        if latest:
            heatmap_data.append({
                "junction_id": junction.id,
                "name": junction.name,
                "latitude": junction.latitude,
                "longitude": junction.longitude,
                "congestion_level": latest.congestion_level,
                "density": latest.density,
                "vehicle_count": latest.vehicle_count,
                "intensity": latest.density / 100.0  # 0.0 to 1.0
            })
    
    return heatmap_data

@router.get("/clusters")
def detect_congestion_clusters(db: Session = Depends(get_db)):
    """Detect vehicle clusters indicating traffic jams"""
    five_min_ago = datetime.now() - timedelta(minutes=5)
    
    # Get recent vehicle positions
    recent_positions = db.query(models.VehiclePosition).filter(
        models.VehiclePosition.timestamp >= five_min_ago
    ).all()
    
    # Simple clustering: group vehicles at same junction with low speed
    clusters = {}
    for pos in recent_positions:
        if pos.speed and pos.speed < 10:  # Slow vehicles
            key = f"junction_{int(pos.latitude * 1000)}_{int(pos.longitude * 1000)}"
            if key not in clusters:
                clusters[key] = {"vehicles": [], "avg_speed": 0}
            clusters[key]["vehicles"].append(pos.vehicle_id)
            clusters[key]["location"] = {"lat": pos.latitude, "lng": pos.longitude}
    
    # Calculate average speed per cluster
    for key in clusters:
        vehicle_ids = clusters[key]["vehicles"]
        speeds = [p.speed for p in recent_positions if p.vehicle_id in vehicle_ids and p.speed]
        clusters[key]["avg_speed"] = sum(speeds) / len(speeds) if speeds else 0
        clusters[key]["vehicle_count"] = len(vehicle_ids)
    
    # Return clusters with more than 5 vehicles
    significant_clusters = {
        k: v for k, v in clusters.items() if v["vehicle_count"] > 5
    }
    
    return significant_clusters
