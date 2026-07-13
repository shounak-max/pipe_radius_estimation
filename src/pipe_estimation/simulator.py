import numpy as np

def simulate_sensor_noise(points, sensor_type="lidar", sensor_origin=(0,0,0)):
    """
    Applies noise characteristics based on sensor type along the depth ray.
    """
    if sensor_type == "lidar":
        std = 2.0
    elif sensor_type == "kinect_v1":
        std = 15.0
    elif sensor_type == "kinect_v2":
        std = 5.0
    else:
        std = 0.0
        
    return add_depth_noise(points, sensor_origin, std)

def add_depth_noise(points, sensor_origin, std):
    if std <= 0:
        return points
        
    origin = np.array(sensor_origin)
    rays = points - origin
    
    # Normalize rays
    norms = np.linalg.norm(rays, axis=1, keepdims=True)
    # Avoid division by zero
    norms[norms == 0] = 1e-8
    ray_dirs = rays / norms
    
    # Generate Gaussian noise along the ray
    noise_mags = np.random.normal(0, std, (points.shape[0], 1))
    
    return points + ray_dirs * noise_mags

def generate_synthetic_pipe(radius, length, num_points, noise_std=0.0, visible_fraction=1.0, origin=(0,0,0), axis=(0,0,1), sensor_origin=None):
    """
    Generates a synthetic point cloud for a pipe aligned with a specific axis.
    """
    theta = np.random.uniform(0, 2 * np.pi * visible_fraction, num_points)
    l = np.random.uniform(0, length, num_points)
    
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = l
    
    points = np.column_stack((x, y, z))
    
    axis = np.array(axis) / np.linalg.norm(axis)
    z_axis = np.array([0, 0, 1])
    
    if not np.allclose(axis, z_axis):
        v = np.cross(z_axis, axis)
        c = np.dot(z_axis, axis)
        s = np.linalg.norm(v)
        if s != 0:
            kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
            rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
            points = points.dot(rotation_matrix.T)
    
    points += np.array(origin)
    
    if noise_std > 0:
        if sensor_origin is None:
            # Default to some offset so rays make sense
            sensor_origin = (origin[0] + radius*3, origin[1], origin[2] + length/2)
        points = add_depth_noise(points, sensor_origin, noise_std)
        
    return points

def generate_plant_scale_scene(sensor_type="lidar", occlusion_level="none"):
    """
    Generates a multi-segment pipe network with elbows and occlusion.
    """
    scene_points = []
    ground_truth = []
    
    sensor_origin = (150, 150, 300)
    
    if occlusion_level == "light":
        vis = 0.50
    elif occlusion_level == "moderate":
        vis = 0.30
    elif occlusion_level == "heavy":
        vis = 0.15
    else:
        vis = 1.0

    p1 = generate_synthetic_pipe(50, 300, 2000, visible_fraction=vis, origin=(0,0,0), axis=(1,0,0), noise_std=0)
    ground_truth.append({"id": "pipe_1", "radius": 50, "axis": (1,0,0), "center": (150,0,0)})
    
    p2 = generate_synthetic_pipe(100, 400, 3000, visible_fraction=vis, origin=(300,50,0), axis=(0,1,0), noise_std=0)
    ground_truth.append({"id": "pipe_2", "radius": 100, "axis": (0,1,0), "center": (300,250,0)})
    
    scene_points.append(p1)
    scene_points.append(p2)
    
    combined_cloud = np.vstack(scene_points)
    combined_cloud = simulate_sensor_noise(combined_cloud, sensor_type, sensor_origin)
    
    return combined_cloud, ground_truth
