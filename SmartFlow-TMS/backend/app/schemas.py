from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Junction schemas
class JunctionBase(BaseModel):
    name: str
    zone: str
    latitude: float
    longitude: float

class JunctionResponse(JunctionBase):
    id: int
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Sensor reading schemas
class SensorReadingBase(BaseModel):
    junction_id: int
    vehicle_count: int
    avg_speed: float
    density: int
    congestion_level: str

class SensorReadingResponse(SensorReadingBase):
    id: int
    timestamp: Optional[datetime]
    
    class Config:
        from_attributes = True

# Signal schemas
class SignalUpdate(BaseModel):
    state: str = Field(..., pattern="^(Red|Yellow|Green)$")
    
class SignalModeUpdate(BaseModel):
    mode: str = Field(..., pattern="^(auto|manual)$")

class SignalResponse(BaseModel):
    id: int
    junction_id: int
    current_state: str
    mode: str
    green_duration: int
    red_duration: int
    yellow_duration: int
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Alert schemas
class AlertReport(BaseModel):
    junction_id: int
    alert_type: str
    severity: str = Field(..., pattern="^[HML]$")
    description: str

class AlertResponse(BaseModel):
    id: int
    junction_id: int
    alert_type: str
    severity: str
    status: str
    description: Optional[str]
    detected_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Route schemas
class RouteRequest(BaseModel):
    origin_id: int
    destination_id: int

class RouteResponse(BaseModel):
    primary: List[int]
    alternatives: List[List[int]]
    time_savings: str
    congestion_score: float

# Prediction schemas
class PredictionResponse(BaseModel):
    junction_id: int
    predicted_congestion: str
    confidence: float
    prediction_horizon: int
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Vehicle schemas
class VehiclePositionResponse(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    speed: Optional[float]
    heading: Optional[float]
    timestamp: Optional[datetime]
    
    class Config:
        from_attributes = True

# Analytics schemas
class HourlyAnalytics(BaseModel):
    hour: int
    avg_vehicles: float
    avg_speed: float
    max_congestion: str

class ZoneAnalytics(BaseModel):
    zone: str
    total_vehicles: int
    avg_speed: float

# Environmental schemas
class EnvironmentalResponse(BaseModel):
    idle_time_saved_minutes: float
    fuel_saved_liters: float
    co2_reduced_kg: float
    equivalent_trees: float
    calculated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Junction with signal (combined response)
class JunctionWithSignal(BaseModel):
    id: int
    name: str
    zone: str
    vehicles: int
    speed: float
    congestion: str
    signal: str
    mode: str
    density: int
    latitude: float
    longitude: float
