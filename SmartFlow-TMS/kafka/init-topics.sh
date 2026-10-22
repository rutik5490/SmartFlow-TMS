#!/bin/bash
# Initialize Kafka topics for SmartFlow TMS

echo "Creating Kafka topics..."

# Wait for Kafka to be ready
sleep 10

# Create topics
kafka-topics.sh --create --topic traffic-sensor-data --partitions 3 --replication-factor 1 --bootstrap-server kafka:9092 --if-not-exists
kafka-topics.sh --create --topic gps-data --partitions 3 --replication-factor 1 --bootstrap-server kafka:9092 --if-not-exists
kafka-topics.sh --create --topic camera-data --partitions 2 --replication-factor 1 --bootstrap-server kafka:9092 --if-not-exists
kafka-topics.sh --create --topic processed-traffic --partitions 3 --replication-factor 1 --bootstrap-server kafka:9092 --if-not-exists
kafka-topics.sh --create --topic alerts --partitions 2 --replication-factor 1 --bootstrap-server kafka:9092 --if-not-exists
kafka-topics.sh --create --topic signal-commands --partitions 2 --replication-factor 1 --bootstrap-server kafka:9092 --if-not-exists
kafka-topics.sh --create --topic predictions --partitions 2 --replication-factor 1 --bootstrap-server kafka:9092 --if-not-exists

echo "All topics created successfully!"

# List topics
kafka-topics.sh --list --bootstrap-server kafka:9092
