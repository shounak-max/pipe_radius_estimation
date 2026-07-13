# Sensor Calibration and Ingestion Standard Operating Procedure (SOP)

## 1. Objective
To ensure that all sensor data collected for the Pipe Radius Estimation benchmark is accurately calibrated, normalized, and repeatable across different sensors and environments. No synthetic noise injection is permitted; all data must be physically captured.

## 2. Sensor Warm-up and Pre-scan Routine
1. **Power On**: Turn on the sensor (LiDAR, Kinect, Azure Kinect, or stereo/RGB-D camera).
2. **Warm-up Period**: Allow the sensor to run for at least 30 minutes before capturing data to ensure thermal stability of the depth measurements.
3. **Firmware/Software Verification**: Record the exact firmware version and software SDK version used for capture in the scan manifest.
4. **Environment Check**: Ensure the scanning environment is stable (no changing sunlight patterns if indoors, controlled lighting if applicable). Record ambient temperature and lighting conditions.

## 3. Calibration
1. **Intrinsic Calibration**:
   - For RGB-D sensors, run the standard checkerboard intrinsic calibration if the factory calibration is known to drift, or extract the factory intrinsics.
   - Save the intrinsic matrix ($3 \times 3$), distortion coefficients, and image dimensions.
2. **Extrinsic Calibration (if multi-sensor or registered)**:
   - If using multiple sensors or aligning to a fixed coordinate system, use a calibrated physical reference object (e.g., a known sphere or checkerboard).
   - Compute and save the $4 \times 4$ rigid transformation matrix from the sensor frame to the world/reference frame.

## 4. Scan Acquisition Protocol
1. **Positioning**: Place the sensor at the designated standoff distance and incidence angle.
2. **Settings**: Lock all auto-exposure, auto-white-balance, and gain settings. Record these settings in the scan manifest.
3. **Capture**: Trigger the scan physically. For repeated captures, slightly reposition the sensor within a controlled tolerance (e.g., $\pm 2$ cm translation, $\pm 1$ degree rotation) and re-trigger.
4. **Data Saving**: Save raw point clouds (PCD/PLY), raw depth frames, and raw RGB frames. Name files using the convention `[sensor_id]_[scene_id]_[timestamp]`.

## 5. Post-Capture
- Immediately verify that the point cloud is not corrupted and covers the intended field of view.
- Fill out the `operator_log_template.md` and update the scan manifest schema.
