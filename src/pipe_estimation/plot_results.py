import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib.pyplot as plt
from pipe_estimation.run_experiments import run_monte_carlo_experiment_1, run_monte_carlo_experiment_2

def plot_and_save():
    artifact_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'plots'))
    os.makedirs(artifact_dir, exist_ok=True)
    
    # Run experiments
    res1 = run_monte_carlo_experiment_1()
    res2 = run_monte_carlo_experiment_2()
    
    # Plot Experiment 1
    noises = [r[0] for r in res1]
    bias_canon = [r[1] for r in res1]
    bias_var = [r[2] for r in res1]
    bias_ru = [r[3] for r in res1]
    
    plt.figure(figsize=(8, 5))
    plt.plot(noises, bias_canon, marker='o', label='Canonical Bias', linestyle='--')
    plt.plot(noises, bias_var, marker='s', label='Variance-Corrected Bias', linestyle='-.')
    plt.plot(noises, bias_ru, marker='^', label='True RU-EPD Bias', linestyle='-')
    plt.title('Experiment 1: Signed Bias vs Gaussian Noise')
    plt.xlabel('Noise Std (mm)')
    plt.ylabel('Signed Bias (mm)')
    plt.legend()
    plt.grid(True)
    exp1_path = os.path.join(artifact_dir, "experiment1_bias.png")
    plt.savefig(exp1_path)
    plt.close()
    
    # Plot Experiment 2
    vis = [r[0] * 100 for r in res2] # convert to percentage
    bias_canon2 = [r[1] for r in res2]
    bias_var2 = [r[2] for r in res2]
    bias_ru2 = [r[3] for r in res2]
    
    plt.figure(figsize=(8, 5))
    plt.plot(vis, bias_canon2, marker='o', label='Canonical Bias', linestyle='--')
    plt.plot(vis, bias_var2, marker='s', label='Variance-Corrected Bias', linestyle='-.')
    plt.plot(vis, bias_ru2, marker='^', label='True RU-EPD Bias', linestyle='-')
    plt.title('Experiment 2: Signed Bias vs Visible Circumference (Occlusion)')
    plt.xlabel('Visible Circumference (%)')
    plt.ylabel('Signed Bias (mm)')
    plt.gca().invert_xaxis() # lower visibility means higher occlusion
    plt.legend()
    plt.grid(True)
    exp2_path = os.path.join(artifact_dir, "experiment2_occlusion.png")
    plt.savefig(exp2_path)
    plt.close()
    
    print(f"Saved plots to {exp1_path} and {exp2_path}")

if __name__ == "__main__":
    plot_and_save()
