from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import logging
import networkx as nx

from api.models import RouteRequest, HeatmapCell
from core.safety_config import BOUNDS, coords_in_bounds, get_time_multiplier
from services.route_service import get_loader, build_road_graph, find_nearest_junction, get_all_edges
from services.route_safety import calculate_safety_score
from services.familiarity_module import FamiliarityScoreCalculator, get_db
from cachetools import TTLCache

router = APIRouter(tags=["Routing"])
logger = logging.getLogger(__name__)

# Route cache (TTLCache: max 1000 routes, 300 second expiry)
route_cache = TTLCache(maxsize=1000, ttl=300)

def _build_route_response_summary(loader, path: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Helper to build consistent route metadata."""
    if not path:
        return {}
    stats = loader.get_path_stats(path)
    return {
        "distance_meters": stats.get("distance_meters", 0),
        "distance_km": stats.get("distance_km", 0),
        "avg_safety_score": stats.get("avg_safety_score", 0),
        "num_segments": stats.get("num_segments", 0),
        "coordinates": [{"latitude": p[0], "longitude": p[1]} for p in path]
    }

@router.post("/safest_route")
async def get_safest_route(request: RouteRequest, db=Depends(get_db)):
    """
    Calculate the safest route between two points.
    """
    # Bounds validation
    if not coords_in_bounds(request.start.lat, request.start.lng):
        raise HTTPException(
            status_code=400,
            detail=f"Start coordinates ({request.start.lat}, {request.start.lng}) are outside the supported area.",
        )
    if not coords_in_bounds(request.end.lat, request.end.lng):
        raise HTTPException(
            status_code=400,
            detail=f"End coordinates ({request.end.lat}, {request.end.lng}) are outside the supported area.",
        )

    # Parse time
    hour = datetime.now().hour
    if request.time:
        try:
            hour = int(request.time.split(":")[0])
        except (ValueError, IndexError):
            pass

    # Check cache
    cache_key = f"{request.start.lat}_{request.start.lng}_{request.end.lat}_{request.end.lng}_{hour}_{request.user_id}"
    if cache_key in route_cache:
        return route_cache[cache_key]

    loader = get_loader()
    if not loader or not loader.nx_graph:
        raise HTTPException(status_code=500, detail="Road graph not loaded")

    # Build junction-based graph
    G = loader.nx_graph
    junctions = loader.junctions
    
    start_junction = loader.find_nearest_junction(request.start.lat, request.start.lng)
    end_junction   = loader.find_nearest_junction(request.end.lat,   request.end.lng)

    if not start_junction or not end_junction:
        raise HTTPException(status_code=400, detail="Could not find junctions near given coordinates")

    start_node = start_junction[0]
    end_node = end_junction[0]

    if start_node == end_node:
        raise HTTPException(status_code=400, detail="Start and end resolve to the same junction.")

    # Calculate routes
    try:
        # Safest path (uses safety_weight assigned in find_safest_path)
        # We'll just call the loader's method
        safest_path = loader.find_safest_path(start_node, end_node)
        
        # Shortest path (pure distance)
        shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight="distance")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        logger.warning(f"Routing failed: {e}")
        raise HTTPException(status_code=404, detail="No route found")

    result = {
        "safest_route": _build_route_response_summary(loader, safest_path),
        "shortest_route": _build_route_response_summary(loader, shortest_path),
        "time_of_day": f"{hour}:00",
        "time_multiplier": get_time_multiplier(hour),
        "cached": False,
    }

    route_cache[cache_key] = {**result, "cached": True}
    return result

@router.get("/heatmap/spatial")
async def get_spatial_heatmap(hour: Optional[int] = None):
    """
    Risk Heatmap Engine: Aggregates segment-level safety scores into 
    a 20x20 spatial grid.
    """
    if hour is None:
        hour = datetime.now().hour

    edges = get_all_edges()
    if not edges:
        return {"cells_count": 0, "cells": []}

    # Grid parameters
    grid_size = 20
    lat_step = (BOUNDS["max_lat"] - BOUNDS["min_lat"]) / grid_size
    lng_step = (BOUNDS["max_lng"] - BOUNDS["min_lng"]) / grid_size

    grid_accumulation = {}

    for seg in edges:
        # We need start_lat, start_lon etc. for this
        # RoadGraphLoader edges have 'from_lat', 'from_lng', etc.
        s_lat = seg.get("from_lat") or seg.get("start_lat")
        s_lng = seg.get("from_lng") or seg.get("start_lon")
        e_lat = seg.get("to_lat") or seg.get("end_lat")
        e_lng = seg.get("to_lng") or seg.get("end_lon")
        
        if s_lat is None or s_lng is None or e_lat is None or e_lng is None:
            continue
            
        safety, _ = calculate_safety_score(seg, hour)
        risk_delta = 100.0 - safety
        
        mid_lat = (s_lat + e_lat) / 2.0
        mid_lng = (s_lng + e_lng) / 2.0
        
        lat_idx = int((mid_lat - BOUNDS["min_lat"]) / lat_step)
        lng_idx = int((mid_lng - BOUNDS["min_lng"]) / lng_step)
        
        lat_idx = max(0, min(grid_size - 1, lat_idx))
        lng_idx = max(0, min(grid_size - 1, lng_idx))
        
        cell_key = (lat_idx, lng_idx)
        if cell_key not in grid_accumulation:
            grid_accumulation[cell_key] = {"risks": [], "safety_scores": [], "segment_ids": []}
        
        grid_accumulation[cell_key]["risks"].append(risk_delta)
        grid_accumulation[cell_key]["safety_scores"].append(safety)
        grid_accumulation[cell_key]["segment_ids"].append(str(seg.get("edge_id", "")))

    heatmap_cells = []
    
    all_cell_total_risks = [sum(data["risks"]) for data in grid_accumulation.values()]
    max_observed_risk = max(all_cell_total_risks) if all_cell_total_risks else 1.0

    for (lat_idx, lng_idx), data in grid_accumulation.items():
        cell_risk_sum = sum(data["risks"])
        intensity = round(float(cell_risk_sum / max_observed_risk), 3) if max_observed_risk > 0 else 0.0
        avg_safety = round(float(sum(data["safety_scores"]) / len(data["safety_scores"])), 1)
        
        cell_min_lat = BOUNDS["min_lat"] + (lat_idx * lat_step)
        cell_max_lat = cell_min_lat + lat_step
        cell_min_lng = BOUNDS["min_lng"] + (lng_idx * lng_step)
        cell_max_lng = cell_min_lng + lng_step
        
        heatmap_cells.append({
            "min_lat": cell_min_lat,
            "max_lat": cell_max_lat,
            "min_lng": cell_min_lng,
            "max_lng": cell_max_lng,
            "risk_intensity": intensity,
            "segment_ids": data["segment_ids"],
            "average_safety": avg_safety
        })

    return {
        "hour": hour,
        "grid_resolution": f"{grid_size}x{grid_size}",
        "bounding_box": BOUNDS,
        "cells_count": len(heatmap_cells),
        "cells": heatmap_cells
    }
