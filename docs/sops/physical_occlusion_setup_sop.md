# Physical Occlusion Setup Standard Operating Procedure (SOP)

## 1. Objective
To physically control and measure occlusion in pipe scans for Experiment 2, quantifying how parameter estimation degrades as visible pipe surface decreases. No computational cropping or synthetic masking is allowed.

## 2. Occlusion Materials
- Opaque panels (wood, plastic, or cardboard)
- Standard rebar cages
- Natural clutter (soil, tools, other pipes)
- Adjustable mounts to hold occluders at fixed distances from the pipe

## 3. Setup Protocol
1. **Unoccluded Baseline**: Scan the physical pipe with 0% intended occlusion from the designated sensor positions.
2. **Placing Occluders**:
   - Place physical occluders between the sensor and the pipe.
   - Adjust the position to achieve the target visible circumference levels: ~90%, ~70%, ~50%, ~30%, and ~15%.
   - Ensure the occluder itself does not move the pipe.
3. **Capture**: Scan the scene using the standard Sensor Calibration SOP.
4. **Recording Real Coverage**:
   - Do not rely on visual estimation during setup.
   - After capture, compare the unoccluded baseline point cloud to the occluded point cloud to calculate the exact percentage of visible pipe arc. Record this in the manifest.

## 4. Failure Modes and Safety
- If the occluder casts shadows that interfere with RGB-D sensing in a way that breaks tracking entirely, log this as an extreme occlusion failure.
- Ensure all mounts are stable so they do not shift during repeated captures.
