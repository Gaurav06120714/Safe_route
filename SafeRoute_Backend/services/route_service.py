from typing import Optional, Dict, List, Tuple
import logging
from .route_graph_loader import RoadGraphLoader

logger = logging.getLogger(__name__)

# Singleton instance
_loader = None

def get_loader():
    global _loader
    if _loader is None:
        try:
            _loader = RoadGraphLoader()
        except Exception as e:
            logger.error(f"Failed to initialize RoadGraphLoader: {e}")
            return None
    return _loader

def build_road_graph(hour: int, familiarity_map: Optional[Dict[str, float]] = None, **kwargs):
    """
    Build or retrieve the road graph, potentially with dynamic weights.
    """
    loader = get_loader()
    if not loader:
        return None, None, []
    
    # In a more advanced implementation, we would apply familiarity_map and hour
    # to the edge weights here.
    
    return loader.nx_graph, None, loader.junctions

def find_nearest_junction(G, lat: float, lng: float, junction_tree=None, junction_list=None):
    """
    Find the nearest junction node in the graph.
    """
    loader = get_loader()
    if not loader:
        return None
        
    result = loader.find_nearest_junction(lat, lng)
    if result:
        # result is ((lat, lng), junction_data)
        return result[0]
    return None

def get_all_edges() -> List[Dict]:
    """Get all edges for heatmap and other purposes."""
    loader = get_loader()
    return loader.edges if loader else []

def get_all_junctions() -> List[Dict]:
    """Get all junctions."""
    loader = get_loader()
    return loader.junctions if loader else []
