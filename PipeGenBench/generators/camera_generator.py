import bpy
import math

class CameraGenerator:
    def __init__(self, config):
        self.config = config
        
    def setup_camera(self):
        cam_data = bpy.data.cameras.new("Camera")
        cam_obj = bpy.data.objects.new("Camera", cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj
        
        # Position camera looking at scene
        cam_obj.location = (0, -2.5, 0)
        cam_obj.rotation_euler = (math.radians(90), 0, 0)
        
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 4 # Fast testing
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 100
        
        return cam_obj, cam_data
        
    def extract_calibration(self, cam_obj, cam_data, scene):
        res_x = scene.render.resolution_x
        res_y = scene.render.resolution_y
        sensor_width_in_mm = cam_data.sensor_width
        focal_length_in_mm = cam_data.lens
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        
        s_u = res_x / sensor_width_in_mm
        s_v = res_y * pixel_aspect_ratio / (sensor_width_in_mm / (res_x / res_y))
        
        fx = focal_length_in_mm * s_u
        fy = focal_length_in_mm * s_v
        cx = res_x / 2.0
        cy = res_y / 2.0
        
        intrinsics = [
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]
        ]
        
        extrinsics = [list(row) for row in cam_obj.matrix_world]
        
        return {
            "intrinsics": intrinsics,
            "extrinsics": extrinsics,
            "image_width": res_x,
            "image_height": res_y
        }
