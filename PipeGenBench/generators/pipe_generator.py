import bpy
import random
import math

class PipeGenerator:
    def __init__(self, config):
        self.config = config
        self.pipes = []
        
    def generate_straight_pipe(self, name="Pipe"):
        radius_min = self.config['pipes']['radius']['min']
        radius_max = self.config['pipes']['radius']['max']
        length_min = self.config['pipes']['length']['min']
        length_max = self.config['pipes']['length']['max']
        
        r = random.uniform(radius_min, radius_max)
        l = random.uniform(length_min, length_max)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r, 
            depth=l, 
            location=(0, 0, 0)
        )
        pipe = bpy.context.active_object
        pipe.name = name
        
        # Default orientation along Z
        axis = [0.0, 0.0, 1.0]
        
        pipe_data = {
            "name": pipe.name,
            "type": "straight",
            "radius": r,
            "length": l,
            "axis": axis,
            "center": list(pipe.location)
        }
        self.pipes.append(pipe_data)
        return pipe, pipe_data
