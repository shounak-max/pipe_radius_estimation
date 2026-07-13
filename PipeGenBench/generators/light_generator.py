import bpy
import random
import math

class LightGenerator:
    def __init__(self, config):
        self.config = config
        
    def generate_lighting(self):
        # Add basic randomized sun
        bpy.ops.object.light_add(type='SUN', location=(random.uniform(-10, 10), random.uniform(-10, 10), 10))
        sun = bpy.context.active_object
        sun.data.energy = random.uniform(2.0, 10.0)
        sun.rotation_euler = (math.radians(random.uniform(30, 60)), random.uniform(-1, 1), random.uniform(-1, 1))
        
        # Add a couple of point lights
        for i in range(random.randint(1, 3)):
            bpy.ops.object.light_add(type='POINT', location=(random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(2, 5)))
            pt = bpy.context.active_object
            pt.data.energy = random.uniform(100.0, 500.0)
            pt.data.color = (random.uniform(0.8, 1.0), random.uniform(0.8, 1.0), random.uniform(0.8, 1.0))
