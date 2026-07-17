import bpy
import numpy as np
import json
import math
import os

def create_blender_dataset(output_dir="C:/tmp/blender_pipe_dataset"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Clear the scene
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type in ['MESH', 'CAMERA', 'LIGHT']:
            obj.select_set(True)
    bpy.ops.object.delete()

    # 2. Build the Complex Topology Scene (Testing G2: Topology & G4: Edge Fusion under occlusion)
    true_radius = 0.1  # 100mm
    
    # Pipe 1: Main trunk (X-axis)
    bpy.ops.mesh.primitive_cylinder_add(radius=true_radius, depth=2.0, location=(0, 0, 0))
    p1 = bpy.context.active_object
    p1.name = "Pipe_Main"
    p1.rotation_euler = (0, math.radians(90), 0)
    
    # Pipe 2: T-Junction Branch (Y-axis)
    bpy.ops.mesh.primitive_cylinder_add(radius=true_radius, depth=1.0, location=(0, 0.5, 0))
    p2 = bpy.context.active_object
    p2.name = "Pipe_Branch_Y"
    p2.rotation_euler = (math.radians(90), 0, 0)
    
    # Pipe 3: Elbow connection (Z-axis offset)
    bpy.ops.mesh.primitive_cylinder_add(radius=true_radius, depth=1.0, location=(1.0, 0, 0.5))
    p3 = bpy.context.active_object
    p3.name = "Pipe_Elbow_Z"
    # Vertical (Z) by default

    # 3. Add Heavy Occluder (Testing G4: Visibility < 15%)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.2, -0.8, 0.2))
    occluder = bpy.context.active_object
    occluder.name = "Occluder_Box"
    # Scale to block most of the T-Junction
    occluder.scale = (1.5, 0.1, 1.5)

    # 4. Add Lighting
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
    sun = bpy.context.active_object
    sun.data.energy = 5.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))

    # 5. Add Camera
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    # Position camera looking at the occluded T-junction
    cam_obj.location = (0, -2.5, 0)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    
    # 6. Configure Render Settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    # 7. Setup Compositor for Depth and RGB output
    scene.view_layers["ViewLayer"].use_pass_z = True
    if hasattr(scene, 'compositing_node_group'):
        scene.compositing_node_group = bpy.data.node_groups.new('Compositor', 'CompositorNodeTree')
        tree = scene.compositing_node_group
        scene.use_nodes = True
    else:
        scene.use_nodes = True
        tree = scene.node_tree
    
    links = tree.links
    
    # Clear existing nodes
    for n in tree.nodes:
        tree.nodes.remove(n)
        
    render_layers = tree.nodes.new('CompositorNodeRLayers')
    
    # Explicitly set main render path for RGB (bypassing compositor quirks)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(output_dir, "rgb.png")
    
    # Depth Output Node
    file_output_depth = tree.nodes.new('CompositorNodeOutputFile')
    if hasattr(file_output_depth, 'directory'):
        file_output_depth.directory = output_dir
        file_output_depth.file_name = "depth"
    else:
        file_output_depth.base_path = output_dir

    if hasattr(file_output_depth, 'file_output_items'):
        file_output_depth.file_output_items.clear()
        file_output_depth.file_output_items.new('FLOAT', 'depth')
    else:
        file_output_depth.file_slots[0].path = "depth_"

    file_output_depth.format.file_format = 'OPEN_EXR_MULTILAYER'
    file_output_depth.format.color_depth = '32'
    
    if 'depth' in file_output_depth.inputs:
        links.new(render_layers.outputs['Depth'], file_output_depth.inputs['depth'])
    else:
        links.new(render_layers.outputs['Depth'], file_output_depth.inputs[0])
    
    # 8. Render Frame
    scene.frame_set(1)
    bpy.ops.render.render(write_still=True)

    # 8.5 Rename depth map to standard name (Blender 5.1 workaround)
    depth_candidates = [
        os.path.join(output_dir, "depth0001.exr"),
        os.path.join(output_dir, "depth_0001.exr"),
        os.path.join(output_dir, "depth.exr"),
        os.path.join(output_dir, "file_name.exr"),
        os.path.join(output_dir, "file_name0001.exr")
    ]
    renamed = False
    for cand in depth_candidates:
        if os.path.exists(cand):
            target_path = os.path.join(output_dir, "depth.exr")
            if cand != target_path:
                if os.path.exists(target_path):
                    os.remove(target_path)
                os.rename(cand, target_path)
            renamed = True
            break
            
    if not renamed:
        print("WARNING: Depth pass was not generated!")

    # 9. Compute and Export Camera Calibration
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
    
    # Export Manifest mapping the complex topology
    manifest = {
        "scan_id": "blender_topology_001",
        "scene_id": "synthetic_t_junction_occluded",
        "site_id": "blender_sim",
        "sensor_id": "blender_cycles",
        "operator_id": "sim",
        "timestamp": "2026-07-14T00:00:00Z",
        "pcd_path": "", 
        "rgb_path": "rgb_0001.png",
        "depth_path": "depth_0001.exr",
        "standoff_range_m": 2.5,
        "incidence_angle_deg": 0.0,
        "measured_visible_circumference_pct": 15.0,
        "ambient_temperature_c": 20.0,
        "lighting_condition": "synthetic_sun",
        "pipe_inventory": ["Pipe_Main", "Pipe_Branch_Y", "Pipe_Elbow_Z"],
        "alignment_type": "hardware_sdk"
    }
    
    calibration = {
        "intrinsics": intrinsics,
        "extrinsics": extrinsics,
        "image_width": res_x,
        "image_height": res_y
    }
    
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)
        
    with open(os.path.join(output_dir, "calibration.json"), "w") as f:
        json.dump(calibration, f, indent=4)
        
    print(f"Dataset generated at: {output_dir}")

if __name__ == "__main__":
    create_blender_dataset()
