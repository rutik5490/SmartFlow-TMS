from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter()

@router.get("/hourly")
def get_hourly_traffic(db: Session = Depends(get_db)):
    """Get 24-hour traffic volume data"""
    today = datetime.now().date()
    
    # Get hourly aggregates for today
    aggregates = db.query(models.HourlyAggregate).filter(
        func.date(models.HourlyAggregate.date) == today
    ).order_by(models.HourlyAggregate.hour).all()
    
    if aggregates:
        return [
            {
                "hour": agg.hour,
                "avg_vehicles": agg.avg_vehicles,
                "avg_speed": agg.avg_speed,
                "max_congestion": agg.max_congestion
            }
            for agg in aggregates
        ]
    
    # Generate simulated data if no aggregates exist
    return generate_hourly_pattern()

@router.get("/zones")
def get_zone_analytics(db: Session = Depends(get_db)):
    """Get zone-wise traffic distribution"""
    junctions = db.query(models.Junction).all()
    
    zones = {}
    for junction in junctions:
        latest = db.query(models.SensorReading).filter(
            models.SensorReading.junction_id == junction.id
        ).order_by(models.SensorReading.timestamp.desc()).first()
        
        zone = junction.zone
        if zone not in zones:
            zones[zone] = {"total_vehicles": 0, "speeds": [], "junctions": 0}
        
        if latest:
            zones[zone]["total_vehicles"] += latest.vehicle_count
            zones[zone]["speeds"].append(latest.avg_speed)
        zones[zone]["junctions"] += 1
    
    result = []
    for zone, data in zones.items():
        avg_speed = sum(data["speeds"]) / len(data["speeds"]) if data["speeds"] else 0
        result.append({
            "zone": zone,
            "total_vehicles": data["total_vehicles"],
            "avg_speed": round(avg_speed, 2)
        })
    
    return result

@router.get("/peaks")
def get_peak_hours_analysis(db: Session = Depends(get_db)):
    """Get peak hours analysis"""
    return {
        "peak_hours": [
            {
                "time": "08:00-09:00",
                "congestion": 93,
                "label": "Morning Peak",
                "description": "Highest traffic volume during morning commute"
            },
            {
                "time": "13:00-14:00",
                "congestion": 91,
                "label": "Lunch Hour",
                "description": "Midday traffic surge"
            },
            {
                "time": "18:00-19:00",
                "congestion": 95,
                "label": "Evening Peak",
                "description": "Evening rush hour maximum congestion"
            }
        ]
    }

@router.get("/vehicle-types")
def get_vehicle_type_distribution():
    """Get vehicle type distribution"""
    return [
        {"type": "Cars", "percentage": 58, "color": "#00d4aa"},
        {"type": "Bikes", "percentage": 24, "color": "#0091ff"},
        {"type": "Buses", "percentage": 11, "color": "#f59e0b"},
        {"type": "Trucks", "percentage": 7, "color": "#ef4444"}
    ]

def generate_hourly_pattern():
    """Generate typical hourly traffic pattern"""
    pattern = [42, 38, 51, 69, 85, 93, 88, 76, 64, 71, 82, 91, 
               79, 66, 58, 63, 74, 88, 95, 87, 72, 61, 49, 34]
    
    return [
        {
            "hour": i,
            "avg_vehicles": pattern[i],
            "avg_speed": round(70 - (pattern[i] * 0.55), 2),
            "max_congestion": "H" if pattern[i] > 80 else "M" if pattern[i] > 60 else "L"
        }
        for i in range(24)
    ]

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """Get overall analytics summary"""
    total_junctions = db.query(models.Junction).count()
    
    # Latest readings
    latest_readings = []
    for j in range(1, total_junctions + 1):
        reading = db.query(models.SensorReading).filter(
            models.SensorReading.junction_id == j
        ).order_by(models.SensorReading.timestamp.desc()).first()
        if reading:
            latest_readings.append(reading)
    
    total_vehicles = sum(r.vehicle_count for r in latest_readings)
    avg_speed = sum(r.avg_speed for r in latest_readings) / len(latest_readings) if latest_readings else 0
    
    return {
        "total_junctions": total_junctions,
        "total_vehicles": total_vehicles,
        "avg_speed": round(avg_speed, 2),
        "data_points": db.query(models.SensorReading).count(),
        "timestamp": datetime.now().isoformat()
    }
