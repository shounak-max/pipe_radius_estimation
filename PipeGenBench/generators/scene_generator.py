import bpy
import random
import math

class SceneGenerator:
    def __init__(self, config, pipe_generator):
        self.config = config
        self.pipe_gen = pipe_generator
        
    def clear_scene(self):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type in ['MESH', 'CAMERA', 'LIGHT']:
                obj.select_set(True)
        bpy.ops.object.delete()
        
    def generate_scene(self):
        self.clear_scene()
        
        # Basic: generate a couple of connected pipes
        p1, d1 = self.pipe_gen.generate_straight_pipe("Pipe_Main")
        p1.rotation_euler = (0, math.radians(90), 0) # align to X
        d1['axis'] = [1.0, 0.0, 0.0]
        
        p2, d2 = self.pipe_gen.generate_straight_pipe("Pipe_Branch")
        p2.rotation_euler = (math.radians(90), 0, 0) # align to Y
        p2.location = (0, d2['length']/2.0, 0)
        d2['axis'] = [0.0, 1.0, 0.0]
        d2['center'] = list(p2.location)
        
        # Add occluder if enabled
        if self.config['occlusion']['enabled']:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.2, -0.8, 0.2))
            occ = bpy.context.active_object
            occ.name = "Occluder"
            occ.scale = (1.5, 0.1, 1.5)
            
        # Add lighting
        bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
        sun = bpy.context.active_object
        sun.data.energy = random.uniform(2.0, 8.0)
        sun.rotation_euler = (math.radians(45), 0, math.radians(45))
        
        return self.pipe_gen.pipes
