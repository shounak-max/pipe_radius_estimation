import pytest
import os
import numpy as np
from pipe_estimation.ingestion import DataIngestor

def test_ingestion_loads_blender_fixture():
    fixture_dir = os.path.join(os.path.dirname(__file__), "..", "PipeGenBench", "output", "test", "Scene_00001")
    
    if not os.path.exists(fixture_dir):
        pytest.skip(f"Fixture directory {fixture_dir} not found. Run PipeGenBench first.")
        
    ingestor = DataIngestor(fixture_dir)
    
    # Test that load_manifest blocks synthetic generation by default
    with pytest.raises(ValueError, match="HARD SCOPE RULE VIOLATION"):
        ingestor.load_manifest("manifest.json")
        
    # Now load properly for further tests
    manifest = ingestor.load_manifest("manifest.json", allow_synthetic=True)
    assert manifest.sensor_id == "CyclesRender"
    assert manifest.operator_id == "sim"
    assert manifest.scene_id == "synthetic_benchmark"
    
    # Load real point cloud using trimesh fallback
    pcd = ingestor.load_point_cloud("pointcloud.ply")
    assert pcd.shape[0] > 0
    assert pcd.shape[1] == 3
    
    # Test load_aligned_rgbd
    fusion_input = ingestor.load_aligned_rgbd(manifest)
    assert fusion_input.segmented_cloud.shape == pcd.shape
    assert fusion_input.calibration.image_width == 1920
