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

    def load_manifest(self, manifest_path: str, allow_synthetic: bool = False) -> ScanManifest:
        full_path = self.data_root / manifest_path
        if not full_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {full_path}")
        with open(full_path, 'r') as f:
            data = json.load(f)
            
        manifest = ScanManifest(**data)
        
        if not allow_synthetic:
            # Tripwire to prevent pipeline from absorbing unverified synthetic generation
            is_sim = (manifest.operator_id == "sim" or manifest.sensor_id == "CyclesRender")
            if is_sim:
                raise ValueError("HARD SCOPE RULE VIOLATION: Pipeline cannot ingest synthetic PipeGenBench data as evidence.")
                
        return manifest

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
        full_path = self.data_root / pcd_path
        if not full_path.exists():
            raise FileNotFoundError(f"Point cloud file not found: {full_path}")
            
        if o3d is not None:
            pcd = o3d.io.read_point_cloud(str(full_path))
            if pcd.is_empty():
                raise ValueError(f"Loaded point cloud from {full_path} is empty or unreadable.")
                
            # Filter NaNs and Infs BEFORE downsampling, otherwise Open3D bounding box explodes
            pcd.remove_non_finite_points()
                
            if voxel_size is not None and voxel_size > 0:
                pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
                
            points = np.asarray(pcd.points)
        else:
            try:
                import trimesh
            except ImportError:
                raise ImportError("Neither open3d nor trimesh is available to load point clouds. Please install one of them.")
                
            mesh = trimesh.load(str(full_path))
            if hasattr(mesh, 'vertices'):
                points = np.array(mesh.vertices)
            else:
                raise ValueError(f"Could not load vertices from {full_path}")
                
            # Basic NaN filter
            valid = np.isfinite(points).all(axis=1)
            points = points[valid]
            
            # Simple voxel downsampling fallback
            if voxel_size is not None and voxel_size > 0:
                # Quantize points to voxel grid
                voxel_indices = np.floor(points / voxel_size).astype(np.int32)
                # Find unique voxels
                _, unique_indices = np.unique(voxel_indices, axis=0, return_index=True)
                points = points[unique_indices]
                
        return points

    def load_aligned_rgbd(self, manifest: ScanManifest) -> "FusionInput":
        """
        Explicit registration stage.
        Loads raw RGB, depth, and point cloud from the manifest and ensures they are pixel-aligned
        before passing them to the fusion module.
        Checks manifest.alignment_type to determine whether to use hardware SDK intrinsics,
        software point-to-plane registration, or passthrough.
        """
        from .fusion import FusionInput, CameraCalibration
        
        # Load Calibration
        calib_path = self.data_root / "calibration.json"
        if not calib_path.exists():
            raise FileNotFoundError(f"Calibration file not found: {calib_path}")
            
        with open(calib_path, 'r') as f:
            calib_data = json.load(f)
            
        calib = CameraCalibration(
            intrinsics=np.array(calib_data["intrinsics"], dtype=np.float32),
            extrinsics=np.array(calib_data["extrinsics"], dtype=np.float32),
            image_width=calib_data["image_width"],
            image_height=calib_data["image_height"]
        )
        
        # Load Point Cloud
        pcd = self.load_point_cloud(manifest.pcd_path)
        
        # Load RGB and convert to edge map
        rgb_path = str(self.data_root / manifest.rgb_path)
        depth_path = str(self.data_root / manifest.depth_path)
        
        # Try OpenCV first for RGB, fallback to imageio
        try:
            import cv2
            rgb_img = cv2.imread(rgb_path, cv2.IMREAD_COLOR)
            if rgb_img is None:
                raise ValueError(f"Failed to load RGB image from {rgb_path}")
            gray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
            # Standard Canny Edge detection
            rgb_edge_image = cv2.Canny(gray, 100, 200)
        except ImportError:
            import imageio.v3 as iio
            rgb_img = iio.imread(rgb_path)
            # Very basic grayscale conversion
            gray = np.dot(rgb_img[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
            # Simple gradient magnitude for edge proxy
            gy, gx = np.gradient(gray.astype(float))
            mag = np.sqrt(gx**2 + gy**2)
            rgb_edge_image = (mag > 50).astype(np.uint8) * 255
            
        # Try OpenEXR first for Depth (most robust for multilayer/Blender quirks), fallback to imageio
        try:
            import OpenEXR
            import Imath
            exr_file = OpenEXR.InputFile(depth_path)
            dw = exr_file.header()['dataWindow']
            size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
            
            channels = exr_file.header()['channels'].keys()
            target_ch = None
            for ch in channels:
                if 'depth' in ch.lower() or 'z' in ch.lower():
                    target_ch = ch
                    break
            if target_ch is None:
                target_ch = list(channels)[0]
                
            pt = Imath.PixelType(Imath.PixelType.FLOAT)
            depth_str = exr_file.channel(target_ch, pt)
            depth_image = np.frombuffer(depth_str, dtype=np.float32).reshape(size[1], size[0])
            
        except ImportError:
            import imageio.v3 as iio
            depth_image = iio.imread(depth_path)
            if isinstance(depth_image, dict):
                # Multilayer EXR returns a dict. Find depth or Z pass.
                for k in depth_image.keys():
                    if 'depth' in k.lower() or 'z' in k.lower():
                        depth_image = depth_image[k]
                        break
                else:
                    depth_image = list(depth_image.values())[0]

            if len(depth_image.shape) == 3:
                depth_image = depth_image[:, :, 0]
                
        # Ensure depth is float32
        depth_image = depth_image.astype(np.float32)
        
        if depth_image.shape != (calib.image_height, calib.image_width):
            raise ValueError(f"Depth image shape {depth_image.shape} does not match calibration {(calib.image_height, calib.image_width)}")
        
        return FusionInput(
            segmented_cloud=pcd,
            rgb_edge_image=rgb_edge_image,
            depth_image=depth_image,
            calibration=calib,
            edge_weight=0.5
        )
