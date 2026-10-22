"""
Spark Streaming Job for Real-Time Traffic Processing
Reads from Kafka, processes data, detects congestion, and generates alerts
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

def create_spark_session():
    """Create Spark session with Kafka support"""
    return SparkSession.builder \
        .appName("TrafficStreamProcessor") \
        .config("spark.kafka.bootstrap.servers", "kafka:9092") \
        .getOrCreate()

def process_traffic_stream(spark):
    """Process real-time traffic data from Kafka"""
    
    # Define schema for traffic data
    traffic_schema = StructType([
        StructField("junction_id", IntegerType()),
        StructField("junction_name", StringType()),
        StructField("zone", StringType()),
        StructField("vehicle_count", IntegerType()),
        StructField("avg_speed", FloatType()),
        StructField("density", IntegerType()),
        StructField("congestion_level", StringType()),
        StructField("timestamp", StringType())
    ])
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "traffic-sensor-data") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON
    traffic_df = df.select(
        from_json(col("value").cast("string"), traffic_schema).alias("data")
    ).select("data.*")
    
    # Windowed aggregation (5-second windows)
    windowed_df = traffic_df \
        .withWatermark("timestamp", "10 seconds") \
        .groupBy(
            window(col("timestamp"), "5 seconds"),
            col("junction_id")
        ) \
        .agg(
            avg("vehicle_count").alias("avg_vehicles"),
            avg("avg_speed").alias("avg_speed"),
            avg("density").alias("avg_density"),
            first("congestion_level").alias("congestion_level")
        )
    
    # Congestion detection and alert generation
    def detect_alerts(row):
        alerts = []
        if row.avg_speed < 20 and row.avg_vehicles > 250:
            alerts.append({
                "type": "heavy_congestion",
                "severity": "H",
                "message": f"Heavy congestion at junction {row.junction_id}"
            })
        return alerts
    
    # Write to console (for debugging)
    query = windowed_df \
        .writeStream \
        .outputMode("update") \
        .format("console") \
        .start()
    
    query.awaitTermination()

if __name__ == "__main__":
    spark = create_spark_session()
    process_traffic_stream(spark)
