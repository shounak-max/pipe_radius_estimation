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

from utils.config import load_config
from generators.pipe_generator import PipeGenerator
from generators.scene_generator import SceneGenerator
from generators.camera_generator import CameraGenerator

def main():
    config_path = os.path.join(os.path.dirname(__file__), "config", "default_config.yaml")
    
    try:
        config = load_config(config_path)
    except ImportError:
        print("PyYAML not found in Blender's python. Trying to install...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        from utils.config import load_config
        config = load_config(config_path)

    output_dir = os.path.join(os.path.dirname(__file__), "output", "Scene_00001")
    os.makedirs(output_dir, exist_ok=True)
    
    pipe_gen = PipeGenerator(config)
    scene_gen = SceneGenerator(config, pipe_gen)
    cam_gen = CameraGenerator(config)
    
    print("Generating Scene...")
    pipes_data = scene_gen.generate_scene()
    
    print("Generating Camera...")
    cam_obj, cam_data = cam_gen.setup_camera()
    calibration = cam_gen.extract_calibration(cam_obj, cam_data, bpy.context.scene)
    
    # Save the file (Test Run)
    blend_file = os.path.join(output_dir, "scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"Saved blend file to {blend_file}")
    
    # Save calibration
    with open(os.path.join(output_dir, "calibration.json"), "w") as f:
        json.dump(calibration, f, indent=4)
        
    print("Milestone 1 Verification Complete.")

if __name__ == "__main__":
    main()
