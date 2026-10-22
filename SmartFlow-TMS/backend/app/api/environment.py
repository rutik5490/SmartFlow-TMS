from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from datetime import datetime

router = APIRouter()

@router.get("/impact")
def get_environmental_impact(db: Session = Depends(get_db)):
    """Calculate environmental impact metrics"""
    # Get latest sensor readings
    readings = db.query(models.SensorReading).all()
    
    if not readings:
        return {
            "idle_time_saved_minutes": 0,
            "fuel_saved_liters": 0,
            "co2_reduced_kg": 0,
            "equivalent_trees": 0
        }
    
    # Calculate baseline (without optimization)
    baseline_avg_speed = 25  # km/h without smart system
    current_avg_speed = sum(r.avg_speed for r in readings) / len(readings)
    
    # Assume 8 hours of operation per day
    operation_hours = 8
    num_vehicles = sum(r.vehicle_count for r in readings)
    
    # Idle time calculation (simplified)
    time_saved_per_vehicle = (current_avg_speed - baseline_avg_speed) / current_avg_speed * operation_hours * 60
    idle_time_saved = max(0, time_saved_per_vehicle * num_vehicles)
    
    # Fuel savings (0.02 liters per minute of idle time)
    fuel_saved = idle_time_saved * 0.02
    
    # CO2 reduction (2.31 kg CO2 per liter of fuel)
    co2_reduced = fuel_saved * 2.31
    
    # Equivalent trees (22 kg CO2 absorbed per tree per year)
    equivalent_trees = co2_reduced / 22
    
    metric = models.EnvironmentalMetric(
        idle_time_saved_minutes=round(idle_time_saved, 2),
        fuel_saved_liters=round(fuel_saved, 2),
        co2_reduced_kg=round(co2_reduced, 2),
        equivalent_trees=round(equivalent_trees, 2)
    )
    
    db.add(metric)
    db.commit()
    
    return {
        "idle_time_saved_minutes": round(idle_time_saved, 2),
        "fuel_saved_liters": round(fuel_saved, 2),
        "co2_reduced_kg": round(co2_reduced, 2),
        "equivalent_trees": round(equivalent_trees, 2),
        "calculated_at": datetime.now().isoformat(),
        "metrics": {
            "average_speed_improvement": f"{round((current_avg_speed - baseline_avg_speed) / baseline_avg_speed * 100, 1)}%",
            "total_vehicles_tracked": num_vehicles,
            "operation_hours": operation_hours
        }
    }
