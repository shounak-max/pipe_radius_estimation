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

def extract_3d_edges(edge_image: np.ndarray, depth_image: np.ndarray, calib: CameraCalibration) -> np.ndarray:
    """
    Backprojects the 2D edge pixels into 3D rays/points using the depth map and camera intrinsics.
    Returns: (M, 3) array of 3D edge constraint points.
    """
    # Stub: To be implemented in the next phase
    return np.array([])

def fit_cylinder_with_edges(input_data: FusionInput, initial_guess: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    Executes a joint least-squares optimization.
    Residual function = depth_residual(points, params) + edge_weight * edge_residual(edge_points, params).
    Returns: 
        - Optimized params: [cx, cy, cz, theta, phi, r]
        - Diagnostics dict (condition number, convergence status, etc.)
    """
    # Stub: To be implemented in the next phase
    return initial_guess, {"converged": True, "cost": 0.0}
