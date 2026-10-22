from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from datetime import datetime
import heapq

router = APIRouter()

# Road graph definition
ROAD_GRAPH = {
    1: {2: 5, 3: 8, 4: 6},
    2: {1: 5, 4: 4, 6: 7},
    3: {1: 8, 5: 6, 8: 9},
    4: {1: 6, 2: 4, 7: 5},
    5: {3: 6, 8: 4},
    6: {2: 7, 7: 3},
    7: {4: 5, 6: 3, 8: 6},
    8: {3: 9, 5: 4, 7: 6}
}

@router.post("/suggest", response_model=schemas.RouteResponse)
def suggest_route(route_request: schemas.RouteRequest, db: Session = Depends(get_db)):
    """Get optimal route suggestion using Dijkstra's algorithm"""
    origin_id = route_request.origin_id
    dest_id = route_request.destination_id
    
    if origin_id not in ROAD_GRAPH or dest_id not in ROAD_GRAPH:
        raise HTTPException(status_code=404, detail="Invalid junction ID")
    
    # Get current congestion data to adjust weights
    congestion_weights = get_congestion_weights(db)
    
    # Run Dijkstra's algorithm
    primary_route = dijkstra(ROAD_GRAPH, origin_id, dest_id, congestion_weights)
    
    if not primary_route:
        raise HTTPException(status_code=404, detail="No route found")
    
    # Find alternative route (exclude one edge from primary)
    alt_route = find_alternative_route(ROAD_GRAPH, origin_id, dest_id, primary_route, congestion_weights)
    
    # Calculate time savings
    primary_cost = calculate_route_cost(primary_route, congestion_weights)
    alt_cost = calculate_route_cost(alt_route, congestion_weights) if alt_route else primary_cost * 1.2
    
    time_savings = f"{max(0, int((alt_cost - primary_cost) * 2))} minutes faster"
    
    return schemas.RouteResponse(
        primary=primary_route,
        alternatives=[alt_route] if alt_route else [],
        time_savings=time_savings,
        congestion_score=round(primary_cost, 2)
    )

@router.get("/live-traffic")
def get_live_traffic_status(db: Session = Depends(get_db)):
    """Get current traffic status for all road segments"""
    junctions = db.query(models.Junction).all()
    road_status = []
    
    for junction in junctions:
        latest = db.query(models.SensorReading).filter(
            models.SensorReading.junction_id == junction.id
        ).order_by(models.SensorReading.timestamp.desc()).first()
        
        if latest:
            road_status.append({
                "junction_id": junction.id,
                "junction_name": junction.name,
                "congestion_level": latest.congestion_level,
                "avg_speed": latest.avg_speed,
                "vehicle_count": latest.vehicle_count
            })
    
    return road_status

def get_congestion_weights(db: Session):
    """Get current congestion-based weight multipliers"""
    weights = {}
    junctions = db.query(models.Junction).all()
    
    for junction in junctions:
        latest = db.query(models.SensorReading).filter(
            models.SensorReading.junction_id == junction.id
        ).order_by(models.SensorReading.timestamp.desc()).first()
        
        if latest:
            if latest.congestion_level == 'H':
                weights[junction.id] = 4.0
            elif latest.congestion_level == 'M':
                weights[junction.id] = 2.0
            else:
                weights[junction.id] = 1.0
        else:
            weights[junction.id] = 1.0
    
    return weights

def dijkstra(graph, start, end, weights=None):
    """Dijkstra's algorithm for shortest path"""
    if weights is None:
        weights = {node: 1.0 for node in graph}
    
    # Priority queue: (cost, node, path)
    pq = [(0, start, [start])]
    visited = set()
    
    while pq:
        cost, current, path = heapq.heappop(pq)
        
        if current == end:
            return path
        
        if current in visited:
            continue
        
        visited.add(current)
        
        for neighbor, base_weight in graph.get(current, {}).items():
            if neighbor not in visited:
                # Adjust weight based on congestion
                adjusted_weight = base_weight * weights.get(neighbor, 1.0)
                new_cost = cost + adjusted_weight
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))
    
    return None

def find_alternative_route(graph, start, end, primary_route, weights):
    """Find alternative route by excluding one edge from primary"""
    if len(primary_route) < 3:
        return None
    
    # Try excluding each intermediate node
    for i in range(1, len(primary_route) - 1):
        excluded = primary_route[i]
        
        # Create modified graph without the excluded node
        modified_graph = {
            node: {n: w for n, w in neighbors.items() if n != excluded}
            for node, neighbors in graph.items()
            if node != excluded
        }
        
        alt_route = dijkstra(modified_graph, start, end, weights)
        if alt_route and alt_route != primary_route:
            return alt_route
    
    return None

def calculate_route_cost(route, weights):
    """Calculate total cost of a route"""
    if not route:
        return 0
    
    total_cost = 0
    for i in range(len(route) - 1):
        current = route[i]
        next_node = route[i + 1]
        
        # Get base weight from graph
        base_weight = ROAD_GRAPH.get(current, {}).get(next_node, 10)
        congestion_multiplier = weights.get(next_node, 1.0)
        
        total_cost += base_weight * congestion_multiplier
    
    return total_cost
