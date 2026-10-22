"""
Camera Simulator
Generates simplified computer vision output for traffic monitoring
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
TOPIC = 'camera-data'

# Junction camera configurations
JUNCTION_CAMERAS = [
    {"id": 1, "name": "MG Road × FC Road", "lanes": 4},
    {"id": 2, "name": "University Circle", "lanes": 3},
    {"id": 3, "name": "Deccan Gymkhana", "lanes": 4},
    {"id": 4, "name": "Shivajinagar Signal", "lanes": 3},
    {"id": 5, "name": "Kothrud Depot", "lanes": 4},
    {"id": 6, "name": "Wakad Bridge", "lanes": 2},
    {"id": 7, "name": "Viman Nagar Circle", "lanes": 3},
    {"id": 8, "name": "Hadapsar Ring Road", "lanes": 3},
]

def generate_camera_data():
    """Generate camera observation data for all junctions"""
    now = datetime.now()
    observations = []
    
    for camera in JUNCTION_CAMERAS:
        # Simulate vehicle detection per lane
        lane_occupancy = []
        total_vehicles = 0
        
        for lane in range(camera["lanes"]):
            # Random occupancy between 0.1 and 1.0
            occupancy = random.uniform(0.1, 1.0)
            lane_occupancy.append(round(occupancy, 2))
            total_vehicles += int(occupancy * 50)  # Max 50 vehicles per lane
        
        # Calculate average occupancy
        avg_occupancy = sum(lane_occupancy) / len(lane_occupancy)
        
        # Congestion flag based on occupancy
        congestion_flag = avg_occupancy > 0.7
        
        observation = {
            "junction_id": camera["id"],
            "junction_name": camera["name"],
            "vehicle_count": total_vehicles,
            "congestion_flag": congestion_flag,
            "lane_occupancy": lane_occupancy,
            "avg_occupancy": round(avg_occupancy, 2),
            "camera_status": "online",
            "timestamp": now.isoformat()
        }
        observations.append(observation)
    
    return observations

def main():
    """Main camera simulator loop"""
    print(f"Starting Camera Simulator...")
    print(f"Kafka Server: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {TOPIC}")
    
    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=5
    )
    
    print("Connected to Kafka. Publishing camera data every 5 seconds...")
    
    try:
        while True:
            observations = generate_camera_data()
            
            for obs in observations:
                producer.send(TOPIC, value=obs)
                congestion_status = "CONGESTED" if obs['congestion_flag'] else "CLEAR"
                print(f"[{obs['timestamp']}] Junction {obs['junction_id']}: "
                      f"Vehicles={obs['vehicle_count']}, "
                      f"Status={congestion_status}, "
                      f"Avg Occupancy={obs['avg_occupancy']}")
            
            producer.flush()
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nShutting down camera simulator...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
