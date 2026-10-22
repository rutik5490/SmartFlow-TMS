-- SmartFlow TMS Database Schema
-- Initialize all tables for traffic management system

-- Junctions/Intersections
CREATE TABLE IF NOT EXISTS junctions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    zone VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real-time sensor readings
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    junction_id INTEGER REFERENCES junctions(id),
    vehicle_count INTEGER NOT NULL,
    avg_speed DECIMAL(5, 2) NOT NULL,
    density INTEGER NOT NULL,
    congestion_level VARCHAR(1) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Traffic signals
CREATE TABLE IF NOT EXISTS traffic_signals (
    id SERIAL PRIMARY KEY,
    junction_id INTEGER REFERENCES junctions(id),
    current_state VARCHAR(10) NOT NULL DEFAULT 'Green',
    mode VARCHAR(10) NOT NULL DEFAULT 'auto',
    green_duration INTEGER DEFAULT 60,
    red_duration INTEGER DEFAULT 60,
    yellow_duration INTEGER DEFAULT 5,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts/Incidents
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    junction_id INTEGER REFERENCES junctions(id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(1) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    description TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- GPS vehicle tracking
CREATE TABLE IF NOT EXISTS vehicle_positions (
    id SERIAL PRIMARY KEY,
    vehicle_id VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    speed DECIMAL(5, 2),
    heading DECIMAL(5, 2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Route suggestions
CREATE TABLE IF NOT EXISTS route_suggestions (
    id SERIAL PRIMARY KEY,
    origin_id INTEGER REFERENCES junctions(id),
    destination_id INTEGER REFERENCES junctions(id),
    suggested_route JSONB,
    alternative_routes JSONB,
    congestion_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    junction_id INTEGER REFERENCES junctions(id),
    predicted_congestion VARCHAR(1) NOT NULL,
    confidence DECIMAL(5, 2),
    prediction_horizon INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Public transport - Bus schedules
CREATE TABLE IF NOT EXISTS bus_schedules (
    id SERIAL PRIMARY KEY,
    route_id VARCHAR(20) NOT NULL,
    route_name VARCHAR(100),
    scheduled_time TIME NOT NULL,
    actual_time TIME,
    delay_minutes INTEGER DEFAULT 0,
    adjusted_by_ai BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'on_time'
);

-- Historical aggregations (for analytics)
CREATE TABLE IF NOT EXISTS hourly_aggregates (
    id SERIAL PRIMARY KEY,
    junction_id INTEGER REFERENCES junctions(id),
    hour INTEGER NOT NULL,
    avg_vehicles DECIMAL(10, 2),
    avg_speed DECIMAL(5, 2),
    max_congestion VARCHAR(1),
    date DATE NOT NULL,
    UNIQUE(junction_id, hour, date)
);

-- Environmental impact metrics
CREATE TABLE IF NOT EXISTS environmental_metrics (
    id SERIAL PRIMARY KEY,
    idle_time_saved_minutes DECIMAL(10, 2),
    fuel_saved_liters DECIMAL(10, 2),
    co2_reduced_kg DECIMAL(10, 2),
    equivalent_trees DECIMAL(10, 2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_sensor_readings_junction ON sensor_readings(junction_id);
CREATE INDEX idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_vehicle_positions_vehicle ON vehicle_positions(vehicle_id);
CREATE INDEX idx_vehicle_positions_timestamp ON vehicle_positions(timestamp);
CREATE INDEX idx_predictions_junction ON predictions(junction_id);
CREATE INDEX idx_hourly_aggregates_date ON hourly_aggregates(date);

-- Insert initial junctions (matching frontend)
INSERT INTO junctions (id, name, zone, latitude, longitude) VALUES
(1, 'MG Road × FC Road', 'Central', 18.5204, 73.8567),
(2, 'University Circle', 'North', 18.5314, 73.8456),
(3, 'Deccan Gymkhana', 'Central', 18.5167, 73.8389),
(4, 'Shivajinagar Signal', 'East', 18.5362, 73.8678),
(5, 'Kothrud Depot', 'West', 18.5074, 73.8077),
(6, 'Wakad Bridge', 'NorthWest', 18.5945, 73.7889),
(7, 'Viman Nagar Circle', 'East', 18.5679, 73.9145),
(8, 'Hadapsar Ring Road', 'SouthEast', 18.5089, 73.9260)
ON CONFLICT (id) DO NOTHING;

-- Insert initial traffic signals
INSERT INTO traffic_signals (junction_id, current_state, mode, green_duration, red_duration, yellow_duration)
SELECT id, 'Green', 'auto', 60, 60, 5 FROM junctions
ON CONFLICT DO NOTHING;

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password_hash, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILpBBS6Tu', 'admin')
ON CONFLICT (username) DO NOTHING;
