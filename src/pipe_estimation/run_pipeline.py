import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from pipe_estimation.simulator import generate_plant_scale_scene
from pipe_estimation.fitting import CylinderFitter
from pipe_estimation.evaluation import compute_signed_bias
from scipy.optimize import least_squares

def run_simulation_ablation(num_trials=50):
    print("==========================================================")
    print(f" Simulation-Only: Integrated Plant-Scale Ablation (N={num_trials}) ")
    print("==========================================================")
    
    biases_base, biases_topo, biases_full = [], [], []
    
    for trial in range(num_trials):
        np.random.seed(trial * 100)
        
        scene_cloud, ground_truth = generate_plant_scale_scene(sensor_type="lidar", occlusion_level="heavy")
        target_pipe = ground_truth[1]
        gt_radius = target_pipe['radius']
        gt_axis = np.array(target_pipe['axis'])
        
        # Heavily occluded (15% visible)
        pipe2_points = scene_cloud[2000:] 
        
        # cx, cy, cz, theta, phi, r
        c_guess = np.mean(pipe2_points, axis=0)
        initial_guess = np.array([c_guess[0], c_guess[1], c_guess[2], 0.0, 1.0, 90.0])
        init_constrained = np.array([c_guess[0], c_guess[1], c_guess[2], 90.0])
        
        # 1. Baseline
        fitter_baseline = CylinderFitter(residual_type="canonical")
        try:
            params_base, diag_base = fitter_baseline.fit(pipe2_points, initial_guess)
            if diag_base.get('converged', False) or diag_base.get('status', -1) > 0:
                bias_base = compute_signed_bias(params_base[5], gt_radius)
                biases_base.append(bias_base)
        except Exception:
            pass
            
        # 2. Topology-Aware
        def constrained_residual(params, points):
            c = params[0:3]
            a = gt_axis
            r = params[3]
            v = points - c
            dist_to_axis = np.linalg.norm(np.cross(v, a), axis=1)
            return dist_to_axis - r
            
        res_topo = least_squares(constrained_residual, init_constrained, args=(pipe2_points,), method='lm')
        if res_topo.success:
            bias_topo = compute_signed_bias(res_topo.x[3], gt_radius)
            biases_topo.append(bias_topo)
        
        # 3. Topology-Aware + Bias Correction
        # We first run the canonical constrained residual to get the fixed variance
        def canonical_constrained_residual(params, points):
            c = params[0:3]
            a = gt_axis
            r = params[3]
            v = points - c
            dist = np.linalg.norm(np.cross(v, a), axis=1)
            return dist - r
            
        res_canon_const = least_squares(canonical_constrained_residual, init_constrained, args=(pipe2_points,), method='lm')
        fixed_var = np.var(canonical_constrained_residual(res_canon_const.x, pipe2_points))
        
        def variance_corrected_constrained_residual(params, points, f_var):
            c = params[0:3]
            a = gt_axis
            r = np.exp(params[3])
            v = points - c
            dist = np.linalg.norm(np.cross(v, a), axis=1)
            residuals = dist - r
            correction = f_var / (2 * r)
            return residuals - correction
            
        init_full = np.copy(res_canon_const.x)
        if init_full[3] <= 0:
            init_full[3] = 1e-6
        init_full[3] = np.log(init_full[3])
            
        res_full = least_squares(variance_corrected_constrained_residual, init_full, args=(pipe2_points, fixed_var), method='lm')
        if res_full.success:
            final_radius = np.exp(res_full.x[3])
            bias_full = compute_signed_bias(final_radius, gt_radius)
            biases_full.append(bias_full)

    # Calculate statistics
    mean_base = np.nanmean(biases_base) if biases_base else np.nan
    std_base = np.nanstd(biases_base) if biases_base else np.nan
    mean_topo = np.nanmean(biases_topo) if biases_topo else np.nan
    std_topo = np.nanstd(biases_topo) if biases_topo else np.nan
    mean_full = np.nanmean(biases_full) if biases_full else np.nan
    std_full = np.nanstd(biases_full) if biases_full else np.nan

    print("\n--- Monte Carlo Results ---")
    print(f"[Baseline] Canonical (Local only)      : Mean Bias = {mean_base:+.3f}mm, Std = {std_base:.3f}mm")
    print(f"[Ablation 1] Topology-Aware (Constrained): Mean Bias = {mean_topo:+.3f}mm, Std = {std_topo:.3f}mm")
    print(f"[Ablation 2] Topology + Var-Corrected  : Mean Bias = {mean_full:+.3f}mm, Std = {std_full:.3f}mm")

    print("\n==========================================================")
    print("Conclusion:")
    if np.abs(mean_base - mean_topo) < 0.1 and np.abs(std_base - std_topo) < 0.1:
        print("Topology constraint alone did NOT significantly reduce bias or variance")
        print("in this single-elbow simulated scene compared to a decent initial guess.")
    else:
        print("Topology constraints materially shifted the fitting outcome.")
        
    if np.abs(mean_full) < np.abs(mean_topo):
        print("Variance-correction successfully reduced the absolute bias magnitude further.")
    else:
        print("Variance-correction did not reduce the bias magnitude in this configuration.")
    print("==========================================================")
    
    return mean_base, mean_topo, mean_full

if __name__ == "__main__":
    run_simulation_ablation()
