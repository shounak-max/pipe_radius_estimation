# Closing the Gaps in Point-Cloud-Based Pipe Parameter Estimation
### Evidence-Grounded Four-Experiment Research Program

**Status:** Revised planning document, reviewed against the eight PDFs in `references/` on 2026-07-12. The program is ready for pilot data collection, but the power calculations remain planning estimates until pilot variance is measured.

**Global constraint: no synthetic point clouds in this research program.** Every experiment below uses physically collected sensor data and physically measured ground truth. Noise, occlusion, missing data, lighting variation, reflectance effects, viewpoint changes, and cross-sensor variation are created by real acquisition conditions, physical fixtures, real occluders, and repeated scans. Simulation-only or synthetic-dataset papers are used only as background or method inspiration, not as evidence that the proposed protocol has already been validated.

---

## 0. Evidence Review and Research Gaps

### 0.1 Evidence tiers from the reference PDFs

| ID | Reference PDF | Evidence usable for this program | Main limitation that leaves a gap |
|---|---|---|---|
| R1 | `1-s2.0-S0926580517301243-am.pdf` - Pipe radius estimation using Kinect range cameras | Physical Kinect 1, Kinect 2, and FARO scans of four certified pipe radii across standoff distances. Reported average radius errors of about 18% for Kinect 1, 10% for Kinect 2, and 2% for the laser scanner. | Small pipe set, limited environments, limited bias/variance separation, and no modern RGB-D/LiDAR transfer benchmark. |
| R2 | `applsci-15-02105-v2.pdf` - RU-EPD for robot pose and pipe diameter using ToF sensors | Shows why a canonical ellipse residual can overestimate pipe diameter under random depth errors, and validates a symmetric error residual on a real 20 inch prototype pipeline. In the real experiment, RU-EPD reduced mean-diameter bias from about 4.2 mm to at most 0.46 mm and reduced error range substantially. | Large parts of the evidence are simulation-based, the real validation uses an in-pipe ToF setup, and elbows/T-junctions remain future work. |
| R3 | `remotesensing-17-00341.pdf` - Underground pipeline reconstruction from LiDAR point clouds | Real Hong Kong underground LiDAR scenes, RandLA-Net segmentation, adaptive RANSAC centerline generation, topological reconstruction, 88.8% recall, 96.2% precision, mean point-to-model deviation of 3.79 cm, and mean relative radius errors below 3%. | Data are not a standardized public cross-sensor benchmark, segmentation can degrade in complex scenes, and valves/manholes are not handled. |
| R4 | `sensors-25-02641.pdf` - Corrugated pipe recognition and measurement using RGB-D and deep learning | Physical RGB-D capture in a controlled precast-factory mockup, registration, RandLA-Net segmentation, slice center extraction, and BP-network centerline fitting. Average measurement errors were 2.2 mm, 1.4 mm, and 1.6 mm for three corrugated pipes. | Controlled indoor setting only; future work calls for broader weather, lighting, occlusion, and incomplete-data robustness. |
| R5 | `sensors-26-01687-v2 (1).pdf` - Edge-point cloud fusion for cylinder fitting using single-view RGB-D data | Real RGB-D data for cylinders with radii 20-60 mm, controlled viewpoints, repeat captures, RANSAC initialization, point-plus-edge fusion, and improved radius/axis robustness over point-only baselines. | Uses manual cylinder/edge annotations, fixed edge-fusion weight, synthetic edge perturbation for one sensitivity analysis, limited heavy-occlusion testing, and assumes ideal cylinders. |
| R6 | `2108.05836v1.pdf` - AdaFit normal estimation | Useful pretrained normal-estimation candidate; reports improved robustness to noise and density variation, with real SceneNN/Semantic3D generalization tests. | Core training/evaluation relies heavily on synthetic PCPNet conditions; should be used only as inference-time comparator on physical pipe scans. |
| R7 | `2210.07158v1.pdf` - HSurf-Net normal estimation | Useful pretrained normal-estimation candidate; targets noisy and density-varying point clouds and reports real indoor/outdoor scene generalization. | Core benchmark is synthetic-shape based; does not directly prove pipe-radius performance under physical pipe metrology. |
| R8 | `sensors-23-01196.pdf` - SPPE for pipe attributes and PIG pose | Useful mathematical formulation for simultaneous pipe attribute and pose estimation, including elliptical cross-sections, LMA optimization, gravity-based ovality angle, and pose/radius metrics. | Evidence is ROS simulation only; this program must physically validate any borrowed SPPE component before treating it as a result. |

