import json
from pathlib import Path

DATA_DIR = Path("data")
COMPLETE_FILE = DATA_DIR / "gachibowli_complete.json"

def split_complete_json():
    print(f"Reading {COMPLETE_FILE}...")
    with open(COMPLETE_FILE, 'r') as f:
        data = json.load(f)
    
    junctions = data.get("junctions", [])
    edges = data.get("edges", [])
    
    print(f"Extracted {len(junctions)} junctions and {len(edges)} edges.")
    
    junctions_file = DATA_DIR / "gachibowli_junctions.json"
    with open(junctions_file, 'w') as f:
        json.dump(junctions, f, indent=2)
    print(f"Saved to {junctions_file}")
    
    edges_file = DATA_DIR / "gachibowli_edges.json"
    with open(edges_file, 'w') as f:
        json.dump(edges, f, indent=2)
    print(f"Saved to {edges_file}")
    
    # Create simplified road graph JSON
    # Format: { "nodes": [{id, lat, lng}, ...], "edges": [{from, to, distance, safety_score}, ...] }
    nodes = []
    for j in junctions:
        nodes.append({
            "id": j["junction_id"],
            "lat": j["latitude"],
            "lng": j["longitude"]
        })
    
    graph_edges = []
    for e in edges:
        graph_edges.append({
            "from": e["start_junction_id"],
            "to": e["end_junction_id"],
            "distance": e["length_meters"],
            "safety_score": 100 - (e.get("crime_density", 0.5) * 100) # Simple fallback
        })
    
    graph_data = {
        "nodes": nodes,
        "edges": graph_edges
    }
    
    graph_file = DATA_DIR / "gachibowli_road_graph.json"
    with open(graph_file, 'w') as f:
        json.dump(graph_data, f, indent=2)
    print(f"Saved to {graph_file}")

if __name__ == "__main__":
    split_complete_json()
