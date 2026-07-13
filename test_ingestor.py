import sys
import os
sys.path.insert(0, os.path.abspath('src'))
import numpy as np
import open3d as o3d
from pipe_estimation.ingestion import DataIngestor

def test_ingestion():
    # 1. Create a dummy PLY file in the data directory
    dummy_points = np.random.rand(100, 3)
    # Inject some NaNs to test filtering
    dummy_points[10] = [np.nan, 1.0, 2.0]
    dummy_points[20] = [np.inf, 1.0, 2.0]
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(dummy_points)
    
    dummy_path = os.path.join('data', 'dummy.ply')
    o3d.io.write_point_cloud(dummy_path, pcd)
    print(f"Created dummy point cloud at {dummy_path}")
    
    # 2. Test DataIngestor
    ingestor = DataIngestor(data_root="data")
    
    print("\nTesting Manifest Loading...")
    manifest = ingestor.load_manifest("manifest.json")
    print(f"Loaded manifest: {manifest.scan_id}")
    
    print("\nTesting Ground Truth Loading...")
    gts = ingestor.load_ground_truth("ground_truth.json")
    print(f"Loaded ground truth for {len(gts)} pipes. First pipe: {gts[0].pipe_id}")
    
    print("\nTesting Point Cloud Loading (with NaN filtering and voxel downsampling)...")
    clean_points = ingestor.load_point_cloud("dummy.ply", voxel_size=0.0) # no downsampling first
    print(f"Loaded {len(clean_points)} valid points out of 100 original (Expected: 98).")
    assert len(clean_points) == 98, "NaN filtering failed!"
    
    downsampled_points = ingestor.load_point_cloud("dummy.ply", voxel_size=0.5)
    print(f"Loaded {len(downsampled_points)} points after 0.5m voxel downsampling.")
    
    print("\nAll Ingestion tests passed!")
    
if __name__ == "__main__":
    test_ingestion()
