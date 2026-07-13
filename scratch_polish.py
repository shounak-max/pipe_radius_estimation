import sys
import os
sys.path.insert(0, os.path.abspath('src'))
import numpy as np
from pipe_estimation.simulator import generate_synthetic_pipe
from pipe_estimation.fitting import CylinderFitter

def test_gauge_freedom():
    points = generate_synthetic_pipe(50.0, 200.0, 1000, 0.0, visible_fraction=1.0)
    fitter = CylinderFitter("canonical")
    init = [0, 0, 100, 0, 0, 48]
    res, diag = fitter.fit(points, init)
    
    # Original cost
    c = res[0:3]
    a = np.array([np.sin(res[3])*np.cos(res[4]), np.sin(res[3])*np.sin(res[4]), np.cos(res[3])])
    r = res[5]
    
    v = points - c
    dist = np.linalg.norm(np.cross(v, a), axis=1)
    
    # Notice that we compute the core geometric cost here, excluding regularization
    geom_cost1 = np.sum((dist - r)**2)
    print(f"Original geometric cost: {geom_cost1}")
    
    # Shift c by 50mm along a
    c2 = c + 50.0 * a
    v2 = points - c2
    dist2 = np.linalg.norm(np.cross(v2, a), axis=1)
    geom_cost2 = np.sum((dist2 - r)**2)
    print(f"Shifted geometric cost: {geom_cost2}")
    print(f"Difference: {abs(geom_cost1 - geom_cost2)}")

def test_15_percent_clustering():
    points_base = 1000
    true_radius = 50.0
    radii = []
    fitter = CylinderFitter("canonical")
    
    for i in range(50):
        np.random.seed(i + 15)
        points = generate_synthetic_pipe(50.0, 200.0, 150, 1.0, visible_fraction=0.15, sensor_origin=(300, 0, 100))
        init = [0, 0, 100, 0, 0, 45]
        try:
            res, diag = fitter.fit(points, init)
            if diag.get('converged', False):
                radii.append(res[5])
        except Exception:
            pass
            
    print(f"\n15% Visibility Radii (first 20):")
    for i, r in enumerate(radii[:20]):
        print(f"  Trial {i}: {r:.2f}mm")

if __name__ == "__main__":
    test_gauge_freedom()
    test_15_percent_clustering()
