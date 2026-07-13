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

def variance_corrected_residual(params, points, fixed_variance=None):
    """
    Rice/magnitude-bias-style variance correction.
    Fits log_r instead of r to prevent negative/zero radius.
    Requires a fixed_variance passed in to avoid self-referential instability.
    params: [cx, cy, cz, theta, phi, log_r]
    """
    c = params[0:3]
    a = get_axis_from_angles(params[3], params[4])
    r = np.exp(params[5])
    
    v = points - c
    dist = np.linalg.norm(np.cross(v, a), axis=1)
    residuals = dist - r
    
    if fixed_variance is None:
        # Fallback if not provided, but ideally should be avoided
        var = np.var(residuals)
    else:
        var = fixed_variance
        
    correction = var / (2 * r)
    
    res = np.zeros(len(points) + 1)
    res[:-1] = residuals - correction
    res[-1] = 1e-4 * np.dot(c, a)
    return res

def true_ru_epd_residual(params, points, sensor_origin):
    """
    The actual RU-EPD residual (C-EPD ray-intersection distance).
    Computes where each measurement ray intersects the cylinder, and takes the distance
    difference along that specific ray.
    
    NOTE ON UNBIASEDNESS: The paper's unbiasedness proof (Theorem 2) and real-world 
    validation strictly depend on an elliptical cross-section (D_max, D_min) where 
    major and minor axis errors cancel each other out. This circular adaptation 
    (single radius r) lacks that cancellation mechanism, and thus is expected to 
    behave differently (often underperforming canonical on pure circular data).
    It should NOT be cited as validating the paper's claim without an elliptical extension.
    """
    c = params[0:3]
    a = get_axis_from_angles(params[3], params[4])
    r = params[5]
    
    o = np.array(sensor_origin)
    rays = points - o
    norms = np.linalg.norm(rays, axis=1, keepdims=True)
    v_ray = rays / norms
    
    dp = o - c
    cross_v_a = np.cross(v_ray, a)
    cross_dp_a = np.cross(dp, a) # shape (3,)
    
    a_quad = np.sum(cross_v_a**2, axis=1)
    b_quad = 2 * np.sum(cross_v_a * cross_dp_a, axis=1)
    c_quad = np.sum(cross_dp_a**2) - r**2
    
    discriminant = b_quad**2 - 4 * a_quad * c_quad
    
    # For points where the ray doesn't intersect, fallback to geometric distance
    valid = discriminant >= 0
    
    t_meas = np.linalg.norm(rays, axis=1)
    t_true = np.zeros_like(t_meas)
    
    if np.any(valid):
        sqrt_disc = np.sqrt(discriminant[valid])
        # Two roots, we want the one closest to the measurement
        t1 = (-b_quad[valid] + sqrt_disc) / (2 * a_quad[valid])
        t2 = (-b_quad[valid] - sqrt_disc) / (2 * a_quad[valid])
        
        dist1 = np.abs(t1 - t_meas[valid])
        dist2 = np.abs(t2 - t_meas[valid])
        
        t_true[valid] = np.where(dist1 < dist2, t1, t2)
    
    res = np.zeros_like(t_meas)
    res[valid] = t_meas[valid] - t_true[valid]
    
    # Fallback to standard distance if ray doesn't intersect (e.g. initial guess is bad)
    if not np.all(valid):
        v = points[~valid] - c
        dist = np.linalg.norm(np.cross(v, a), axis=1)
        res[~valid] = dist - r

    # Regularizer to break the true axis-translation gauge freedom
    res = np.append(res, 1e-4 * np.dot(c, a))
    return res

class CylinderFitter:
    def __init__(self, residual_type="variance_corrected"):
        self.residual_type = residual_type

    def fit(self, points, initial_guess, sensor_origin=None):
        """
        Fits a cylinder to the points using LMA.
        initial_guess: [cx, cy, cz, theta, phi, r]
        Returns:
            params: array
            diagnostics: dict
        """
        points = np.asarray(points)
        
        if self.residual_type == "variance_corrected":
            # 1. Estimate variance from an initial canonical fit
            res_canon = least_squares(canonical_cylinder_residual, initial_guess, args=(points,), method='lm')
            residuals = canonical_cylinder_residual(res_canon.x, points)[:-1]
            fixed_variance = np.var(residuals)
            
            # 2. Reparameterize r -> log_r for the initial guess
            init_var = np.copy(res_canon.x)
            if init_var[5] <= 0:
                init_var[5] = 1e-6
            init_var[5] = np.log(init_var[5])
            
            residual_func = variance_corrected_residual
            args = (points, fixed_variance)
            result = least_squares(residual_func, init_var, args=args, method='lm')
            
            # Convert back log_r -> r
            result.x[5] = np.exp(result.x[5])
            
        elif self.residual_type == "ru_epd":
            residual_func = true_ru_epd_residual
            if sensor_origin is None:
                raise ValueError("sensor_origin must be provided for true_ru_epd residual")
            args = (points, sensor_origin)
            result = least_squares(residual_func, initial_guess, args=args, method='lm')
        else:
            residual_func = canonical_cylinder_residual
            args = (points,)
            result = least_squares(residual_func, initial_guess, args=args, method='lm')
        
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
