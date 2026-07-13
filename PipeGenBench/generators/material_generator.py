import bpy
import random

class MaterialGenerator:
    def __init__(self, config):
        self.config = config
        
    def apply_random_material(self, obj):
        mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        
        # Randomize PBR properties
        mat_type = random.choice(["steel", "pvc", "rusted"])
        if mat_type == "steel":
            bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1)
            bsdf.inputs['Metallic'].default_value = random.uniform(0.7, 1.0)
            bsdf.inputs['Roughness'].default_value = random.uniform(0.2, 0.5)
        elif mat_type == "pvc":
            bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = random.uniform(0.4, 0.7)
        elif mat_type == "rusted":
            bsdf.inputs['Base Color'].default_value = (0.3, 0.1, 0.05, 1)
            bsdf.inputs['Metallic'].default_value = random.uniform(0.0, 0.3)
            bsdf.inputs['Roughness'].default_value = random.uniform(0.7, 1.0)
            
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        return mat_type
