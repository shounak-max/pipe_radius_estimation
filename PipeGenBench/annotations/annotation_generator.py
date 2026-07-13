import json
import os

class AnnotationGenerator:
    def __init__(self, config):
        self.config = config
        
    def generate_metadata(self, scan_id, pipes_data, calibration, output_dir):
        manifest = {
            "scan_id": scan_id,
            "scene_id": "synthetic_benchmark",
            "site_id": "PipeGenBench",
            "sensor_id": "CyclesRender",
            "operator_id": "sim",
            "timestamp": "2026-07-14T00:00:00Z",
            "pcd_path": "pointcloud.ply",
            "rgb_path": "rgb.png",
            "depth_path": "depth.exr",
            "standoff_range_m": 2.5,
            "incidence_angle_deg": 0.0,
            "measured_visible_circumference_pct": 50.0, # Approximate for now
            "ambient_temperature_c": 20.0,
            "lighting_condition": "randomized",
            "pipe_inventory": [p["name"] for p in pipes_data],
            "alignment_type": "hardware_sdk"
        }
        
        with open(os.path.join(output_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=4)
            
        with open(os.path.join(output_dir, "calibration.json"), "w") as f:
            json.dump(calibration, f, indent=4)
            
        # Ground truth specifics
        with open(os.path.join(output_dir, "metadata.json"), "w") as f:
            json.dump({"pipes": pipes_data}, f, indent=4)
