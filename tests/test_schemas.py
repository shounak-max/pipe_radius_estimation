import unittest
from pipe_estimation.schemas import PipeGroundTruth, ScanManifest

class TestSchemas(unittest.TestCase):
    def test_pipe_ground_truth(self):
        gt = PipeGroundTruth(
            pipe_id="pipe_01",
            material="steel",
            surface_finish="glossy",
            nominal_diameter_mm=200.0,
            measured_radius_mm=100.5,
            radius_uncertainty_mm=0.2,
            measurement_method="CMM",
            calibration_cert_ref="CERT-12345"
        )
        self.assertEqual(gt.pipe_id, "pipe_01")
        self.assertEqual(gt.measured_radius_mm, 100.5)

    def test_scan_manifest(self):
        manifest = ScanManifest(
            scan_id="scan_001",
            scene_id="scene_lab_01",
            site_id="lab_01",
            sensor_id="kinect_v2_01",
            operator_id="operator_1",
            timestamp="2026-07-12T10:00:00Z",
            pcd_path="data/scan_001.ply",
            standoff_range_m=1.5,
            incidence_angle_deg=0.0,
            measured_visible_circumference_pct=100.0,
            ambient_temperature_c=22.5,
            lighting_condition="indoor fluorescent",
            pipe_inventory=["pipe_01", "pipe_02"]
        )
        self.assertEqual(manifest.scan_id, "scan_001")
        self.assertEqual(len(manifest.pipe_inventory), 2)

if __name__ == '__main__':
    unittest.main()
