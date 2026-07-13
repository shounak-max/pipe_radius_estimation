from typing import List, Optional
from pydantic import BaseModel, Field

class PipeGroundTruth(BaseModel):
    pipe_id: str = Field(..., description="Unique identifier for the physical pipe")
    material: str = Field(..., description="Material of the pipe (e.g., steel, PVC)")
    surface_finish: str = Field(..., description="Surface finish (e.g., glossy, rusted)")
    nominal_diameter_mm: float = Field(..., description="Nominal diameter in mm")
    measured_radius_mm: float = Field(..., description="Physically measured radius in mm")
    radius_uncertainty_mm: float = Field(..., description="Measurement standard deviation")
    measurement_method: str = Field(..., description="CMM, Total Station, Caliper, etc.")
    calibration_cert_ref: str = Field(..., description="Reference to the tool's calibration certificate")

class ScanManifest(BaseModel):
    scan_id: str = Field(..., description="Unique identifier for the scan")
    scene_id: str = Field(..., description="Identifier for the scene/environment")
    site_id: str = Field(..., description="Identifier for the facility or location")
    sensor_id: str = Field(..., description="Identifier for the specific sensor device")
    operator_id: str = Field(..., description="Operator collecting the data")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    
    pcd_path: str = Field(..., description="Path to raw point cloud")
    rgb_path: Optional[str] = Field(None, description="Path to raw RGB image, if available")
    depth_path: Optional[str] = Field(None, description="Path to raw depth image, if available")
    
    standoff_range_m: float = Field(..., description="Standoff distance in meters")
    incidence_angle_deg: float = Field(..., description="Approximate incidence angle in degrees")
    measured_visible_circumference_pct: float = Field(..., description="Measured visible circumference (0-100%)")
    
    ambient_temperature_c: float = Field(..., description="Ambient temperature in Celsius")
    lighting_condition: str = Field(..., description="Notes on lighting (e.g., indoor fluorescent)")
    
    pipe_inventory: List[str] = Field(..., description="List of pipe_ids present in the scan")

class ProcessingConfiguration(BaseModel):
    config_id: str = Field(..., description="Unique identifier for this processing run configuration")
    segmentation_method: str = Field(..., description="Algorithm used for pipe segmentation (e.g., RANSAC, RandLA-Net)")
    fitting_residual_type: str = Field(..., description="canonical, variance_corrected, or ru_epd")
    edge_fusion_enabled: bool = Field(..., description="Whether RGB-D edge fusion is enabled")
    topology_recovery_enabled: bool = Field(..., description="Whether adaptive centerline and topology recovery is enabled")
    inlier_threshold: float = Field(..., description="Inlier threshold for fitting in meters")
    max_iterations: int = Field(..., description="Max iterations for non-linear optimization")
