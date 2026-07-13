import numpy as np
from scipy.optimize import least_squares

def test_bias():
    true_radius = 50.0
    length = 200.0
    num_points = 1000
    noise = 5.0
    sensor_origin = np.array([300, 0, length/2])
    
    # Generate points
    theta = np.random.uniform(0, 2 * np.pi, num_points)
    l = np.random.uniform(0, length, num_points)
    x = true_radius * np.cos(theta)
    y = true_radius * np.sin(theta)
    z = l
    points = np.column_stack((x, y, z))
    
    rays = points - sensor_origin
    norms = np.linalg.norm(rays, axis=1, keepdims=True)
    ray_dirs = rays / norms
    noise_mags = np.random.normal(0, noise, (num_points, 1))
    points += ray_dirs * noise_mags
    
    c = np.array([0, 0, 0])
    a = np.array([0, 0, 1])
    
    def get_axis(theta, phi):
        return np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])

    def res_canon(params):
        c = params[0:3]
        a = get_axis(params[3], params[4])
        r = params[5]
        v = points - c
        d = np.linalg.norm(np.cross(v, a), axis=1)
        res = np.zeros(num_points + 1)
        res[:-1] = d - r
        res[-1] = 1e-4 * np.dot(c, a)
        return res
        
    def res_sym1(params):
        c = params[0:3]
        a = get_axis(params[3], params[4])
        r = params[5]
        v = points - c
        d = np.linalg.norm(np.cross(v, a), axis=1)
        res = np.zeros(num_points + 1)
        res[:-1] = (d**2 - r**2) / (2.0 * r)
        res[-1] = 1e-4 * np.dot(c, a)
        return res
        
    def res_sym_unbiased(params):
        c = params[0:3]
        a = get_axis(params[3], params[4])
        r = params[5]
        v = points - c
        d = np.linalg.norm(np.cross(v, a), axis=1)
        
        var_d = np.var(d - r)
        bias_correction = var_d / (2.0 * max(r, 1e-8))
        
        res = np.zeros(num_points + 1)
        res[:-1] = d - r - bias_correction
        res[-1] = 1e-4 * np.dot(c, a)
        return res

    initial = [0.0, 0.0, 0.0, 0.0, 0.0, 48.0]
    for name, func in [("Canon", res_canon), ("Sym_Unbiased", res_sym_unbiased)]:
        res = least_squares(func, initial, method='lm')
        print(f"{name}: r={res.x[5]:.3f}, bias={res.x[5]-true_radius:+.3f}")

if __name__ == "__main__":
    test_bias()
