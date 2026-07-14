import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import unittest
import numpy as np
from pipe_estimation.fitting import canonical_cylinder_residual, variance_corrected_residual, CylinderFitter
from pipe_estimation.simulator import generate_synthetic_pipe

class TestFitting(unittest.TestCase):
    def test_canonical_residual_math(self):
        # Point at distance 10 from Z axis
        points = np.array([[10, 0, 5]])
        params = np.array([0, 0, 0, 0, 0, 9]) # Cylinder centered at 0, radius 9
        res = canonical_cylinder_residual(params, points)
        self.assertAlmostEqual(res[0], 1.0) # distance is 10, radius is 9, diff is 1

    def test_zero_noise_full_visibility(self):
        # True params
        radius = 50.0
        points = generate_synthetic_pipe(radius, 200, 1000, noise_std=0.0, visible_fraction=1.0)
        
        # Initial guess slightly off
        init_guess = np.array([0.0, 0.0, 100.0, 0.0, 0.0, 48.0])
        
        fitter_canon = CylinderFitter(residual_type="canonical")
        fitter_sym = CylinderFitter(residual_type="variance_corrected")
        
        res_canon, _ = fitter_canon.fit(points, init_guess)
        res_sym, _ = fitter_sym.fit(points, init_guess)
        
        self.assertAlmostEqual(res_canon[5], radius, places=3)
        self.assertAlmostEqual(res_sym[5], radius, places=3)
        
    def test_zero_noise_low_visibility(self):
        # 30% visibility
        radius = 50.0
        points = generate_synthetic_pipe(radius, 200, 1000, noise_std=0.0, visible_fraction=0.3)
        
        init_guess = np.array([0.0, 0.0, 100.0, 0.0, 0.0, 48.0])
        
        fitter_canon = CylinderFitter(residual_type="canonical")
        fitter_sym = CylinderFitter(residual_type="variance_corrected")
        
        res_canon, _ = fitter_canon.fit(points, init_guess)
        res_sym, _ = fitter_sym.fit(points, init_guess)
        
        self.assertAlmostEqual(res_canon[5], radius, places=3)
        self.assertAlmostEqual(res_sym[5], radius, places=3)

if __name__ == '__main__':
    unittest.main()
