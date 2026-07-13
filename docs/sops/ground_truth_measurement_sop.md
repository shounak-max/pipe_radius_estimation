# Ground-Truth Measurement Standard Operating Procedure (SOP)

## 1. Objective
To physically measure the ground-truth parameters (radius, diameter, axis, and topology) of the pipe segments used in the benchmark, ensuring that ground truth is obtained from certified methods and not from point cloud fitting.

## 2. Acceptable Measurement Instruments
- Coordinate Measuring Machine (CMM)
- Portable Measurement Arm (e.g., FARO Arm)
- Total Station / Laser Tracker
- Digital Calipers (only for small pipes, $r < 100$ mm)
- Manufacturer Certification (must have a documented certificate)

## 3. Measurement Protocol for Straight Pipes
1. **Identification**: Mark each physical pipe segment with a unique `pipe_id` label.
2. **Diameter Measurement**:
   - Take at least 6 diameter measurements at different angles and lengths along the pipe using digital calipers or CMM.
   - Calculate the mean measured diameter and radius.
   - Record the standard deviation as the measurement uncertainty.
3. **Axis Measurement**:
   - For total station or CMM, measure at least 10 points along the physical surface to determine the precise central axis vector.
4. **Surface and Material Notes**:
   - Record the material (e.g., PVC, Steel, Concrete) and surface finish (e.g., matte, glossy, rusted).

## 4. Measurement Protocol for Complex Shapes (Corrugated, Elbows, Tees)
1. **Corrugated Pipes**: Measure the inner diameter, outer crest diameter, and the pitch (distance between crests).
2. **Elbows**: Measure the straight segment radii, the bend angle, and the bend radius (centerline radius of the bend).
3. **Topology**: For connected segments, measure the exact physical location of the joints/flanges in the reference coordinate system.

## 5. Documentation
- Log all values in the Ground-Truth Manifest (JSON/CSV).
- Include the calibration certificate reference of the measurement tool used.
- Include date, operator name, and any anomalies (e.g., visible dents).
