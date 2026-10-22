from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class Junction(Base):
    __tablename__ = "junctions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    zone = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    junction_id = Column(Integer, ForeignKey("junctions.id"))
    vehicle_count = Column(Integer, nullable=False)
    avg_speed = Column(Float, nullable=False)
    density = Column(Integer, nullable=False)
    congestion_level = Column(String(1), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class TrafficSignal(Base):
    __tablename__ = "traffic_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    junction_id = Column(Integer, ForeignKey("junctions.id"))
    current_state = Column(String(10), nullable=False, default="Green")
    mode = Column(String(10), nullable=False, default="auto")
    green_duration = Column(Integer, default=60)
    red_duration = Column(Integer, default=60)
    yellow_duration = Column(Integer, default=5)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    junction_id = Column(Integer, ForeignKey("junctions.id"))
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(1), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    description = Column(Text)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

class VehiclePosition(Base):
    __tablename__ = "vehicle_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String(20), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float)
    heading = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class RouteSuggestion(Base):
    __tablename__ = "route_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    origin_id = Column(Integer, ForeignKey("junctions.id"))
    destination_id = Column(Integer, ForeignKey("junctions.id"))
    suggested_route = Column(JSON)
    alternative_routes = Column(JSON)
    congestion_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    junction_id = Column(Integer, ForeignKey("junctions.id"))
    predicted_congestion = Column(String(1), nullable=False)
    confidence = Column(Float)
    prediction_horizon = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BusSchedule(Base):
    __tablename__ = "bus_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String(20), nullable=False)
    route_name = Column(String(100))
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    actual_time = Column(DateTime(timezone=True))
    delay_minutes = Column(Integer, default=0)
    adjusted_by_ai = Column(Boolean, default=False)
    status = Column(String(20), default="on_time")

class HourlyAggregate(Base):
    __tablename__ = "hourly_aggregates"
    
    id = Column(Integer, primary_key=True, index=True)
    junction_id = Column(Integer, ForeignKey("junctions.id"))
    hour = Column(Integer, nullable=False)
    avg_vehicles = Column(Float)
    avg_speed = Column(Float)
    max_congestion = Column(String(1))
    date = Column(DateTime(timezone=True), nullable=False)

class EnvironmentalMetric(Base):
    __tablename__ = "environmental_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    idle_time_saved_minutes = Column(Float)
    fuel_saved_liters = Column(Float)
    co2_reduced_kg = Column(Float)
    equivalent_trees = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
