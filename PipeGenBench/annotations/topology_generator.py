import json
import os

class TopologyGenerator:
    def __init__(self, config):
        self.config = config
        
    def generate_topology(self, pipes_data, output_dir):
        # Build a simple logical graph
        nodes = []
        edges = []
        
        # We assume SceneGenerator creates a simple T-junction for now
        # Ideally, we would geometrically intersect pipes to find junctions
        
        # Mock Topology for the dataset
        if len(pipes_data) >= 2:
            nodes.append({
                "node_id": "Junction_1",
                "node_type": "t_junction",
                "center_coordinate": pipes_data[1]["center"]
            })
            
            edges.append({
                "edge_id": "Edge_1",
                "source_node": "Junction_1",
                "target_node": pipes_data[0]["name"],
                "pipe_radius": pipes_data[0]["radius"],
                "pipe_axis": pipes_data[0]["axis"]
            })
            edges.append({
                "edge_id": "Edge_2",
                "source_node": "Junction_1",
                "target_node": pipes_data[1]["name"],
                "pipe_radius": pipes_data[1]["radius"],
                "pipe_axis": pipes_data[1]["axis"]
            })
            
        topology = {
            "nodes": nodes,
            "edges": edges
        }
        
        with open(os.path.join(output_dir, "topology.json"), "w") as f:
            json.dump(topology, f, indent=4)
