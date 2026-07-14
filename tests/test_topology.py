import pytest
import numpy as np
import os
import json
from pipe_estimation.topology import build_topology_graph, PipeSegment, extract_adaptive_centerline

def test_topology_recovers_known_t_junction():
    fixture_dir = os.path.join(os.path.dirname(__file__), "..", "PipeGenBench", "output", "test", "Scene_00001")
    if not os.path.exists(fixture_dir):
        pytest.skip("Fixture missing")
        
    topo_path = os.path.join(fixture_dir, "topology.json")
    with open(topo_path, 'r') as f:
        ground_truth_topo = json.load(f)
        
    # Read the ground truth junction point from metadata or topology
    gt_nodes = ground_truth_topo.get("nodes", [])
    if len(gt_nodes) == 0:
        pytest.skip("No T-junctions in fixture scene to test against")
        
    gt_center = np.array(gt_nodes[0]["center_coordinate"])
    
    # Load real point cloud using trimesh
    try:
        import trimesh
        mesh = trimesh.load(os.path.join(fixture_dir, "pointcloud.ply"))
        points = np.array(mesh.vertices)
    except Exception:
        pytest.skip("Could not load pointcloud.ply")
        
    # Extract segments using the ground truth edges
    edges_gt = ground_truth_topo.get("edges", [])
    if len(edges_gt) < 2:
        pytest.skip("Not enough edges in ground truth to test topology")
        
    axis1 = np.array(edges_gt[0]["pipe_axis"])
    axis2 = np.array(edges_gt[1]["pipe_axis"])
    
    # Filter points that form a tight cylinder along axis1
    v1 = points - gt_center
    dist_to_axis1 = np.linalg.norm(np.cross(v1, axis1), axis=1)
    pts1 = points[dist_to_axis1 < 0.3]
    
    # Filter points that form a tight cylinder along axis2
    v2 = points - gt_center
    dist_to_axis2 = np.linalg.norm(np.cross(v2, axis2), axis=1)
    pts2 = points[dist_to_axis2 < 0.3]
    
    if len(pts1) < 10 or len(pts2) < 10:
        pytest.skip("Could not extract enough points along ground truth axes")
        
    seg1 = PipeSegment(segment_id="pipe_1", points=pts1)
    seg2 = PipeSegment(segment_id="pipe_2", points=pts2)
    
    nodes, edges = build_topology_graph([seg1, seg2], distance_threshold=10.0, angle_threshold=np.radians(45))
    
    assert len(nodes) >= 1
    assert nodes[0].node_type == "t_junction"
    
    dist = np.linalg.norm(nodes[0].center_coordinate - gt_center)
    assert dist < 1.0 # The recovered junction should be extremely close
