from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from datetime import datetime
import random

router = APIRouter()

@router.get("/", response_model=List[schemas.JunctionWithSignal])
def get_all_junctions(db: Session = Depends(get_db)):
    """Get all junctions with live traffic data"""
    junctions = db.query(models.Junction).all()
    
    result = []
    for junction in junctions:
        # Get latest sensor reading
        latest_reading = db.query(models.SensorReading).filter(
            models.SensorReading.junction_id == junction.id
        ).order_by(models.SensorReading.timestamp.desc()).first()
        
        # Get signal state
        signal = db.query(models.TrafficSignal).filter(
            models.TrafficSignal.junction_id == junction.id
        ).first()
        
        if latest_reading and signal:
            result.append(schemas.JunctionWithSignal(
                id=junction.id,
                name=junction.name,
                zone=junction.zone,
                vehicles=latest_reading.vehicle_count,
                speed=latest_reading.avg_speed,
                congestion=latest_reading.congestion_level,
                signal=signal.current_state,
                mode=signal.mode,
                density=latest_reading.density,
                latitude=junction.latitude,
                longitude=junction.longitude
            ))
    
    return result

@router.get("/{junction_id}", response_model=schemas.JunctionWithSignal)
def get_junction(junction_id: int, db: Session = Depends(get_db)):
    """Get specific junction details"""
    junction = db.query(models.Junction).filter(models.Junction.id == junction_id).first()
    if not junction:
        raise HTTPException(status_code=404, detail="Junction not found")
    
    latest_reading = db.query(models.SensorReading).filter(
        models.SensorReading.junction_id == junction_id
    ).order_by(models.SensorReading.timestamp.desc()).first()
    
    signal = db.query(models.TrafficSignal).filter(
        models.TrafficSignal.junction_id == junction_id
    ).first()
    
    if latest_reading and signal:
        return schemas.JunctionWithSignal(
            id=junction.id,
            name=junction.name,
            zone=junction.zone,
            vehicles=latest_reading.vehicle_count,
            speed=latest_reading.avg_speed,
            congestion=latest_reading.congestion_level,
            signal=signal.current_state,
            mode=signal.mode,
            density=latest_reading.density,
            latitude=junction.latitude,
            longitude=junction.longitude
        )
    
    raise HTTPException(status_code=404, detail="No data available for junction")

@router.get("/stats")
def get_junction_stats(db: Session = Depends(get_db)):
    """Get junction statistics"""
    total_junctions = db.query(models.Junction).count()
    
    # Count by congestion level (latest readings)
    high_congestion = db.query(models.SensorReading).filter(
        models.SensorReading.congestion_level == 'H'
    ).count()
    
    medium_congestion = db.query(models.SensorReading).filter(
        models.SensorReading.congestion_level == 'M'
    ).count()
    
    low_congestion = db.query(models.SensorReading).filter(
        models.SensorReading.congestion_level == 'L'
    ).count()
    
    return {
        "total_junctions": total_junctions,
        "high_congestion": high_congestion,
        "medium_congestion": medium_congestion,
        "low_congestion": low_congestion,
        "timestamp": datetime.now().isoformat()
    }
