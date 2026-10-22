"""
Run all sensor simulators as separate processes
"""

import multiprocessing
import time
from traffic_sensor import main as traffic_main
from gps_simulator import main as gps_main
from camera_simulator import main as camera_main

def run_traffic_sensor():
    """Run traffic sensor simulator"""
    try:
        traffic_main()
    except Exception as e:
        print(f"Traffic Sensor Error: {e}")

def run_gps_simulator():
    """Run GPS simulator"""
    try:
        gps_main()
    except Exception as e:
        print(f"GPS Simulator Error: {e}")

def run_camera_simulator():
    """Run camera simulator"""
    try:
        camera_main()
    except Exception as e:
        print(f"Camera Simulator Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("SmartFlow TMS - Sensor Simulation Suite")
    print("=" * 60)
    
    # Create processes
    processes = [
        multiprocessing.Process(target=run_traffic_sensor, name="TrafficSensor"),
        multiprocessing.Process(target=run_gps_simulator, name="GPSSimulator"),
        multiprocessing.Process(target=run_camera_simulator, name="CameraSimulator"),
    ]
    
    # Start all processes
    for process in processes:
        print(f"Starting {process.name}...")
        process.start()
        time.sleep(1)
    
    print("\nAll simulators running. Press Ctrl+C to stop.\n")
    
    try:
        # Wait for processes
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("\nShutting down all simulators...")
        for process in processes:
            process.terminate()
            process.join(timeout=5)
        print("All simulators stopped.")
