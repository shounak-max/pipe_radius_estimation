import bpy
import os

class RenderPipeline:
    def __init__(self, config):
        self.config = config
        
    def render(self, output_dir):
        scene = bpy.context.scene
        
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
        
        # RGB
        file_output_rgb = tree.nodes.new('CompositorNodeOutputFile')
        file_output_rgb.directory = output_dir
        if hasattr(file_output_rgb, 'file_slots'):
            file_output_rgb.file_slots[0].path = "rgb"
        else:
            file_output_rgb.file_output_items.clear()
            file_output_rgb.file_output_items.new('RGBA', 'rgb')
        links.new(render_layers.outputs['Image'], file_output_rgb.inputs[0])
        
        # Depth
        file_output_depth = tree.nodes.new('CompositorNodeOutputFile')
        file_output_depth.directory = output_dir
        file_output_depth.format.file_format = 'OPEN_EXR_MULTILAYER'
        file_output_depth.format.color_depth = '32'
        if hasattr(file_output_depth, 'file_slots'):
            file_output_depth.file_slots[0].path = "depth"
        else:
            file_output_depth.file_output_items.clear()
            file_output_depth.file_output_items.new('FLOAT', 'depth')
        links.new(render_layers.outputs['Depth'], file_output_depth.inputs[0])
        
        # In Blender 5.1, when executing in background mode, the compositor might not evaluate 
        # file output nodes if the node group is not the active scene node tree.
        # But EEVEE/CYCLES might still fail if there's no actual output. 
        # Using CYCLES and saving explicitly via save_render as fallback.
        
        # Render Frame
        scene.frame_set(1)
        
        # Explicitly set the main render path for RGB (bypassing compositor quirks in background mode)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(output_dir, "rgb.png")
        
        # Execute render (write_still=True forces the main composite/scene to save to filepath)
        bpy.ops.render.render(write_still=True)
        
        # Pointcloud export (pure code fixture)
        # We select all visible mesh objects and export them as a .ply
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type == 'MESH' and not obj.hide_render:
                obj.select_set(True)
                
        ply_path = os.path.join(output_dir, "pointcloud.ply")
        # Export PLY
        bpy.ops.wm.ply_export(filepath=ply_path, export_selected_objects=True, ascii_format=True)

        
        # Blender's CompositorNodeOutputFile might name things inconsistently in 5.1
        # Check all possible names and rename to depth.exr
        depth_candidates = [
            os.path.join(output_dir, "depth0001.exr"),
            os.path.join(output_dir, "depth.exr"),
            os.path.join(output_dir, "file_name.exr"),
            os.path.join(output_dir, "file_name0001.exr")
        ]
        
        renamed = False
        for cand in depth_candidates:
            if os.path.exists(cand):
                if cand != os.path.join(output_dir, "depth.exr"):
                    os.rename(cand, os.path.join(output_dir, "depth.exr"))
                renamed = True
                break
                
        if not renamed:
            raise FileNotFoundError(f"CRITICAL FAILURE: Depth pass was not generated for {output_dir}")
