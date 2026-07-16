import bpy
import os

class RenderPipeline:
    def __init__(self, config):
        self.config = config
        
    def render(self, output_dir):
        # Clear/overwrite output directory to prevent stale files from accumulating
        if os.path.exists(output_dir):
            for f in os.listdir(output_dir):
                if f.endswith('.exr') or f.endswith('.png') or f.endswith('.ply'):
                    try:
                        os.remove(os.path.join(output_dir, f))
                    except OSError:
                        pass

        scene = bpy.context.scene
        
        # Force CYCLES for guaranteed geometric depth pass in headless mode
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 32
        
        # Ensure nodes are setup and Z pass is enabled
        scene.view_layers["ViewLayer"].use_pass_z = True
        
        # Support Blender 5.x Compositor API
        if hasattr(scene, 'compositing_node_group'):
            scene.compositing_node_group = bpy.data.node_groups.new('Compositor', 'CompositorNodeTree')
            tree = scene.compositing_node_group
            scene.use_nodes = True # Ensure compositor runs
        else:
            scene.use_nodes = True
            tree = scene.node_tree
            
        links = tree.links
        
        for n in tree.nodes:
            tree.nodes.remove(n)
            
        render_layers = tree.nodes.new('CompositorNodeRLayers')
        
        # Depth via Output File Node
        depth_output = tree.nodes.new('CompositorNodeOutputFile')
        
        if hasattr(depth_output, 'directory'):
            # Blender 5.1+ API
            depth_output.directory = output_dir
            depth_output.file_name = "depth"
        else:
            # Blender < 5.0 API
            depth_output.base_path = output_dir

        if hasattr(depth_output, 'file_output_items'):
            depth_output.file_output_items.clear()
            depth_output.file_output_items.new('FLOAT', 'depth')
        else:
            depth_output.file_slots[0].path = "depth_"

        depth_output.format.file_format = 'OPEN_EXR_MULTILAYER'
        depth_output.format.color_depth = '32'
        
        # Explicitly link to the newly created 'depth' socket
        if 'depth' in depth_output.inputs:
            links.new(render_layers.outputs['Depth'], depth_output.inputs['depth'])
        else:
            links.new(render_layers.outputs['Depth'], depth_output.inputs[0])
        
        # Render Frame
        scene.frame_set(1)
        
        # Explicitly set the main render path for RGB (bypassing compositor quirks in background mode)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(output_dir, "rgb.png")
        
        # Execute render (write_still=True forces the main composite/scene to save to filepath)
        bpy.ops.render.render(write_still=True)
        
        # Blender's CompositorNodeOutputFile might name things inconsistently in 5.1
        # Check all possible names and rename to depth.exr
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
                if cand != os.path.join(output_dir, "depth.exr"):
                    if os.path.exists(os.path.join(output_dir, "depth.exr")):
                        os.remove(os.path.join(output_dir, "depth.exr"))
                    os.rename(cand, os.path.join(output_dir, "depth.exr"))
                renamed = True
                break
                
        if not renamed:
            raise FileNotFoundError(f"CRITICAL FAILURE: Depth pass was not generated for {output_dir}")

        # Pointcloud export (pure code fixture)
        # We select all visible mesh objects and export them as a .ply
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type == 'MESH' and not obj.hide_render:
                obj.select_set(True)
                
        ply_path = os.path.join(output_dir, "pointcloud.ply")
        # Export PLY
        bpy.ops.wm.ply_export(filepath=ply_path, export_selected_objects=True, ascii_format=True)
