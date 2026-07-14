import pytest
import os
import json
import numpy as np

# We'll use imageio to read EXR for the test, but since it's just a test, we can mock it
# if imageio with freeimage plugin isn't installed. Let's actually test with a dummy 
# edge image and the real depth map if possible.
try:
    import imageio.v3 as iio
    HAS_IMAGEIO = True
except ImportError:
    HAS_IMAGEIO = False

from pipe_estimation.fusion import extract_3d_edges, fit_cylinder_with_edges, CameraCalibration, FusionInput

def test_fusion_extract_3d_edges_math_check():
    fixture_dir = os.path.join(os.path.dirname(__file__), "..", "PipeGenBench", "output", "test", "Scene_00001")
    if not os.path.exists(fixture_dir):
        pytest.skip("Fixture missing")
        
    calib_path = os.path.join(fixture_dir, "calibration.json")
    with open(calib_path, 'r') as f:
        calib_data = json.load(f)
        
    calib = CameraCalibration(
        intrinsics=np.array(calib_data["intrinsics"]),
        extrinsics=np.array(calib_data["extrinsics"]),
        image_width=calib_data["image_width"],
        image_height=calib_data["image_height"]
    )
    
    # Create a synthetic edge image (e.g. center pixel)
    edge_image = np.zeros((1080, 1920), dtype=np.uint8)
    edge_image[540, 960] = 255
    
    # We create a dummy depth image with exactly 5.0 meters depth at the center
    depth_image = np.zeros((1080, 1920), dtype=np.float32)
    depth_image[540, 960] = 5.0
    
    pts_world = extract_3d_edges(edge_image, depth_image, calib)
    
    assert pts_world.shape == (1, 3)
    
    # Ensure that it did some valid transform (not all zeros)
    assert not np.all(pts_world == 0)

def test_fit_cylinder_with_edges():
    # Provide synthetic points and edge points
    points = np.random.randn(100, 3) * 0.1 + np.array([0, 0, 5])
    calib = CameraCalibration(intrinsics=np.eye(3), extrinsics=np.eye(4), image_width=100, image_height=100)
    
    # Dummy fusion input
    input_data = FusionInput(
        segmented_cloud=points,
        rgb_edge_image=np.zeros((100, 100)),
        depth_image=np.zeros((100, 100)),
        calibration=calib,
        edge_weight=0.5
    )
    
    initial_guess = np.array([0, 0, 5, 0, 0, 0.5])
    params, diag = fit_cylinder_with_edges(input_data, initial_guess)
    
    assert diag["converged"]
    assert len(params) == 6
