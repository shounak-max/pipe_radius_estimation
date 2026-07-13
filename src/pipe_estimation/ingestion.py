import json
from pathlib import Path
from typing import List, Optional
import numpy as np
try:
    import open3d as o3d
except ImportError:
    o3d = None

from .schemas import ScanManifest, PipeGroundTruth

class DataIngestor:
    def __init__(self, data_root: str):
        self.data_root = Path(data_root)
        if not self.data_root.exists():
            raise FileNotFoundError(f"Data root directory not found: {self.data_root}")

    def load_manifest(self, manifest_path: str) -> ScanManifest:
        full_path = self.data_root / manifest_path
        if not full_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {full_path}")
        with open(full_path, 'r') as f:
            data = json.load(f)
        return ScanManifest(**data)

    def load_ground_truth(self, gt_path: str) -> List[PipeGroundTruth]:
        full_path = self.data_root / gt_path
        if not full_path.exists():
            raise FileNotFoundError(f"Ground truth file not found: {full_path}")
        with open(full_path, 'r') as f:
            data = json.load(f)
        return [PipeGroundTruth(**item) for item in data]

    def load_point_cloud(self, pcd_path: str, voxel_size: Optional[float] = None) -> np.ndarray:
        """
        Loads a point cloud file (.ply, .pcd) and returns it as a clean numpy array.
        Filters out any NaN or Inf coordinates that often come from raw depth sensors.
        Optionally applies voxel downsampling.
        """
        if o3d is None:
            raise ImportError("open3d is required to load point clouds. Please install it.")
            
        full_path = self.data_root / pcd_path
        if not full_path.exists():
            raise FileNotFoundError(f"Point cloud file not found: {full_path}")
            
        pcd = o3d.io.read_point_cloud(str(full_path))
        if pcd.is_empty():
            raise ValueError(f"Loaded point cloud from {full_path} is empty or unreadable.")
            
        # Filter NaNs and Infs BEFORE downsampling, otherwise Open3D bounding box explodes
        pcd.remove_non_finite_points()
            
        if voxel_size is not None and voxel_size > 0:
            pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
            
        points = np.asarray(pcd.points)
        return points
