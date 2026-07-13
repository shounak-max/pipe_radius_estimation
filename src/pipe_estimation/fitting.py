import numpy as np
from scipy.optimize import least_squares
from scipy.linalg import svd

def get_axis_from_angles(theta, phi):
    return np.array([
        np.sin(theta) * np.cos(phi),
        np.sin(theta) * np.sin(phi),
        np.cos(theta)
    ])

def canonical_cylinder_residual(params, points):
    """
    Standard cylinder residual: distance from point to the cylinder surface.
    params: [cx, cy, cz, theta, phi, r]
    """
    c = params[0:3]
    a = get_axis_from_angles(params[3], params[4])
    r = params[5]
    
    v = points - c
    dist_to_axis = np.linalg.norm(np.cross(v, a), axis=1)
    
    res = np.zeros(len(points) + 1)
    res[:-1] = dist_to_axis - r
    res[-1] = 1e-4 * np.dot(c, a) # Regularize center drift
    return res

def symmetric_bias_aware_residual(params, points):
    """
    Symmetric algebraic residual (d^2 - r^2)
    This form avoids the square root which biases the expected value under depth-axis noise.
    """
    c = params[0:3]
    a = get_axis_from_angles(params[3], params[4])
    r = params[5]
    
    v = points - c
    dist_to_axis = np.linalg.norm(np.cross(v, a), axis=1)
    
    var_d = np.var(dist_to_axis - r)
    bias_correction = var_d / (2.0 * max(r, 1e-8))
    
    res = np.zeros(len(points) + 1)
    res[:-1] = dist_to_axis - r - bias_correction
    res[-1] = 1e-4 * np.dot(c, a)
    return res

class CylinderFitter:
    def __init__(self, residual_type="symmetric"):
        self.residual_type = residual_type

    def fit(self, points: np.ndarray, initial_guess: np.ndarray):
        """
        Fits a cylinder to the points using LMA.
        initial_guess: [cx, cy, cz, theta, phi, r]
        Returns:
            params: array
            diagnostics: dict
        """
        residual_func = symmetric_bias_aware_residual if self.residual_type == "symmetric" else canonical_cylinder_residual
        
        points = np.asarray(points)
        
        result = least_squares(residual_func, initial_guess, args=(points,), method='lm')
        
        # Diagnostics
        diagnostics = {
            'status': result.status,
            'message': result.message,
            'nfev': result.nfev,
            'cost': result.cost,
            'converged': result.status > 0
        }
        
        if result.jac is not None and result.jac.size > 0:
            try:
                # Nondimensionalize Jacobian by normalizing each column to unit length
                # This treats all parameter directions equally for conditioning purposes
                col_norms = np.linalg.norm(result.jac, axis=0)
                col_norms[col_norms < 1e-12] = 1.0 # prevent div by zero
                J_scaled = result.jac / col_norms
                
                u, s, vh = svd(J_scaled, full_matrices=False)
                diagnostics['singular_values'] = s
                
                if s[-1] > 1e-12:
                    cond = s[0] / s[-1]
                else:
                    cond = np.inf
            except Exception:
                cond = np.nan
                diagnostics['singular_values'] = np.array([])
        else:
            cond = np.nan
            diagnostics['singular_values'] = np.array([])
            
        diagnostics['condition_number'] = cond
        
        result.x[5] = abs(result.x[5])
        
        return result.x, diagnostics
