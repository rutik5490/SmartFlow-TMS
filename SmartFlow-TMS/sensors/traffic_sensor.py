"""
Traffic Sensor Simulator
Generates realistic traffic data for all junctions and publishes to Kafka
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
TOPIC = 'traffic-sensor-data'

# Junction configurations
JUNCTIONS = [
    {"id": 1, "name": "MG Road × FC Road", "zone": "Central", "base_traffic": 245},
    {"id": 2, "name": "University Circle", "zone": "North", "base_traffic": 178},
    {"id": 3, "name": "Deccan Gymkhana", "zone": "Central", "base_traffic": 312},
    {"id": 4, "name": "Shivajinagar Signal", "zone": "East", "base_traffic": 134},
    {"id": 5, "name": "Kothrud Depot", "zone": "West", "base_traffic": 267},
    {"id": 6, "name": "Wakad Bridge", "zone": "NorthWest", "base_traffic": 89},
    {"id": 7, "name": "Viman Nagar Circle", "zone": "East", "base_traffic": 201},
    {"id": 8, "name": "Hadapsar Ring Road", "zone": "SouthEast", "base_traffic": 156},
]

# Time-based traffic multipliers (24 hours)
HOURLY_MULTIPLIERS = {
    0: 0.3, 1: 0.25, 2: 0.2, 3: 0.2, 4: 0.25,
    5: 0.4, 6: 0.7, 7: 0.9, 8: 1.0, 9: 0.85,
    10: 0.75, 11: 0.8, 12: 0.9, 13: 0.85, 14: 0.8,
    15: 0.85, 16: 0.95, 17: 1.0, 18: 0.95, 19: 0.8,
    20: 0.65, 21: 0.55, 22: 0.45, 23: 0.35
}

def get_traffic_multiplier(hour):
    """Get traffic multiplier based on hour of day"""
    return HOURLY_MULTIPLIERS.get(hour, 0.5)

def generate_sensor_data():
    """Generate realistic sensor data for all junctions"""
    now = datetime.now()
    hour = now.hour
    multiplier = get_traffic_multiplier(hour)
    
    readings = []
    for junction in JUNCTIONS:
        # Calculate vehicle count with time-based pattern and random variation
        base = junction["base_traffic"]
        vehicle_count = int(base * multiplier * random.uniform(0.85, 1.15))
        vehicle_count = max(20, min(400, vehicle_count))
        
        # Density calculation
        density = int((vehicle_count / 400) * 100)
        
        # Speed inversely related to density
        avg_speed = max(8, min(65, int(70 - (density * 0.55) + random.uniform(-3, 3))))
        
        # Congestion level
        if density > 70:
            congestion = "H"
        elif density > 40:
            congestion = "M"
        else:
            congestion = "L"
        
        reading = {
            "junction_id": junction["id"],
            "junction_name": junction["name"],
            "zone": junction["zone"],
            "vehicle_count": vehicle_count,
            "avg_speed": avg_speed,
            "density": density,
            "congestion_level": congestion,
            "timestamp": now.isoformat()
        }
        readings.append(reading)
    
    return readings

def main():
    """Main simulator loop"""
    print(f"Starting Traffic Sensor Simulator...")
    print(f"Kafka Server: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {TOPIC}")
    
    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=5
    )
    
    print("Connected to Kafka. Publishing sensor data every 3 seconds...")
    
    try:
        while True:
            readings = generate_sensor_data()
            
            for reading in readings:
                producer.send(TOPIC, value=reading)
                print(f"[{reading['timestamp']}] Junction {reading['junction_id']}: "
                      f"Vehicles={reading['vehicle_count']}, "
                      f"Speed={reading['avg_speed']} km/h, "
                      f"Congestion={reading['congestion_level']}")
            
            producer.flush()
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nShutting down sensor simulator...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
