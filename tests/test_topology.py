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
    
    # Create two synthetic segments that intersect at that junction
    # We will simulate a point cloud for each segment
    
    # Segment 1: along X axis intersecting gt_center
    pts1 = []
    for x in np.linspace(-50, 50, 100):
        pts1.append(gt_center + np.array([x, 0, 0]))
    seg1 = PipeSegment(segment_id="pipe_1", points=np.array(pts1))
    
    # Segment 2: along Y axis intersecting gt_center
    pts2 = []
    for y in np.linspace(0, 50, 100):
        pts2.append(gt_center + np.array([0, y, 0]))
    seg2 = PipeSegment(segment_id="pipe_2", points=np.array(pts2))
    
    nodes, edges = build_topology_graph([seg1, seg2], distance_threshold=5.0, angle_threshold=np.radians(10))
    
    assert len(nodes) == 1
    assert nodes[0].node_type == "t_junction"
    
    dist = np.linalg.norm(nodes[0].center_coordinate - gt_center)
    assert dist < 1.0 # The recovered junction should be extremely close