### 0.2 Gap-to-experiment map

| Gap | Evidence that exposes the gap | Experiment that closes it | Core output |
|---|---|---|---|
| G1. Radius/diameter error is often reported as one accuracy number, without separating systematic bias from random variance. | R1 reports sensor/distance accuracy; R2 proves residual-induced diameter bias; R5 shows point-only methods drift under difficult RGB-D geometry. | Experiment 1 | Bias/variance curves by sensor, distance/incidence, diameter, residual, and optional edge/normal modules. |
| G2. Occlusion and incomplete visibility are discussed, but breakdown points are not measured under physically controlled occlusion. | R3 and R4 handle real missing data; R5 notes heavy occlusion was not explicitly tested. | Experiment 2 | Physical occlusion degradation curves and topology-recovery thresholds. |
| G3. Cross-sensor and cross-environment transfer protocols are not standardized. | R1, R3, R4, and R5 each validate in different settings with different sensors and metrics. | Experiment 3 | Open benchmark with metadata schema, ground truth, transfer matrix, and evaluation code. |
| G4. Individual fixes are not validated together at plant scale. | R2, R3, R4, and R5 each solve one part of the problem. | Experiment 4 | Integrated ablation study showing which components actually contribute under real facility or full-scale mockup conditions. |

### 0.3 Method-use policy for simulation-heavy references

- AdaFit, HSurf-Net, and SPPE can be included as method candidates only after being run on physically collected scans.
- Synthetic PCPNet results, ROS-generated PIG scans, rendered scenes, or computationally deleted point clouds cannot be counted as this program's experimental evidence.
- Sensitivity studies that were simulated in prior work must be converted into physical protocols here: repeated captures, physical sensor repositioning, real lighting changes, real material reflectance changes, physical occluders, and physical calibration targets.

---

## 1. Experiment 1 - Physical Bias/Variance Decomposition

### Objective

Separate systematic bias from random variance in pipe radius and diameter estimation, and test whether bias-aware residuals and RGB-D edge cues reduce systematic error across real sensors and acquisition conditions.

### Primary hypotheses

1. Canonical point-only cylinder/ellipse fitting will show measurable signed bias that grows with adverse range, incidence angle, small radius, or high curvature.
2. A symmetric error residual adapted from RU-EPD will reduce signed bias without simply trading it for higher variance.
3. For RGB-D sensors, edge-point fusion will reduce axis/radius drift when point-cloud geometry is weak, especially for small pipes and oblique views.
4. Learned normals may improve local fitting on noisy physical scans, but any benefit must be proven on the real scans collected here, not inferred from synthetic normal-estimation benchmarks.

### Physical design

**Factors**

| Factor | Levels | Notes |
|---|---|---|
| Sensor | LiDAR, Kinect v1/v2, Azure Kinect or comparable ToF RGB-D, stereo/RGB-D camera | Keep exact model, firmware, calibration file, warm-up time, and frame settings in the scan manifest. |
| Acquisition condition | Near/mid/far range or shallow/moderate/steep incidence angle | Choose values within each sensor's reliable range. The factor represents real sensor noise; no noise is injected. |
| Pipe radius/diameter | 5-8 certified pipe segments | Include at least one small radius where RGB-D curvature sensing is difficult and at least one facility-relevant large pipe. |
| Fitting method | Point-only RANSAC/least squares, canonical ellipse/cylinder residual, symmetric RU-EPD-style residual | The residual comparison is the primary inferential test. |
| RGB-D fusion substudy | Point-only vs. edge-point fusion | Applies only to sensors with aligned RGB and depth. Edge detection must be automatic in the final analysis; manual edge labels may be used only for an upper-bound pilot. |
| Normal-estimation substudy | PCA/WLS normals vs. AdaFit or HSurf-Net inference | Secondary paired comparison; no retraining or synthetic fine-tuning. |

