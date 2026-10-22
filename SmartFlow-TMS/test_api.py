"""
Test script to verify all API endpoints are working
Run this after starting the backend
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an endpoint and print result"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        status = "✅" if response.status_code in [200, 201] else "❌"
        print(f"{status} {method:4s} {endpoint:40s} - {response.status_code}")
        
        if response.status_code not in [200, 201]:
            print(f"   Error: {response.text}")
        
        return response.json()
    except Exception as e:
        print(f"❌ {method:4s} {endpoint:40s} - ERROR: {e}")
        return None

def main():
    print("=" * 70)
    print("SmartFlow TMS - API Testing Script")
    print("=" * 70)
    print()
    
    # Health check
    print("1. System Health")
    print("-" * 70)
    test_endpoint("GET", "/health")
    test_endpoint("GET", "/")
    print()
    
    # Intersections
    print("2. Traffic Monitoring")
    print("-" * 70)
    test_endpoint("GET", "/api/intersections")
    test_endpoint("GET", "/api/intersections/1")
    test_endpoint("GET", "/api/intersections/stats")
    print()
    
    # Alerts
    print("3. Alerts & Incidents")
    print("-" * 70)
    test_endpoint("GET", "/api/alerts")
    test_endpoint("GET", "/api/alerts/active/count")
    test_endpoint("POST", "/api/alerts/report", {
        "junction_id": 1,
        "alert_type": "Test Incident",
        "severity": "M",
        "description": "Testing alert system"
    })
    print()
    
    # Signals
    print("4. Signal Control")
    print("-" * 70)
    test_endpoint("GET", "/api/signals")
    test_endpoint("PUT", "/api/signals/1/state", {"state": "Red"})
    test_endpoint("POST", "/api/signals/emergency")
    test_endpoint("POST", "/api/signals/all-auto")
    print()
    
    # Predictions
    print("5. ML Predictions")
    print("-" * 70)
    test_endpoint("GET", "/api/predictions")
    test_endpoint("GET", "/api/predictions/hotspots")
    test_endpoint("GET", "/api/predictions/forecast")
    test_endpoint("GET", "/api/predictions/model-info")
    print()
    
    # Routes
    print("6. Route Optimization")
    print("-" * 70)
    test_endpoint("POST", "/api/routes/suggest", {
        "origin_id": 1,
        "destination_id": 8
    })
    test_endpoint("GET", "/api/routes/live-traffic")
    print()
    
    # Vehicles
    print("7. Vehicle Tracking")
    print("-" * 70)
    test_endpoint("GET", "/api/vehicles/active")
    test_endpoint("GET", "/api/vehicles/congestion-map")
    print()
    
    # Analytics
    print("8. Analytics")
    print("-" * 70)
    test_endpoint("GET", "/api/analytics/hourly")
    test_endpoint("GET", "/api/analytics/zones")
    test_endpoint("GET", "/api/analytics/peaks")
    test_endpoint("GET", "/api/analytics/vehicle-types")
    test_endpoint("GET", "/api/analytics/summary")
    print()
    
    # Environment
    print("9. Environmental Impact")
    print("-" * 70)
    test_endpoint("GET", "/api/environment/impact")
    print()
    
    print("=" * 70)
    print("Testing Complete!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Open http://localhost:8000/docs for interactive API testing")
    print("2. Start sensors: cd sensors && python run_sensors.py")
    print("3. Open traffic_management_system.html in browser")

if __name__ == "__main__":
    main()
