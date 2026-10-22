"""
GPS Vehicle Simulator
Simulates 50-100 vehicles moving on road network and publishes to Kafka
"""

import json
import time
import random
import math
from datetime import datetime
from kafka import KafkaProducer

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
TOPIC = 'gps-data'

# Road network nodes (junctions with coordinates)
ROAD_NODES = {
    1: {"lat": 18.5204, "lng": 73.8567, "name": "MG Road × FC Road"},
    2: {"lat": 18.5314, "lng": 73.8456, "name": "University Circle"},
    3: {"lat": 18.5167, "lng": 73.8389, "name": "Deccan Gymkhana"},
    4: {"lat": 18.5362, "lng": 73.8678, "name": "Shivajinagar Signal"},
    5: {"lat": 18.5074, "lng": 73.8077, "name": "Kothrud Depot"},
    6: {"lat": 18.5945, "lng": 73.7889, "name": "Wakad Bridge"},
    7: {"lat": 18.5679, "lng": 73.9145, "name": "Viman Nagar Circle"},
    8: {"lat": 18.5089, "lng": 73.9260, "name": "Hadapsar Ring Road"},
}

# Define road connections (edges)
ROAD_EDGES = [
    (1, 2), (1, 3), (1, 4),
    (2, 4), (2, 6),
    (3, 5), (3, 8),
    (4, 7),
    (5, 8),
    (6, 7),
    (7, 8),
]

NUM_VEHICLES = 75

class Vehicle:
    """Simulated vehicle with GPS tracking"""
    
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        # Start at random node
        self.current_node = random.randint(1, 8)
        self.target_node = self._select_next_node()
        self.progress = 0.0  # 0.0 to 1.0 between nodes
        self.speed = random.uniform(30, 60)
        self.heading = 0.0
        
    def _select_next_node(self):
        """Select next node from connected edges"""
        connected = []
        for edge in ROAD_EDGES:
            if edge[0] == self.current_node:
                connected.append(edge[1])
            elif edge[1] == self.current_node:
                connected.append(edge[0])
        return random.choice(connected) if connected else self.current_node
    
    def update_position(self):
        """Update vehicle position"""
        # Move towards target
        self.progress += random.uniform(0.02, 0.05)
        
        if self.progress >= 1.0:
            # Reached target, select new target
            self.current_node = self.target_node
            self.target_node = self._select_next_node()
            self.progress = 0.0
        
        # Interpolate position
        start = ROAD_NODES[self.current_node]
        end = ROAD_NODES[self.target_node]
        
        lat = start["lat"] + (end["lat"] - start["lat"]) * self.progress
        lng = start["lng"] + (end["lng"] - start["lng"]) * self.progress
        
        # Calculate heading
        self.heading = math.degrees(math.atan2(
            end["lng"] - start["lng"],
            end["lat"] - start["lat"]
        ))
        
        # Vary speed slightly
        self.speed = max(5, min(80, self.speed + random.uniform(-5, 5)))
        
        return {
            "vehicle_id": self.vehicle_id,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "speed": round(self.speed, 2),
            "heading": round(self.heading, 2),
            "current_node": self.current_node,
            "target_node": self.target_node,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main GPS simulator loop"""
    print(f"Starting GPS Simulator with {NUM_VEHICLES} vehicles...")
    print(f"Kafka Server: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {TOPIC}")
    
    # Create vehicles
    vehicles = [Vehicle(f"VH-{i:03d}") for i in range(1, NUM_VEHICLES + 1)]
    
    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=5
    )
    
    print("Connected to Kafka. Publishing GPS data every 2 seconds...")
    
    try:
        while True:
            for vehicle in vehicles:
                position = vehicle.update_position()
                producer.send(TOPIC, value=position)
            
            producer.flush()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Published positions for {NUM_VEHICLES} vehicles")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nShutting down GPS simulator...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
