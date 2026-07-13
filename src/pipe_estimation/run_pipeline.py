import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
from pipe_estimation.simulator import generate_synthetic_pipe
from pipe_estimation.fitting import CylinderFitter
from pipe_estimation.evaluation import compute_signed_bias

def run_monte_carlo_experiment_1(num_trials=50):
    print("--- Experiment 1: Bias and Variance (Gap 1) [Monte Carlo N=50] ---")
    true_radius = 50.0 # mm
    length = 200.0
    num_points = 1000
    noise_levels = [0.0, 1.0, 2.0, 5.0]
    
    canonical_fitter = CylinderFitter(residual_type="canonical")
    variance_fitter = CylinderFitter(residual_type="variance_corrected")
    ru_epd_fitter = CylinderFitter(residual_type="ru_epd")
    
    sensor_origin = (300, 0, length/2) # Look at the pipe from the side
    
    for noise in noise_levels:
        print(f"\n>> Noise Std = {noise}mm")
        biases_canon = []
        biases_var = []
        biases_ru = []
        
        canon_converged = 0
        var_converged = 0
        ru_converged = 0
        
        for trial in range(num_trials):
            seed = trial + int(noise*100)
            np.random.seed(seed)
            points = generate_synthetic_pipe(true_radius, length, num_points, noise, visible_fraction=1.0, sensor_origin=sensor_origin)
            
            # Print paired sampling proof for the first trial
            if trial == 0:
                print(f"  [Verification] Trial 0 uses paired RNG seed: {seed}. All estimators share the same {points.shape} point cloud.")
            
            # cx, cy, cz, theta, phi, r
            initial_guess = np.array([5.0, -5.0, length/2, 0.0, 0.0, true_radius * 0.9])
            
            diag_canon, diag_var, diag_ru = {}, {}, {}
            
            try:
                params_canon, diag_canon = canonical_fitter.fit(points, initial_guess)
                mean_res_norm = np.sqrt(2 * diag_canon.get('cost', np.inf) / max(1, len(points)))
                # Reject if residual is vastly larger than expected noise (or at least 3.0mm to allow for zero-noise edge case)
                if diag_canon.get('converged', False) and mean_res_norm < max(3.0, 5.0 * noise):
                    bias_canon = compute_signed_bias(params_canon[5], true_radius)
                    biases_canon.append(bias_canon)
                    canon_converged += 1
            except Exception as e:
                pass
                
            try:
                params_var, diag_var = variance_fitter.fit(points, initial_guess)
                mean_res_norm = np.sqrt(2 * diag_var.get('cost', np.inf) / max(1, len(points)))
                if diag_var.get('converged', False) and mean_res_norm < max(3.0, 5.0 * noise):
                    bias_var = compute_signed_bias(params_var[5], true_radius)
                    biases_var.append(bias_var)
                    var_converged += 1
            except Exception as e:
                pass

            try:
                params_ru, diag_ru = ru_epd_fitter.fit(points, initial_guess, sensor_origin=sensor_origin)
                mean_res_norm = np.sqrt(2 * diag_ru.get('cost', np.inf) / max(1, len(points)))
                if diag_ru.get('converged', False) and mean_res_norm < max(3.0, 5.0 * noise):
                    bias_ru = compute_signed_bias(params_ru[5], true_radius)
                    biases_ru.append(bias_ru)
                    ru_converged += 1
            except Exception as e:
                import traceback; traceback.print_exc()
                pass
                
            # Print diagnostic info for Trial 0 across ALL noise levels
            if trial == 0:
                sv_canon = np.array2string(diag_canon.get('singular_values', np.array([])), precision=2, suppress_small=True)
                print(f"  [Diagnostics] Canon cond={diag_canon.get('condition_number', np.nan):.1f} | Var cond={diag_var.get('condition_number', np.nan):.1f} | RU cond={diag_ru.get('condition_number', np.nan):.1f}")
                print(f"  [SV Canon] {sv_canon}")
                
        if len(biases_canon) > 0:
            mean_canon = np.mean(biases_canon)
            std_canon = np.std(biases_canon)
            stderr_canon = std_canon / np.sqrt(len(biases_canon))
            rejected = num_trials - canon_converged
            print(f"  Canonical Bias: Mean = {mean_canon:+.3f}mm | Std = {std_canon:.3f}mm | SE = {stderr_canon:.3f}mm ({canon_converged} converged, {rejected} rejected)")
        else:
            print("  Canonical Bias: ALL FAILED TO CONVERGE")
            
        if len(biases_var) > 0:
            mean_var = np.mean(biases_var)
            std_var = np.std(biases_var)
            stderr_var = std_var / np.sqrt(len(biases_var))
            rejected = num_trials - var_converged
            print(f"  Variance-Corrected Bias: Mean = {mean_var:+.3f}mm | Std = {std_var:.3f}mm | SE = {stderr_var:.3f}mm ({var_converged} converged, {rejected} rejected)")
        else:
            print("  Variance-Corrected Bias: ALL FAILED TO CONVERGE")
            
        if len(biases_ru) > 0:
            mean_ru = np.mean(biases_ru)
            std_ru = np.std(biases_ru)
            stderr_ru = std_ru / np.sqrt(len(biases_ru))
            rejected = num_trials - ru_converged
            print(f"  True RU-EPD Bias: Mean = {mean_ru:+.3f}mm | Std = {std_ru:.3f}mm | SE = {stderr_ru:.3f}mm ({ru_converged} converged, {rejected} rejected)")
        else:
            print("  True RU-EPD Bias: ALL FAILED TO CONVERGE")

