import bpy
import random

class OccluderGenerator:
    def __init__(self, config):
        self.config = config
        
    def generate_occluders(self):
        if not self.config.get('occlusion', {}).get('enabled', False):
            return []
            
        occluders = []
        for i in range(random.randint(1, 3)):
            bpy.ops.mesh.primitive_cube_add(
                size=random.uniform(0.5, 2.0), 
                location=(random.uniform(-1, 1), random.uniform(-2, 0), random.uniform(0, 2))
            )
            occ = bpy.context.active_object
            occ.name = f"Occluder_{i}"
            occ.scale = (random.uniform(0.2, 1.5), random.uniform(0.1, 0.5), random.uniform(0.2, 1.5))
            occluders.append(occ.name)
            
        return occluders
