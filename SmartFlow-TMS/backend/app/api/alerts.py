from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[schemas.AlertResponse])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all alerts with optional filters"""
    query = db.query(models.Alert)
    
    if status:
        query = query.filter(models.Alert.status == status)
    if severity:
        query = query.filter(models.Alert.severity == severity)
    
    alerts = query.order_by(models.Alert.detected_at.desc()).all()
    return alerts

@router.get("/active/count")
def get_active_alert_count(db: Session = Depends(get_db)):
    """Get count of active alerts"""
    count = db.query(models.Alert).filter(models.Alert.status == 'active').count()
    return {"active_count": count}

@router.get("/{alert_id}", response_model=schemas.AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get specific alert details"""
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/{alert_id}/resolve", response_model=schemas.AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Resolve an alert"""
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = 'resolved'
    alert.resolved_at = datetime.now()
    db.commit()
    db.refresh(alert)
    
    return alert

@router.post("/report", response_model=schemas.AlertResponse)
def report_incident(alert_data: schemas.AlertReport, db: Session = Depends(get_db)):
    """Report a new incident"""
    alert = models.Alert(
        junction_id=alert_data.junction_id,
        alert_type=alert_data.alert_type,
        severity=alert_data.severity,
        description=alert_data.description,
        status='active',
        detected_at=datetime.now()
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert

@router.post("/resolve-all")
def resolve_all_alerts(db: Session = Depends(get_db)):
    """Resolve all active alerts"""
    db.query(models.Alert).filter(
        models.Alert.status == 'active'
    ).update({
        "status": "resolved",
        "resolved_at": datetime.now()
    })
    db.commit()
    return {"message": "All alerts resolved"}

@router.get("/summary")
def get_alert_summary(db: Session = Depends(get_db)):
    """Get alert summary statistics"""
    total = db.query(models.Alert).count()
    active = db.query(models.Alert).filter(models.Alert.status == 'active').count()
    monitoring = db.query(models.Alert).filter(models.Alert.status == 'monitoring').count()
    resolved = db.query(models.Alert).filter(models.Alert.status == 'resolved').count()
    
    high = db.query(models.Alert).filter(models.Alert.severity == 'H').count()
    medium = db.query(models.Alert).filter(models.Alert.severity == 'M').count()
    low = db.query(models.Alert).filter(models.Alert.severity == 'L').count()
    
    return {
        "total": total,
        "active": active,
        "monitoring": monitoring,
        "resolved": resolved,
        "severity": {
            "high": high,
            "medium": medium,
            "low": low
        }
    }
