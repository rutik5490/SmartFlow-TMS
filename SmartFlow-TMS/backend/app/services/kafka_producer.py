"""
Kafka Producer Service
Publishes data to Kafka topics
"""

from kafka import KafkaProducer
import json
from app.config import settings

class KafkaProducerService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def send_sensor_data(self, data: dict):
        """Publish sensor data to Kafka"""
        self.producer.send('traffic-sensor-data', value=data)
        self.producer.flush()
    
    def send_alert(self, alert_data: dict):
        """Publish alert to Kafka"""
        self.producer.send('alerts', value=alert_data)
        self.producer.flush()
    
    def send_signal_command(self, command: dict):
        """Publish signal command to Kafka"""
        self.producer.send('signal-commands', value=command)
        self.producer.flush()
    
    def close(self):
        """Close producer connection"""
        self.producer.close()