**Ground truth**

- Certified or precision-machined pipe segments measured with digital calipers and cross-checked by CMM, portable arm, total station, laser tracker, or manufacturer certification.
- For facility pipes without certificate values, use a total station or laser tracker survey of that specific pipe.
- Store ground truth as a structured table: pipe ID, nominal radius, measured radius, uncertainty, measurement method, date, operator, and calibration certificate reference.

### Data collection

- Collect an unoccluded scan set for every sensor, pipe, and acquisition condition.
- At each cell, collect 20-25 independent real repeats by physically re-triggering capture, slightly repositioning the sensor within a controlled tolerance, and logging ambient conditions.
- Capture raw point clouds, raw RGB/depth frames when available, calibration files, sensor pose, standoff distance, incidence angle, exposure/gain settings, and operator notes.

### Metrics

- Signed radius error and signed diameter error.
- Variance and standard deviation of signed error.
- RMSE and MAE.
- Axis orientation error where ground-truth axis is available.
- Failure/non-convergence rate.
- Runtime and memory per frame.
- For RGB-D fusion: edge reprojection error and edge-confidence summary.

### Analysis

- Use a mixed-effects model rather than a plain fixed-effect ANOVA when repeated scans share the same physical pipe:
  `error ~ sensor * acquisition_condition * fitting_method + (1 | pipe_id) + (1 | session_id)`.
- Analyze signed bias and RMSE separately.
- Report confidence intervals and effect sizes, not only p-values.
- Use paired tests for method comparisons inside the same physical scan.
- For RGB-D fusion, include an interaction term for radius and incidence angle because R5 suggests small radii and oblique views are where point-only methods degrade.
- Re-estimate power after the first pilot block of at least 5 pipes x 3 conditions x 5 repeats.

### Planning power

The confirmatory residual comparison keeps the current planning target of about 20-25 real repeated scans per primary cell. With 4 sensors x 3 acquisition conditions x 2 residual families, that is about 480-600 real scans before radius blocking is included in the mixed model. If the method factor is expanded to three point-only residuals, use the pilot variance to decide whether to reduce sensor levels, collapse conditions, or increase collection time.

### Deliverables

- Sensor-specific bias/variance profiles.
- Residual-method comparison table.
- RGB-D edge-fusion substudy report.
- Normal-estimation substudy report.
- Public acquisition manifest template for later benchmark release.

---

## 2. Experiment 2 - Physical Occlusion Degradation and Topology Recovery

### Objective

Quantify how radius, axis, centerline, and topology estimates degrade as physically visible pipe surface shrinks, and identify the occlusion level where each method fails.

### Primary hypotheses

1. Direct point-only fitting fails earlier than segmentation plus local slice fitting and topology-aware reconstruction.
2. Adaptive RANSAC centerline and topology reconstruction will preserve usable topology at higher occlusion levels than local fitting alone.
3. RGB-D edge cues help under moderate occlusion but degrade when edges are physically hidden, low-contrast, or contaminated by rebar/background texture.
4. Corrugated pipes and elbows will show different failure modes from straight smooth pipes.

### Physical design

| Factor | Levels | Notes |
|---|---|---|
| Occlusion | Target visible circumference after physical blocking: about 90%, 70%, 50%, 30%, 15% visible | Create with panels, mesh, rebar cages, soil, pipe racks, or facility clutter. Actual visibility is measured after capture. |
| Shape | Straight smooth pipe, corrugated pipe, elbow/bend, optional tee/reducer pilot | Use real parts. |
| Method | Direct point-only fitting, segmentation plus local slice fitting, adaptive RANSAC centerline/topology reconstruction, RGB-D edge-point fusion, combined topology plus bias-aware fitting | RGB-D method included only when aligned images exist. |
| Environment | Lab rig plus at least one field-realistic subset | Field subset can be trench, rebar cage, precast mockup, or cluttered plant rig. |

### Ground truth

- Scan and/or survey each pipe before adding occluders.
- Measure radius, axis, segment endpoints, elbow angle, bend radius, and topology with CMM, total station, laser tracker, or high-resolution reference scan.
- For naturally occluded real sites, survey before burial/covering when possible. If not possible, mark the site as qualitative or pilot-only.

