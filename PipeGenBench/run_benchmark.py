import sys
import os
import json

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import bpy
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False
    
if not IN_BLENDER:
    print("This script must be run from within Blender:")
    print("blender -b -P run_benchmark.py")
    sys.exit(1)

import site
try:
    import yaml
except ImportError:
    print("PyYAML not found in Blender's python. Trying to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "--user"])
    sys.path.append(site.getusersitepackages())
    import yaml

from utils.config import load_config
from generators.pipe_generator import PipeGenerator
from generators.scene_generator import SceneGenerator
from generators.camera_generator import CameraGenerator
from generators.light_generator import LightGenerator
from generators.material_generator import MaterialGenerator
from generators.occluder_generator import OccluderGenerator
from annotations.annotation_generator import AnnotationGenerator
from annotations.topology_generator import TopologyGenerator
from exporters.render_pipeline import RenderPipeline
from utils.sensor_simulator import SensorSimulator

def main():
    config_path = os.path.join(os.path.dirname(__file__), "config", "default_config.yaml")
    config = load_config(config_path)

        
    num_scenes = config.get('dataset', {}).get('num_scenes', 1)
    
    pipe_gen = PipeGenerator(config)
    scene_gen = SceneGenerator(config, pipe_gen)
    cam_gen = CameraGenerator(config)
    light_gen = LightGenerator(config)
    mat_gen = MaterialGenerator(config)
    occ_gen = OccluderGenerator(config)
    anno_gen = AnnotationGenerator(config)
    topo_gen = TopologyGenerator(config)
    render_pipe = RenderPipeline(config)
    sensor_sim = SensorSimulator(config)
    
    # Dataset Split tracking
    train_count = int(num_scenes * 0.8)
    val_count = int(num_scenes * 0.1)
    
    for i in range(num_scenes):
        scene_id = f"Scene_{i+1:05d}"
        
        # Dataset Split logic
        if i < train_count:
            split_dir = "train"
        elif i < train_count + val_count:
            split_dir = "val"
        else:
            split_dir = "test"
            
        output_dir = os.path.join(os.path.dirname(__file__), "output", split_dir, scene_id)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating {scene_id} in {split_dir}...")
        
        pipes_data = scene_gen.generate_scene()
        
        # Apply Materials
        for obj in bpy.context.scene.objects:
            if obj.name.startswith("Pipe"):
                mat_gen.apply_random_material(obj)
                
        # Lighting
        light_gen.generate_lighting()
        
        # Occluders
        occ_gen.generate_occluders()
        
        # Camera
        cam_obj, cam_data = cam_gen.setup_camera()
        calibration = cam_gen.extract_calibration(cam_obj, cam_data, bpy.context.scene)
        
        # Render
        render_pipe.render(output_dir)
        
        # Sensor Simulation
        sensor_sim.apply_noise(os.path.join(output_dir, "depth.exr"))
        
        # Annotations
        anno_gen.generate_metadata(scene_id, pipes_data, calibration, output_dir)
        topo_gen.generate_topology(pipes_data, output_dir)
        
        # Save .blend for inspection
        blend_file = os.path.join(output_dir, "scene.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)
        print(f"Completed {scene_id}")
        
    print("\nDataset Generation Complete.")
    
    # Dataset Statistics
    stats = {
        "total_scenes": num_scenes,
        "splits": {
            "train": train_count,
            "val": val_count,
            "test": num_scenes - train_count - val_count
        }
    }
    with open(os.path.join(os.path.dirname(__file__), "output", "dataset_statistics.json"), "w") as f:
        json.dump(stats, f, indent=4)

if __name__ == "__main__":
    main()
