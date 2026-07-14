import numpy as np
from pydantic import BaseModel, ConfigDict
from scipy.optimize import least_squares

class CameraCalibration(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    intrinsics: np.ndarray
    extrinsics: np.ndarray
    image_width: int
    image_height: int

class FusionInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    segmented_cloud: np.ndarray
    rgb_edge_image: np.ndarray
    depth_image: np.ndarray
    calibration: CameraCalibration
    edge_weight: float = 0.5

from .fitting import variance_corrected_residual, canonical_cylinder_residual, get_axis_from_angles

def extract_3d_edges(edge_image: np.ndarray, depth_image: np.ndarray, calib: CameraCalibration) -> np.ndarray:
    """
    Backprojects the 2D edge pixels into 3D rays/points using the depth map and camera intrinsics.
    Returns: (M, 3) array of 3D edge constraint points.
    """
    v, u = np.nonzero(edge_image)
    z = depth_image[v, u]
    
    # Filter valid depths
    valid = (z > 0) & np.isfinite(z)
    u, v, z = u[valid], v[valid], z[valid]
    
    if len(z) == 0:
        return np.empty((0, 3))
        
    fx, fy = calib.intrinsics[0, 0], calib.intrinsics[1, 1]
    cx, cy = calib.intrinsics[0, 2], calib.intrinsics[1, 2]
    
    # Backproject to camera coordinates (OpenCV pinhole model)
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    
    pts_cam = np.column_stack((x, y, z))
    
    # Transform to world space using extrinsics (assume W2C mapping, so use inverse)
    c2w = np.linalg.inv(calib.extrinsics)
    ones = np.ones((pts_cam.shape[0], 1))
    pts_cam_homo = np.hstack((pts_cam, ones))
    
    pts_world = (c2w @ pts_cam_homo.T).T[:, :3]
    return pts_world

def edge_residual(params, edge_points):
    c = params[0:3]
    a = get_axis_from_angles(params[3], params[4])
    r = np.exp(params[5]) # using log_r
    
    if len(edge_points) == 0:
        return np.array([])
        
    v = edge_points - c
    dist = np.linalg.norm(np.cross(v, a), axis=1)
    return dist - r

def fit_cylinder_with_edges(input_data: FusionInput, initial_guess: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Executes a joint least-squares optimization.
    Residual function = depth_residual(points, params) + edge_weight * edge_residual(edge_points, params).
    """
    points = input_data.segmented_cloud
    edge_points = extract_3d_edges(input_data.rgb_edge_image, input_data.depth_image, input_data.calibration)
    
    # 1. Estimate initial variance using canonical fit on surface points
    res_canon = least_squares(canonical_cylinder_residual, initial_guess, args=(points,), method='lm')
    residuals_canon = canonical_cylinder_residual(res_canon.x, points)[:-1]
    fixed_variance = np.var(residuals_canon)
    
    init_var = np.copy(res_canon.x)
    if init_var[5] <= 0:
        init_var[5] = 1e-6
    init_var[5] = np.log(init_var[5])
    
    def joint_residual(params):
        r_depth = variance_corrected_residual(params, points, fixed_variance)
        r_edge = edge_residual(params, edge_points)
        if len(r_edge) > 0:
            return np.concatenate((r_depth, input_data.edge_weight * r_edge))
        return r_depth
        
    result = least_squares(joint_residual, init_var, method='lm')
    result.x[5] = np.exp(result.x[5])
    
    diagnostics = {
        'status': result.status,
        'message': result.message,
        'nfev': result.nfev,
        'cost': result.cost,
        'converged': result.status > 0
    }
    return result.x, diagnostics