### Visibility measurement

- Do not assign occlusion by deleting points.
- Estimate actual visible arc/circumference from the occluded real scan relative to the matching unoccluded scan.
- Record both intended occlusion and measured visible coverage.

### Metrics

- Radius/diameter error.
- Axis-angle error.
- Centerline position error.
- Centerline continuity error.
- Topology precision, recall, and F1 for correctly connected segments.
- Failure/non-convergence rate.
- Breakdown point: the lowest visible coverage where each method stays below the predefined usability threshold, such as 5% radius error and topology F1 above 0.85.

### Analysis

- Use repeated-measures mixed models:
  `metric ~ visible_coverage * method * shape + (1 | pipe_id) + (1 | session_id)`.
- Fit degradation curves and report method-specific breakdown points with confidence intervals.
- Use corrected paired comparisons at each occlusion level.
- Analyze failures as binary outcomes with logistic mixed-effects models.

### Planning power

Use the current planning estimate as the upper target: about 15 physical pipe instances per shape condition, 5 occlusion levels, and 3-5 method variants. Reusing the same physical pipe across progressive occlusion levels is valid because each scan is a new physical observation. Pilot data may justify fewer shape instances if effect sizes are large.

### Deliverables

- Occlusion degradation curves.
- Breakdown-point table by shape and method.
- Topology recovery report.
- Physical occluder layout diagrams and measurement protocol.

---

## 3. Experiment 3 - Cross-Sensor, Cross-Environment Benchmark

### Objective

Create and validate a reusable benchmark for cross-sensor and cross-environment pipe-parameter estimation using only real scans and physical ground truth.

### Design

| Dimension | Levels |
|---|---|
| Sensors | LiDAR, Kinect/Azure Kinect or comparable ToF RGB-D, stereo/RGB-D |
| Environments | Controlled lab rig, semi-controlled industrial/precast facility, uncontrolled field or underground site |
| Transfer condition | Zero-shot frozen parameters, light physical-domain calibration |

The benchmark unit is a `sensor x environment x scene` capture set with known calibration, ground truth, and metadata.

### Benchmark data schema

Every scan bundle must include:

- `scan_id`, `scene_id`, `site_id`, `sensor_id`, `operator_id`, and timestamp.
- Raw point cloud path and raw RGB/depth paths where applicable.
- Intrinsic calibration, extrinsic calibration, sensor pose estimate, warm-up time, and firmware/software versions.
- Pipe inventory: pipe IDs, material, surface finish, nominal diameter, measured diameter/radius, axis/centerline, topology, and uncertainty.
- Acquisition metadata: range, incidence angle, lighting, temperature, reflectance notes, occlusion notes, and clutter category.
- Ground-truth method and calibration certificate reference.
- Train/calibration/evaluation split labels.
- License and release status.

### Transfer protocol

1. Calibrate on one `sensor x environment` source combination.
2. Freeze parameters and evaluate zero-shot on all other target combinations.
3. Repeat with a small target calibration set, such as 5-10 labeled physical scans per target.
4. Report the result as a source-to-target matrix for signed bias, RMSE, failure rate, runtime, and memory.

### Metrics

- Radius/diameter signed bias, RMSE, and MAE.
- Axis and centerline errors.
- Topology precision/recall/F1 when topology is present.
- Runtime and memory.
- Manual parameter changes per target scene.
- Calibration data required to reach each target accuracy level.

### Planning power

The planning target remains about 25-30 evaluation scans per `sensor x environment` combination, or about 270 evaluation scans for 9 combinations. Calibration scans are separate from evaluation scans and must not be reused for reported test metrics.

### Deliverables

- Versioned benchmark folder structure.
- Scan manifest and ground-truth manifest templates.
- Evaluation script specification.
- Zero-shot and light-calibration transfer matrices.
- Public release checklist, including anonymization and site-permission constraints.

---

## 4. Experiment 4 - Integrated Plant-Scale Ablation

### Objective

Test whether the combined pipeline improves end-to-end radius, centerline, and topology estimation at plant scale, and identify which component actually contributes to the improvement.