def run_monte_carlo_experiment_2(num_trials=50):
    print("\n--- Experiment 2: Occlusion Degradation (Gap 2) [Monte Carlo N=50] ---")
    true_radius = 50.0
    length = 200.0
    num_points_base = 1000
    noise = 1.0 # fixed small noise
    
    visible_fractions = [0.9, 0.7, 0.5, 0.3, 0.15]
    
    canonical_fitter = CylinderFitter(residual_type="canonical")
    variance_fitter = CylinderFitter(residual_type="variance_corrected")
    ru_epd_fitter = CylinderFitter(residual_type="ru_epd")
    
    sensor_origin = (300, 0, length/2) # Look at the pipe from the side
    
    for vis in visible_fractions:
        print(f"\n>> Visibility = {vis*100}%")
        biases_canon = []
        biases_var = []
        biases_ru = []
        canon_converged = 0
        var_converged = 0
        ru_converged = 0
        
        for trial in range(num_trials):
            seed = trial + int(vis*100)
            np.random.seed(seed)
            num_points = int(num_points_base * vis)
            points = generate_synthetic_pipe(true_radius, length, num_points, noise, visible_fraction=vis, sensor_origin=sensor_origin)
            
            # cx, cy, cz, theta, phi, r
            initial_guess = np.array([0.0, 0.0, length/2, 0.0, 0.0, true_radius * 0.9])
            
            diag_canon, diag_var, diag_ru = {}, {}, {}
            
            try:
                params_canon, diag_canon = canonical_fitter.fit(points, initial_guess)
                mean_res_norm = np.sqrt(2 * diag_canon.get('cost', np.inf) / max(1, len(points)))
                if diag_canon.get('converged', False) and mean_res_norm < max(3.0, 5.0 * noise):
                    bias_canon = compute_signed_bias(params_canon[5], true_radius)
                    biases_canon.append(bias_canon)
                    canon_converged += 1
            except Exception:
                pass
                
            try:
                params_var, diag_var = variance_fitter.fit(points, initial_guess)
                mean_res_norm = np.sqrt(2 * diag_var.get('cost', np.inf) / max(1, len(points)))
                if diag_var.get('converged', False) and mean_res_norm < max(3.0, 5.0 * noise):
                    bias_var = compute_signed_bias(params_var[5], true_radius)
                    biases_var.append(bias_var)
                    var_converged += 1
            except Exception:
                pass

            try:
                params_ru, diag_ru = ru_epd_fitter.fit(points, initial_guess, sensor_origin=sensor_origin)
                mean_res_norm = np.sqrt(2 * diag_ru.get('cost', np.inf) / max(1, len(points)))
                if diag_ru.get('converged', False) and mean_res_norm < max(3.0, 5.0 * noise):
                    bias_ru = compute_signed_bias(params_ru[5], true_radius)
                    biases_ru.append(bias_ru)
                    ru_converged += 1
            except Exception:
                pass
                
            if trial == 0:
                print(f"  [Diagnostics] Canon cond={diag_canon.get('condition_number', np.nan):.1f} | Var cond={diag_var.get('condition_number', np.nan):.1f} | RU cond={diag_ru.get('condition_number', np.nan):.1f}")

        if len(biases_canon) > 0:
            mean_canon = np.mean(biases_canon)
            std_canon = np.std(biases_canon)
            stderr_canon = std_canon / np.sqrt(len(biases_canon))
            rejected = num_trials - canon_converged
            print(f"  Canonical Bias: Mean = {mean_canon:+.3f}mm | Std = {std_canon:.3f}mm | SE = {stderr_canon:.3f}mm ({canon_converged} converged, {rejected} rejected)")
        else:
            print("  Canonical Bias: ALL FAILED TO CONVERGE")
            
        if len(biases_var) > 0:
            mean_var = np.mean(biases_var)
            std_var = np.std(biases_var)
            stderr_var = std_var / np.sqrt(len(biases_var))
            rejected = num_trials - var_converged
            print(f"  Variance-Corrected Bias: Mean = {mean_var:+.3f}mm | Std = {std_var:.3f}mm | SE = {stderr_var:.3f}mm ({var_converged} converged, {rejected} rejected)")
        else:
            print("  Variance-Corrected Bias: ALL FAILED TO CONVERGE")
            
        if len(biases_ru) > 0:
            mean_ru = np.mean(biases_ru)
            std_ru = np.std(biases_ru)
            stderr_ru = std_ru / np.sqrt(len(biases_ru))
            rejected = num_trials - ru_converged
            print(f"  True RU-EPD Bias: Mean = {mean_ru:+.3f}mm | Std = {std_ru:.3f}mm | SE = {stderr_ru:.3f}mm ({ru_converged} converged, {rejected} rejected)")
        else:
            print("  True RU-EPD Bias: ALL FAILED TO CONVERGE")

if __name__ == "__main__":
    run_monte_carlo_experiment_1()
    run_monte_carlo_experiment_2()
