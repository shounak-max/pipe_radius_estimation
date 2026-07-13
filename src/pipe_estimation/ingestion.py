import json
from pathlib import Path
from typing import List
from .schemas import ScanManifest, PipeGroundTruth

class DataIngestor:
    def __init__(self, data_root: str):
        self.data_root = Path(data_root)

    def load_manifest(self, manifest_path: str) -> ScanManifest:
        with open(self.data_root / manifest_path, 'r') as f:
            data = json.load(f)
        return ScanManifest(**data)

    def load_ground_truth(self, gt_path: str) -> List[PipeGroundTruth]:
        with open(self.data_root / gt_path, 'r') as f:
            data = json.load(f)
        return [PipeGroundTruth(**item) for item in data]

    def load_point_cloud(self, pcd_path: str):
        # Stub for loading point cloud (e.g. using open3d)
        # import open3d as o3d
        # return o3d.io.read_point_cloud(str(self.data_root / pcd_path))
        pass