### Integrated pipeline

The full pipeline is:

1. Sensor calibration and scan ingestion.
2. Pipe segmentation.
3. Bias-aware radius/diameter fitting.
4. Optional RGB-D edge-point fusion when RGB-D is available.
5. Physical-occlusion-aware centerline and topology reconstruction.
6. Cross-sensor calibration/normalization.
7. Benchmark evaluation and reporting.

### Ablation conditions

| Condition | Description |
|---|---|
| Full pipeline | All validated components enabled. |
| No bias correction | Replace symmetric residual with canonical point-only fitting. |
| No topology recovery | Remove adaptive centerline/topology reconstruction and keep local fitting only. |
| No cross-sensor calibration | Use source-domain parameters without sensor/environment normalization. |
| No RGB/edge cue | Disable edge-point fusion on RGB-D data. |
| Baseline-only | Original point-only RANSAC/least-squares pipeline with standard segmentation. |

### Site

Use either:

- A real facility with straight pipes, elbows, reducers/tees if available, clutter, partial occlusion, varied materials, and multiple sensor positions.
- A full-scale physical mockup built from real straight, corrugated, elbow, and clutter components if facility access is unavailable.

No rendered or digital-twin scene substitutes for the validation site.

### Metrics

- End-to-end radius/diameter signed bias, RMSE, and failure rate.
- Axis and centerline error.
- Topology F1.
- Robustness across repeated passes and sensor positions.
- Runtime, memory, and throughput.
- Operator effort: manual annotations, parameter changes, failed runs needing intervention, and minutes of manual tuning per scene.

### Analysis

- Use repeated real passes from multiple sensor positions.
- Prefer a mixed-effects model:
  `metric ~ pipeline_condition + (1 | pass_id) + (1 | pipe_id) + (1 | sensor_id)`.
- Compare each ablation to the full pipeline with corrected paired contrasts.
- Analyze failure rate separately with logistic models.

### Planning power

With 6 conditions, target about 18-20 independent real passes per condition for confirmatory analysis, or about 108-120 total trial runs. If this is not practical, run a clearly labeled pilot with 8-10 passes per condition and avoid confirmatory claims.

### Deliverables

- Integrated pipeline ablation table.
- Failure-mode taxonomy.
- Operator-effort report.
- Plant-scale runtime/memory report.
- Final recommendation on which components should be retained for a deployable benchmark pipeline.

---

## 5. Statistical and Power Plan

### General statistical rules

- Do not collapse signed bias, variance, and RMSE into one accuracy number.
- Treat repeated scans of the same physical pipe as repeated measures.
- Use mixed-effects models when pipe, site, session, or sensor identity creates grouped observations.
- Use paired comparisons wherever two methods run on the same scan.
- Correct multiple comparisons with Holm, Tukey, or false-discovery-rate control depending on the family of tests.
- Report effect sizes and confidence intervals for every major result.
- Report failures explicitly; do not silently omit non-converged scans.

### Pilot power update

Before locking sample sizes:

1. Collect a pilot block from at least 3 sensors, 3 acquisition conditions, 3 pipe radii, and 5 repeats.
2. Estimate variance components for sensor, pipe, session, and repeat.
3. Recompute power for signed bias and RMSE separately.
4. Decide whether to increase repeats, reduce factor levels, or treat a result as exploratory.

### Confirmatory vs. exploratory claims

- Experiments 1 and 2 are confirmatory only after pilot-updated sample sizes are met.
- Experiment 3 is confirmatory for transfer only if every cell has the target evaluation scans and held-out ground truth.
- Experiment 4 can be published as a pilot if plant-scale pass count is lower than the confirmatory target, but the wording must state that clearly.

---

## 6. Reproducibility and Data Management

### Required artifacts before data collection

- Sensor calibration SOP.
- Ground-truth measurement SOP.
- Physical occlusion setup SOP.
- Scan manifest schema.
- Ground-truth manifest schema.
- Processing configuration schema.
- Failure-code list.
- Operator log template.
- Data release and anonymization checklist.

### Required artifacts after data collection

