from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[schemas.SignalResponse])
def get_all_signals(db: Session = Depends(get_db)):
    """Get all traffic signal states"""
    signals = db.query(models.TrafficSignal).all()
    return signals

@router.get("/{junction_id}", response_model=schemas.SignalResponse)
def get_signal(junction_id: int, db: Session = Depends(get_db)):
    """Get specific signal state"""
    signal = db.query(models.TrafficSignal).filter(
        models.TrafficSignal.junction_id == junction_id
    ).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal

@router.put("/{junction_id}/state", response_model=schemas.SignalResponse)
def update_signal_state(
    junction_id: int,
    signal_update: schemas.SignalUpdate,
    db: Session = Depends(get_db)
):
    """Change signal state"""
    signal = db.query(models.TrafficSignal).filter(
        models.TrafficSignal.junction_id == junction_id
    ).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    signal.current_state = signal_update.state
    signal.mode = 'manual'
    signal.updated_at = datetime.now()
    db.commit()
    db.refresh(signal)
    
    return signal

@router.put("/{junction_id}/mode", response_model=schemas.SignalResponse)
def update_signal_mode(
    junction_id: int,
    mode_update: schemas.SignalModeUpdate,
    db: Session = Depends(get_db)
):
    """Toggle signal mode (auto/manual)"""
    signal = db.query(models.TrafficSignal).filter(
        models.TrafficSignal.junction_id == junction_id
    ).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    signal.mode = mode_update.mode
    signal.updated_at = datetime.now()
    db.commit()
    db.refresh(signal)
    
    return signal

@router.post("/emergency")
def emergency_mode(db: Session = Depends(get_db)):
    """Activate emergency mode - clear path through specific junctions"""
    # Set all signals to red
    db.query(models.TrafficSignal).update({
        "current_state": "Red",
        "mode": "manual",
        "updated_at": datetime.now()
    })
    
    # Clear path through junctions 2, 4, 6 (University Circle → Shivajinagar → Wakad Bridge)
    emergency_path = [2, 4, 6]
    for junction_id in emergency_path:
        signal = db.query(models.TrafficSignal).filter(
            models.TrafficSignal.junction_id == junction_id
        ).first()
        if signal:
            signal.current_state = "Green"
    
    db.commit()
    
    return {
        "message": "Emergency route cleared!",
        "path": "University Circle → Shivajinagar → Wakad Bridge",
        "cleared_junctions": emergency_path
    }

@router.post("/all-auto")
def set_all_auto(db: Session = Depends(get_db)):
    """Set all signals to auto mode"""
    db.query(models.TrafficSignal).update({
        "mode": "auto",
        "updated_at": datetime.now()
    })
    db.commit()
    
    return {"message": "All signals set to auto mode"}

@router.put("/optimize/{junction_id}")
def optimize_signal_timing(junction_id: int, db: Session = Depends(get_db)):
    """AI-optimize signal timing based on current congestion"""
    signal = db.query(models.TrafficSignal).filter(
        models.TrafficSignal.junction_id == junction_id
    ).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    # Get latest sensor reading
    latest = db.query(models.SensorReading).filter(
        models.SensorReading.junction_id == junction_id
    ).order_by(models.SensorReading.timestamp.desc()).first()
    
    if latest:
        # Adaptive timing logic
        if latest.congestion_level == 'H':
            signal.green_duration = 90
            signal.red_duration = 45
        elif latest.congestion_level == 'M':
            signal.green_duration = 60
            signal.red_duration = 60
        else:
            signal.green_duration = 30
            signal.red_duration = 75
        
        signal.updated_at = datetime.now()
        db.commit()
        
        return {
            "message": f"Signal optimized for {latest.congestion_level} congestion",
            "green_duration": signal.green_duration,
            "red_duration": signal.red_duration
        }
    
    return {"message": "No sensor data available"}
