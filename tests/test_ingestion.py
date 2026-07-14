import pytest
import os
import numpy as np
from pipe_estimation.ingestion import DataIngestor
from pipe_estimation.run_experiments import assert_physical_provenance

def test_ingestion_loads_blender_fixture():
    fixture_dir = os.path.join(os.path.dirname(__file__), "..", "PipeGenBench", "output", "test", "Scene_00001")
    
    if not os.path.exists(fixture_dir):
        pytest.skip(f"Fixture directory {fixture_dir} not found. Run PipeGenBench first.")
        
    ingestor = DataIngestor(fixture_dir)
    
    manifest = ingestor.load_manifest("manifest.json")
    assert manifest.sensor_id == "CyclesRender"
    assert manifest.operator_id == "sim"
    assert manifest.scene_id == "synthetic_benchmark"
    
    # Ensure the tripwire guard works on this manifest
    with pytest.raises(ValueError, match="HARD SCOPE RULE VIOLATION"):
        assert_physical_provenance(manifest)
        
    # Mock point cloud loading since open3d might not be installed in the test environment
    import unittest.mock
    with unittest.mock.patch.object(ingestor, 'load_point_cloud', return_value=np.random.randn(100, 3)):
        pcd = ingestor.load_point_cloud("pointcloud.ply")
        assert pcd.shape[0] > 0
        assert pcd.shape[1] == 3
        
        # Test load_aligned_rgbd
        fusion_input = ingestor.load_aligned_rgbd(manifest)
        assert fusion_input.segmented_cloud.shape == pcd.shape
        assert fusion_input.calibration.image_width == 1920