- Raw data archive.
- Processed point-cloud archive.
- Calibration files.
- Ground-truth tables with uncertainty.
- Evaluation scripts and fixed version tags.
- Result tables and plotted degradation/transfer curves.
- README explaining how to reproduce every reported metric.

### Acceptance checklist

An experiment is complete only when:

- Every scan has a manifest row.
- Every metric can be traced to a scan ID, ground-truth ID, method version, and configuration file.
- All excluded scans have a failure/exclusion code.
- Pilot-updated power assumptions are recorded.
- Results separate bias, variance, RMSE, and failure rate.
- No synthetic or computationally masked point cloud is included in the evidence set.

---

## 7. Master Timeline

| Month | Experiment 1 | Experiment 2 | Experiment 3 | Experiment 4 | Milestone |
|---|---|---|---|---|---|
| 1 | Sensor procurement, calibration SOP, pipe certification | Occluder design | Benchmark schema draft | Facility/mockup planning | Instrumentation and schemas ready |
| 2 | Pilot scans and pilot power update | Source real corrugated/elbow samples | Site permission work | Mockup bill of materials | Pilot variance available |
| 3 | Full physical scan collection | Baseline unoccluded scans | Lab benchmark setup | | Experiment 1 data complete |
| 4 | Analysis and write-up | Physical occlusion scans | Facility benchmark collection | | Experiment 1 results draft |
| 5 | | Occlusion analysis | Facility benchmark collection | | Experiment 2 data complete |
| 6 | | Write-up | Field/underground benchmark collection | | Experiment 2 results draft |
| 7 | | | Transfer analysis and benchmark packaging | Build/access validation site | Experiment 3 data complete |
| 8 | | | Benchmark release candidate | Integrated repeated passes | Experiment 3 results draft |
| 9 | | | | Integrated repeated passes | Experiment 4 data complete |
| 10 | | | | Ablation analysis | Experiment 4 results draft |
| 11 | Cross-experiment consistency checks | | | | Full manuscript draft |
| 12 | Reproducibility audit, dataset packaging, final revision | | | | Submission package ready |

---

## 8. Master Budget

Order-of-magnitude USD estimate. Localize prices and rental availability before committing.

| Category | Item | Estimate |
|---|---|---|
| Sensors | LiDAR unit | $5,000-8,000 |
| Sensors | Kinect v1/v2 plus Azure Kinect or comparable ToF RGB-D | $600-1,500 |
| Sensors | Stereo/RGB-D camera | $300-1,500 |
| Ground truth | CMM access, portable arm, total station, or laser tracker rental | $2,000-5,000 rental; $10,000-30,000 purchase depending on device |
| Ground truth | Certified or precision-machined pipe segment set | $2,000-6,000 |
| Materials | Corrugated pipes, elbows, tees/reducers, mounting fixtures | $1,000-3,000 |
| Occlusion | Panels, mesh, rebar sections, soil boxes, adjustable mounts | $500-1,500 |
| Plant-scale mockup | Full-scale physical rig if facility access is unavailable | $3,000-8,000 |
| Compute | Workstation for processing and pretrained-model inference | $1,500-3,000 |
| Site access | Facility, trench/underground access, travel, permissions | $5,000-10,000 |
| Personnel | One research assistant or PhD student, 12 months | $45,000-65,000 region-dependent |
| Dissemination | Dataset hosting, DOI, repository maintenance | $500-1,000 |
| Contingency | 10-15% of subtotal | About $7,000-13,000 |
| Total | Indicative range | About $75,000-150,000 |

---

## 9. Reference and Verification Notes

The accompanying `experiment_references.json` records the reviewed PDFs, evidence tier, protocol use, and unresolved limitations.

Reference-use rules:

- Physical-data papers can support protocol design and expected effect direction.
- Mixed physical/simulation papers can support method choice, but any simulation-derived effect size must be treated as provisional.
- Simulation-only papers can define algorithms or metrics, but cannot support claims that this no-synthetic-point-cloud program has already validated a result.
- Any paper with manual annotations or controlled-only settings creates a validation gap that must be explicitly tested in Experiments 2-4.

The largest remaining practical risks are site access, ground-truth logistics, consistent calibration across sensors, and the labor required for physical repeats. Those risks are methodological, not reasons to use synthetic padding.
